from config import Config
from scraper import InstagramScraper
from logger import configure_logger, logger
from user import User
from utils import create_profile_folder, get_profile_name, get_base_url, get_config_file


if __name__ == '__main__':
    create_profile_folder()
    configure_logger()

    logger().info('starting instagram-naive-scraper')

    user = User(get_base_url(), get_profile_name()).read()
    config = Config(get_config_file()).read()
    InstagramScraper(user, config).run()

    logger().info('ending instagram-naive-scraper')
