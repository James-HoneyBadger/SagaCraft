"""Utilities for running the engine while capturing stdout.

Both the IDE and the lightweight player use stdout-based rendering.
"""

from __future__ import annotations

import sys
from io import StringIO
from typing import Any, Callable, Optional, Tuple


def capture_stdout(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Tuple[Any, str]:
    """Run func(*args, **kwargs) while capturing stdout; returns (result, text)."""
    old_stdout = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer
    try:
        result = func(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    return result, buffer.getvalue()


def run_engine_command(engine: Any, command: str) -> Tuple[str, Optional[Exception]]:
    """Run engine.process_command(command) while capturing stdout.

    Returns:
        (output, error)
    """
    old_stdout = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer
    error: Optional[Exception] = None
    try:
        engine.process_command(command)
    except (RuntimeError, ValueError, AttributeError, OSError) as exc:
        error = exc
    finally:
        sys.stdout = old_stdout
    return buffer.getvalue(), error
