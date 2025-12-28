#!/usr/bin/env bash
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
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
python -c "
import tkinter as tk
from sagacraft.ui.ide import AdventureIDE

root = tk.Tk()
root.title('SagaCraft - Adventure Creator')
ide = AdventureIDE(root)
root.mainloop()
"
