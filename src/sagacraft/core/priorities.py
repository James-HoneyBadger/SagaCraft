"""Shared priority enums used across subsystems.

We intentionally keep one canonical priority scale to avoid drift between
plugins and event handling.
"""

from enum import IntEnum


class Priority(IntEnum):
    """Shared priority scale (lower values run first)."""

    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100
