#!/usr/bin/env bash
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
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
python -m sagacraft.ui.player "$@"
