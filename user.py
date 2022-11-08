import json

from logger import logger
from posts import Posts, PostStatus
from utils import create_folder


class User:
    def __init__(self, base_url: str, profile: str) -> None:
        self.posts: Posts = Posts(base_url)
        self.profile: str = profile
        self.folder: str = f'{self.profile}'
        self.filepath: str = f'{self.folder}/{self.profile}-profile.json'
        self.base_url: str = base_url
        self.profile_url: str = f'{self.base_url}/{self.profile}'

        create_folder(self.folder)

    def __str__(self) -> str:
        return f'User({self.profile})'

    def save(self) -> 'User':
        total = len(self.posts.available)
        total_downloaded = len(self.posts.downloaded)
        progress = round((total_downloaded / total) * 100, 2)

        data = {
            'profile': self.profile,
            'total': total,
            'total_downloaded': total_downloaded,
            'progress': progress,
            'available_posts': list(self.posts.available),
            'downloaded_posts': list(self.posts.downloaded),
        }

        logger().info(f'saved {self.profile} with progress {progress:.2f}% ({total_downloaded}/{total})')

        with open(self.filepath, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2)

        return self

    def read(self) -> 'User':
        try:
            with open(self.filepath, 'r', encoding='utf-8') as json_file:
                profile = json.load(json_file)
                self.posts.add_posts(profile['available_posts'], PostStatus.AVAILABLE)
                self.posts.add_posts(profile['downloaded_posts'], PostStatus.DOWNLOADED)
                logger().info(f'read {len(self.posts.available)} links from {self.filepath}')
        except FileNotFoundError:
            logger().info(f'no posts to read from {self.filepath}')
        except json.JSONDecodeError:
            logger().error(f'failed while decoding {self.filepath} as a JSON file')

        return self
