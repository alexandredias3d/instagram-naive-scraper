import logging
from typing import Optional

from utils import get_profile_name


def configure_logger(filepath: Optional[str] = None, level: int = logging.DEBUG) -> None:
    logger_to_config = logger()

    filepath = filepath if filepath else get_default_filepath()

    file_handler = logging.FileHandler(filepath, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] : %(message)s'))

    logger_to_config.setLevel(level)
    logger_to_config.addHandler(file_handler)


def logger() -> logging.Logger:
    return logging.getLogger(get_profile_name())


def get_default_filepath() -> str:
    return f'{get_profile_name()}/execution.log'
