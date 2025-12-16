"""Shared Tkinter menu helpers.

Kept intentionally small: these utilities exist to remove duplication between
`ui/ide.py` and `ui/player.py` while preserving UI behavior.
"""

from __future__ import annotations

import tkinter as tk
from functools import partial
from typing import Any, Callable, Literal, Mapping, Sequence, cast


_Tearoff = Literal[0, 1] | bool


DEFAULT_UI_FONT_FAMILIES: Sequence[str] = (
    "Segoe UI",
    "Arial",
    "Helvetica",
    "Verdana",
    "Tahoma",
    "Calibri",
)

DEFAULT_UI_FONT_SIZES: Sequence[int] = (9, 10, 11, 12, 14, 16)


def create_styled_menu(
    parent: tk.Misc,
    colors: Mapping[str, str],
    tearoff: _Tearoff = 0,
) -> tk.Menu:
    """Create a tk.Menu with the project's standard theme colors."""
    return tk.Menu(
        parent,
        tearoff=tearoff,
        bg=colors["panel"],
        fg=colors["fg"],
        activebackground=colors["accent"],
    )


def add_font_family_commands(
    menu: tk.Menu,
    on_select: Callable[[str], Any],
    families: Sequence[str] = DEFAULT_UI_FONT_FAMILIES,
) -> None:
    """Add font family entries to a menu."""
    for family in families:
        menu.add_command(
            label=family,
            command=cast(Callable[[], Any], partial(on_select, family)),
        )


def add_font_size_commands(
    menu: tk.Menu,
    on_select: Callable[[int], Any],
    sizes: Sequence[int] = DEFAULT_UI_FONT_SIZES,
) -> None:
    """Add font size entries to a menu."""
    for size in sizes:
        menu.add_command(
            label=f"{size}pt",
            command=cast(Callable[[], Any], partial(on_select, size)),
        )
