"""Shared JSON config helpers for UI modules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def read_json_mapping(path: Path) -> Dict[str, Any]:
    """Read JSON from path and ensure the result is a mapping."""
    with open(path, "r", encoding="utf-8") as handle:
        data: Any = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object in {path}")
    return data


def safe_read_json_mapping(path: Path) -> Dict[str, Any]:
    """Read JSON mapping; return empty dict on IO/JSON/type errors."""
    try:
        return read_json_mapping(path)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def write_json_mapping(path: Path, data: Dict[str, Any]) -> None:
    """Write a mapping as JSON to path (utf-8, indented)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def update_ui_preferences(
    data: Dict[str, Any],
    *,
    theme: str,
    font_family: str,
    font_size: int,
    extra: Dict[str, Any] | None = None,
) -> None:
    """Upsert UI preferences into a config mapping under the `ui` key."""
    ui = data.setdefault("ui", {})
    if not isinstance(ui, dict):
        ui = {}
        data["ui"] = ui

    ui.update(
        {
            "theme": theme,
            "font_family": font_family,
            "font_size": font_size,
        }
    )
    if extra:
        ui.update(extra)


def update_basic_ui_preferences(
    data: Dict[str, Any],
    *,
    theme: str,
    font_family: str,
    font_size: int,
) -> None:
    """Convenience wrapper for the shared (Player) UI preference fields."""
    update_ui_preferences(
        data,
        theme=theme,
        font_family=font_family,
        font_size=font_size,
    )
