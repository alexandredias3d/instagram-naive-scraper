import requests
from dataclasses import dataclass, field
from enum import Enum


class ContentType(Enum):
    IMAGE = 'IMG'
    VIDEO = 'VID'
    TEXT = 'TXT'
    URL = 'URL'
    DEFAULT = ''


@dataclass(frozen=True, eq=True, order=True)
class Content:
    link: str = field(compare=True)
    type: ContentType = field(compare=False)
    text: str = field(compare=False, default='')

    def save(self, filepath: str) -> None:
        match self.type:
            case ContentType.URL | ContentType.TEXT:
                self.__save_text(filepath)
            case ContentType.IMAGE | ContentType.VIDEO:
                self.__save_media(filepath)

    def __save_text(self, filepath: str) -> None:
        with open(f'{filepath}.txt', 'w', encoding='utf-8') as file:
            file.write(self.text)

    def __save_media(self, filepath: str) -> None:
        try:
            response = requests.get(self.link)
            file_type = response.headers['Content-Type'].split('/')[-1]
            with open(f'{filepath}.{file_type}', 'wb+') as file:
                file.write(response.content)
        except Exception as error:
            print(error)
