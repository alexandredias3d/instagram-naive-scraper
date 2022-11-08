import itertools
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Playwright, TimeoutError as PlaywrightTimeoutError  # type: ignore
from typing import Iterable

from config import Config
from logger import logger
from content import ContentType, Content
from posts import PostStatus
from user import User
from utils import create_folder, InsertionOrderSet


class InstagramScraper:
    def __init__(self, user: User, config: Config) -> None:
        self.user = user
        self.config = config

    def run(self) -> None:
        with sync_playwright() as playwright:
            self.__run(playwright)

    def __run(self, playwright: Playwright) -> None:
        logger().info(f'started scrapping {self.user}')

        browser = playwright.firefox.launch(headless=self.config.headless, slow_mo=self.config.action_delay)

        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0')
        self.__log_in(page)
        posts = self.__get_posts_links(page)
        self.user.posts.add_posts(posts, PostStatus.AVAILABLE)
        self.user.save()
        self.__scrape_user_posts(page)

        logger().info(f'finished scrapping {self.user}')

    def __goto(self, page: Page, url: str) -> None:
        success = False
        attempt = 1
        while not success and attempt <= self.config.max_retries:
            try:
                page.goto(url)
                logger().info(f'success while going to {url} (attempt: {attempt}/{self.config.max_retries})')
                success = True
            except Exception as exception:
                logger().error(f'error while going to {url} (attempt: {attempt}/{self.config.max_retries})')
                logger().error(exception)
                self.__sleep(self.config.loading_delay)
            attempt += 1
        self.__sleep(self.config.loading_delay)

    def __sleep(self, duration: int) -> None:
        logger().debug(f'waiting {duration} seconds')
        time.sleep(duration)

    def __log_in(self, page: Page) -> None:
        self.__goto(page, self.user.base_url)

        forms = page.locator('input')
        forms.nth(0).fill(self.config.username)
        forms.nth(1).fill(self.config.password)

        log_in_button = page.locator('text="Log in"')
        log_in_button.click()

        self.__sleep(self.config.loading_delay)

    def __get_posts_links(self, page: Page) -> InsertionOrderSet[str]:
        self.__goto(page, self.user.profile_url)
        posts_links = InsertionOrderSet[str]()

        previous_amount_of_links = 0
        iterations_without_new_links = 0
        while True:
            page.keyboard.press('End')

            links = page.locator('article').locator('a[href^="/p/"]')
            posts_links.add_multiple([f'{self.user.base_url}{link}' for i in range(links.count()) if (link := links.nth(i).get_attribute('href'))])

            if posts_links.contains_any(self.user.posts.available):
                break

            current_amount_of_links = len(posts_links)
            if current_amount_of_links == previous_amount_of_links:
                iterations_without_new_links += 1
                self.__sleep(self.config.scrolling_delay)
            else:
                iterations_without_new_links = 0

            previous_amount_of_links = current_amount_of_links

            if iterations_without_new_links == 5:
                break

            self.__sleep(self.config.scrolling_delay)

        return posts_links

    def __scrape_user_posts(self, page: Page) -> None:
        for post in self.user.posts.get_posts_to_download():
            attempt = 1
            success = False
            while not success and attempt <= self.config.max_retries:
                self.__goto(page, post)
                attempt_message = f'(attempt: {attempt}/{self.config.max_retries})'
                try:
                    self.__scrape_post(page, post)
                    logger().info(f'success scraping {post} from user {self.user.profile} {attempt_message}')
                    success = True
                except Exception as exception:
                    logger().error(f'failed scraping {post} from user {self.user.profile} {attempt_message}')
                    logger().error(f'{exception}')
                finally:
                    self.__sleep(self.config.scraping_delay)
                attempt += 1

            if success:
                self.user.posts.add_posts(post, PostStatus.DOWNLOADED)

            self.user.save()

    def __scrape_post(self, page: Page, post: str) -> None:
        date = self.__get_post_date(page)

        folder = f'{self.user.profile}/{date.strftime("%Y%m%d-%H_%M")}'
        create_folder(folder)

        url = Content(post, ContentType.URL, post)
        caption = self.__get_post_caption(page, post)
        media = self.__get_media_links(page)

        for index, content in enumerate(itertools.chain([url, caption], media)):
            content.save(f'{folder}/{index:02d}-{content.type.value}')

        logger().debug(f'date: {date}, media: {len(media)}')

    def __get_post_date(self, page: Page) -> datetime:
        date_string = page.locator('article >> time').nth(0).get_attribute('datetime')
        date_string = date_string if date_string else ''
        date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        return date

    def __get_post_caption(self, page: Page, post: str) -> Content:
        caption = ''
        try:
            spans = page.locator('article >> ul >> span')

            index = 1
            if spans.nth(0) == '':
                index = 2

            caption = page.locator('article >> ul >> span').nth(index).inner_html()
        except PlaywrightTimeoutError:
            logger().info(f'timeout while getting caption from {post}')

        caption = re.sub(r'<br>', '\n', caption)
        caption = re.sub(r'<a.*>(.*)</a>', r'\1', caption)

        return Content(post, ContentType.TEXT, caption)

    def __get_media_links(self, page: Page) -> InsertionOrderSet[Content]:
        contents = InsertionOrderSet[Content]()

        self.__has_clicked_on_next_button(page)

        has_media_left = True
        while has_media_left:
            contents.add_multiple(self.__get_media_contents(page))
            has_media_left = self.__has_clicked_on_next_button(page)

        contents.add_multiple(self.__get_media_contents(page))

        return contents

    def __get_media_contents(self, page: Page) -> Iterable[Content]:
        contents = InsertionOrderSet[Content]()
        try:
            media = page.locator('article >> img, video')
            for i in range(media.count()):
                element = media.nth(i)
                link = element.get_attribute('src')
                tag = element.element_handle().get_property('tagName').json_value()
                alternate_text = element.get_attribute('alt')

                if not link or (alternate_text and 'profile' in alternate_text):
                    continue

                media_type = ContentType.DEFAULT
                match tag.upper():
                    case 'IMG':
                        media_type = ContentType.IMAGE
                    case 'VIDEO':
                        media_type = ContentType.VIDEO
                contents.add(Content(link, media_type))
        except PlaywrightTimeoutError:
            pass

        return contents

    def __has_clicked_on_next_button(self, page: Page) -> bool:
        next_button = page.locator('button[aria-label="Next"]')
        if next_button.is_visible():
            next_button.click()
            return True
        else:
            return False
