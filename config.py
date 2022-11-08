import json

from logger import logger


class Config:

    def __init__(self, filename: str = 'config.json') -> None:
        self.username: str = ''
        self.password: str = ''
        self.headless: bool = False
        self.action_delay: float = 0
        self.loading_delay: int = 15
        self.scrolling_delay: int = 30
        self.scraping_delay: int = 70
        self.max_retries: int = 5
        self.filename: str = filename

    def read(self) -> 'Config':
        with open(self.filename, 'r', encoding='utf-8') as file:
            config = json.load(file)
            self.username = config['username']
            self.password = config['password']
            self.action_delay = config['action_delay'] * 1_000
            self.loading_delay = config['loading_delay']
            self.scrolling_delay = config['scrolling_delay']
            self.scraping_delay = config['scraping_delay']
            self.max_retries = config['max_retries']

            browser = config['browser'].lower()
            match browser:
                case 'gui':
                    self.headless = False
                case 'headless':
                    self.headless = True
                case _:
                    logger().warning(f'browser option {browser} not recognized (available options are gui and headless')
        return self
