"""Shared UI theme palettes.

These palettes are used by both the IDE and the lightweight player.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict


_THEMES: Dict[str, Dict[str, str]] = {
    "Dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "accent": "#4a90e2",
        "accent_dark": "#357abd",
        "success": "#5cb85c",
        "warning": "#f0ad4e",
        "danger": "#d9534f",
        "sidebar": "#3c3c3c",
        "panel": "#353535",
        "border": "#4a4a4a",
        "text_bg": "#252525",
        "button": "#4a90e2",
        "button_hover": "#357abd",
    },
    "Light": {
        "bg": "#f5f5f5",
        "fg": "#333333",
        "accent": "#4a90e2",
        "accent_dark": "#357abd",
        "success": "#5cb85c",
        "warning": "#f0ad4e",
        "danger": "#d9534f",
        "sidebar": "#e0e0e0",
        "panel": "#ffffff",
        "border": "#cccccc",
        "text_bg": "#ffffff",
        "button": "#4a90e2",
        "button_hover": "#357abd",
    },
    "Dracula": {
        "bg": "#282a36",
        "fg": "#f8f8f2",
        "accent": "#bd93f9",
        "accent_dark": "#9d73d9",
        "success": "#50fa7b",
        "warning": "#f1fa8c",
        "danger": "#ff5555",
        "sidebar": "#1e1f28",
        "panel": "#44475a",
        "border": "#6272a4",
        "text_bg": "#1e1f28",
        "button": "#bd93f9",
        "button_hover": "#9d73d9",
    },
    "Nord": {
        "bg": "#2e3440",
        "fg": "#eceff4",
        "accent": "#88c0d0",
        "accent_dark": "#5e81ac",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "danger": "#bf616a",
        "sidebar": "#3b4252",
        "panel": "#434c5e",
        "border": "#4c566a",
        "text_bg": "#2e3440",
        "button": "#88c0d0",
        "button_hover": "#5e81ac",
    },
    "Monokai": {
        "bg": "#272822",
        "fg": "#f8f8f2",
        "accent": "#66d9ef",
        "accent_dark": "#46b9cf",
        "success": "#a6e22e",
        "warning": "#e6db74",
        "danger": "#f92672",
        "sidebar": "#1e1f1c",
        "panel": "#3e3d32",
        "border": "#75715e",
        "text_bg": "#1e1f1c",
        "button": "#66d9ef",
        "button_hover": "#46b9cf",
    },
}


def get_default_themes() -> Dict[str, Dict[str, str]]:
    """Return a fresh copy of the default theme palette mapping."""
    return deepcopy(_THEMES)
