import csv
from pathlib import Path
from typing import Any, Dict, Iterable, List, Type, TypeVar

from photo_handler import logger
from .base import ConfigEntry, ConfigEntryError

CLS = TypeVar("CLS")


class BasicConfig:
    """ Config which takes clean CSV file as input with "url", "prompt", "category" columns """
    entries: List[ConfigEntry]

    def __init__(self, entries: Iterable[ConfigEntry]):
        self.entries = sorted(entries)

    @staticmethod
    def get_entry_from_dict(input_dict: Dict[str, Any]) -> ConfigEntry:
        """ Parses a dictionary (typically a CSV entry) and returns an entry """
        return ConfigEntry(url=input_dict["url"],
                           prompt=input_dict.get("prompt"),
                           category=input_dict.get("category"))

    @classmethod
    def from_csvs(cls: Type[CLS], path_to_files: Path, glob_pattern: str) -> CLS:
        """ Initializes the config from a CSV file(s) """
        content = set()
        for file in path_to_files.glob(glob_pattern):
            with file.open(newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        entry = cls.get_entry_from_dict(row)
                    except ConfigEntryError as e:
                        logger.warning(e, exc_info=True)
                        continue
                    content.add(entry)
        return cls(content)
