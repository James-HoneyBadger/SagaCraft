"""Test/runtime convenience: ensure local `src/` is on `sys.path`.

Python automatically imports `sitecustomize` (if present on sys.path) during
startup after the standard `site` initialization.

This lets contributors run `python -m unittest discover` from the repo root
without needing to set `PYTHONPATH=src`.
"""

from __future__ import annotations

import os
import sys


def _ensure_src_on_syspath() -> None:
    repo_root = os.path.dirname(__file__)
    src_path = os.path.join(repo_root, "src")

    if os.path.isdir(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)


_ensure_src_on_syspath()
