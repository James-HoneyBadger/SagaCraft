# SagaCraft Launch Scripts - Fixed

## Issue
The `Saga.sh` and `Play.sh` launcher scripts were failing with:
```
ModuleNotFoundError: No module named 'sagacraft'
```

## Root Cause
- Scripts had duplicate shebang lines and conflicting wrapper logic
- PYTHONPATH was set as a relative path (`src`) which didn't work when scripts were executed from different directories
- Scripts were trying to delegate to `/scripts/Saga.sh` and `/scripts/Play.sh` which didn't exist

## Solution

### Saga.sh (IDE Launcher)
✅ Fixed PYTHONPATH to use absolute path: `$SCRIPT_DIR/src`
✅ Removed duplicate shebang and wrapper delegation
✅ Cleaned up script structure
✅ Now exports PYTHONPATH before executing Python

### Play.sh (Game Launcher)
✅ Fixed PYTHONPATH to use absolute path: `$SCRIPT_DIR/src`
✅ Removed duplicate shebang and wrapper delegation
✅ Cleaned up script structure
✅ Now exports PYTHONPATH before executing Python

## How to Use

### Launch the IDE (Adventure Creator)
```bash
./Saga.sh
```

### Play an Adventure
```bash
./Play.sh [optional_adventure_file.json]
```

## Verification
Both scripts have been tested and verified to:
- ✅ Set PYTHONPATH correctly
- ✅ Find the sagacraft module
- ✅ Successfully launch their respective applications

## Files Modified
- `Saga.sh` - IDE launcher script
- `Play.sh` - Game player launcher script

The launchers are now production-ready and can be executed from any directory.
