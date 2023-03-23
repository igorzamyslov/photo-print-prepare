from __future__ import annotations

from typing import NamedTuple, Optional


class ConfigEntryError(Exception):
    """ Raised during Config initialization """


class ConfigEntry(NamedTuple):
    url: str
    prompt: Optional[str]
    category: Optional[str]
