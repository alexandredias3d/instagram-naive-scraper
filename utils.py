import sys
from pathlib import Path
from typing import Generic, TypeVar, Set, MutableSequence, Iterable, Iterator, Optional

T = TypeVar('T')


class InsertionOrderSet(Generic[T]):
    def __init__(self, elements: Optional[Iterable[T]] = None) -> None:
        self.__set: Set[T] = set()
        self.__list: MutableSequence[T] = list()

        if elements:
            self.add_multiple(elements)

    def add(self, element: T) -> None:
        if element not in self.__set:
            self.__set.add(element)
            self.__list.append(element)

    def add_multiple(self, elements: Iterable[T]) -> None:
        for element in elements:
            self.add(element)

    def contains(self, element: T) -> bool:
        return element in self.__set

    def contains_any(self, elements: Iterable[T]) -> bool:
        return any(element in self.__set for element in elements)

    def __iter__(self) -> Iterator[T]:
        yield from self.__list

    def __len__(self) -> int:
        return len(self.__list)


def get_profile_name() -> str:
    return sys.argv[1]


def get_config_file() -> str:
    return sys.argv[2] if len(sys.argv) >= 3 else 'config.json'


def get_base_url() -> str:
    return 'https://www.instagram.com'


def create_folder(filepath: str) -> None:
    Path(filepath).mkdir(parents=True, exist_ok=True)


def folder_number(filepath: str) -> int:
    parent = Path(filepath).parent
    return len(list(parent.glob(f'{filepath}*')))


def create_profile_folder() -> None:
    create_folder(get_profile_name())
