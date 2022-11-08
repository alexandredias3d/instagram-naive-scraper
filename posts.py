from enum import Enum
from typing import Iterable, Iterator

from utils import InsertionOrderSet


class PostStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    DOWNLOADED = 'DOWNLOADED'


class Posts:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.available: InsertionOrderSet[str] = InsertionOrderSet[str]()
        self.downloaded: InsertionOrderSet[str] = InsertionOrderSet[str]()

    def add_posts(self, posts: Iterable[str], status: PostStatus) -> None:
        if isinstance(posts, str):
            posts = [posts]

        posts = [post if self.base_url in post else f'{self.base_url}{post}' for post in posts]

        match status:
            case PostStatus.AVAILABLE:
                self.available.add_multiple(posts)
            case PostStatus.DOWNLOADED:
                self.downloaded.add_multiple(posts)

    def get_posts_to_download(self) -> Iterator[str]:
        for link in self.available:
            if link not in self.downloaded:
                yield link
