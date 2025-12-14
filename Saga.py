#!/usr/bin/env python3
"""SagaCraft IDE Launcher - Quick start for adventure creation and editing"""

import sys
import os
from pathlib import Path

# Add src to path so we can import sagacraft modules
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "src"))

# Activate virtual environment if it exists
venv_python = script_dir / ".venv" / "bin" / "python"
if venv_python.exists() and sys.executable != str(venv_python):
    # Restart with venv python
    os.execv(str(venv_python), [str(venv_python), __file__] + sys.argv[1:])

# Change to script directory for relative paths to work
os.chdir(script_dir)

# Now launch the IDE
try:
    import tkinter as tk
    from sagacraft.ui.ide import AdventureIDE
    
    root = tk.Tk()
    root.title("SagaCraft - Adventure Creator")
    ide = AdventureIDE(root)
    root.mainloop()
except Exception as e:
    print(f"Error starting IDE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
