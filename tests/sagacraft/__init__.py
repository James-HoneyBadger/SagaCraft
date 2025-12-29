"""Test-only import shim for the `sagacraft` package.

The project source lives in `src/sagacraft`, but `unittest discover` typically
places the `tests/` directory on `sys.path` (not `src/`).

By making `tests/sagacraft` a namespace package whose `__path__` also includes
`../src/sagacraft`, we allow imports like `from sagacraft.systems...` to work
without requiring `PYTHONPATH=src`.

This file is intentionally lightweight and only affects test runs.
"""

from __future__ import annotations

import os
import pkgutil

# Extend as a namespace package, then point at the real implementation.
__path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore[name-defined]

_tests_pkg_dir = os.path.dirname(__file__)
_repo_root = os.path.dirname(os.path.dirname(_tests_pkg_dir))
_src_pkg_dir = os.path.join(_repo_root, "src", "sagacraft")

if os.path.isdir(_src_pkg_dir) and _src_pkg_dir not in __path__:
    __path__.append(_src_pkg_dir)
