"""Helpers for loading adventure JSON files."""

from __future__ import annotations

import json
from typing import Any, Dict


def read_adventure_data(adventure_file: str) -> Dict[str, Any]:
    """Read and parse an adventure JSON file.

    Raises:
        OSError: If the file can't be read.
        json.JSONDecodeError: If the file isn't valid JSON.
        TypeError: If the parsed JSON isn't a mapping.
    """
    with open(adventure_file, "r", encoding="utf-8") as handle:
        data: Any = json.load(handle)

    if not isinstance(data, dict):
        raise TypeError("Adventure JSON must be an object at the top level")

    return data
