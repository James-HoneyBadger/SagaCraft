"""Ensure local `src/` is on `sys.path` when running tests.

When running `python -m unittest discover tests`, Python adds the `tests/` folder
to `sys.path`, not the repo root. Placing `sitecustomize.py` here ensures the
project package (`src/sagacraft`) is importable without requiring PYTHONPATH.
"""

from __future__ import annotations

import os
import sys


def _ensure_src_on_syspath() -> None:
    tests_dir = os.path.dirname(__file__)
    repo_root = os.path.dirname(tests_dir)
    src_path = os.path.join(repo_root, "src")

    if os.path.isdir(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)


_ensure_src_on_syspath()
