#!/usr/bin/env bash
# Compatibility wrapper (kept at repo root).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/scripts/Play.sh" "$@"
#!/bin/bash
# SagaCraft Game Player Launcher
# Usage: ./Play.sh [adventure_file.json]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the game player with PYTHONPATH set
PYTHONPATH="src" python -m sagacraft.ui.player "$@"
