import csv
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Type, TypeVar

from midjourney import logger

CLS = TypeVar("CLS")


class ConfigEntryError(Exception):
    """ Raised during Config initialization """


class ConfigEntry(NamedTuple):
    url: str
    prompt: Optional[str]
    category: Optional[str]


class BasicConfig:
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


class MidjourneyCsvConfig(BasicConfig):
    @staticmethod
    def _extract_url_parameter(url_string) -> str:
        # Parse the URL string and get the "url" parameter value
        parsed_url = urllib.parse.urlparse(url_string)
        url_param = urllib.parse.parse_qs(str(parsed_url.query)).get("url", None)
        if url_param:
            # Decode the URL parameter value
            decoded_url = urllib.parse.unquote(url_param[0])
            return decoded_url
        raise ConfigEntryError("Expected url query parameter: %s", url_string)

    @staticmethod
    def _transform_url(url: str) -> str:
        """ .../0_0_123_N.webp -> .../0_0.webp """
        filename = url.rsplit('/', 1)[-1]
        if '_' in filename:
            parts = filename.split('.')
            name_parts = parts[0].split('_')
            if len(name_parts) > 2:
                name_parts = name_parts[0:2]
            filename = '_'.join(name_parts) + '.' + parts[-1]
            return url.rsplit('/', 1)[0] + '/' + filename
        else:
            return url

    @classmethod
    def get_entry_from_dict(cls, input_dict: Dict[str, Any]) -> ConfigEntry:
        # category
        path = str(urllib.parse.urlparse(input_dict["web-scraper-start-url"]).path)
        category = path.split("/")[-2]
        # url
        url = input_dict["image-src"]
        if url.startswith("/_next"):
            url = cls._extract_url_parameter(url)
            if url is None:
                message = "Unknown URL format: %s" % input_dict["image-src"]
                logger.warning(message)
                raise ConfigEntryError(message)
        url = cls._transform_url(url)
        # prompt
        prompt = input_dict["prompt"]
        return ConfigEntry(url=url, category=category, prompt=prompt)