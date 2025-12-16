#!/usr/bin/env bash
# Compatibility wrapper (kept at repo root).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/scripts/Saga.sh" "$@"
#!/bin/bash
# SagaCraft IDE Launcher
# Usage: ./Saga.sh

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the IDE with PYTHONPATH set
PYTHONPATH="src" python -c "
import tkinter as tk
from sagacraft.ui.ide import AdventureIDE

root = tk.Tk()
root.title('SagaCraft - Adventure Creator')
ide = AdventureIDE(root)
root.mainloop()
"
