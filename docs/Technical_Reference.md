# SagaCraft Technical Reference

## Repository layout
- `src/sagacraft/`: Python package (engine, systems, tools, UI)
- `sagacraft_engine.py`: standalone extended engine module used by the Player
- `adventures/`: example adventures (`.json`)
- `config/`: configuration (`config/engine.json`, mod state, recent adventures)
- `mods/`: user mods (Python scripts) and examples
- `plugins/`: plugin-style components (optional; may depend on older paths)
- `scripts/`: launch scripts (`scripts/Play.sh`, `scripts/Saga.sh`)
- Root wrappers: `Play.sh`, `Saga.sh` delegate to `scripts/`

## Primary entrypoints
- Player UI: `PYTHONPATH=src python -m sagacraft.ui.player`
- IDE UI: `PYTHONPATH=src python -m sagacraft.ui.ide`

## Engines
SagaCraft has two related engine implementations:

### Core engine (`sagacraft.core.engine`)
- Defines core world model dataclasses: `Room`, `Item`, `Monster`, `Player`
- Main engine: `AdventureGame`
- Command processing: `AdventureGame.process_command()`
- Built-in help: `AdventureGame.show_help()`

### Extended engine (`sagacraft.core.extended_engine` and `sagacraft_engine.py`)
- Adds optional richer content (extended item/room/monster fields, plus puzzles/quests/dialogues in `sagacraft_engine.py`).
- Player loads the engine dynamically from `sagacraft_engine.py` and expects one of:
  - `ExtendedAdventureGame`
  - `EnhancedAdventureGame`

## UI
- `sagacraft.ui.player`: lightweight play client; also provides headless modes (`--check`, `--load`, etc.).
- `sagacraft.ui.ide`: full Adventure IDE/editor.
- Shared UI helpers:
  - `sagacraft.ui.menu_helpers`: shared Tk menu builders
  - `sagacraft.ui.config_io`: safe JSON read/write + UI preference updates
  - `sagacraft.ui.engine_runner`: command execution helpers
  - `sagacraft.ui.theme`: theme definitions

## Configuration
- `config/engine.json`:
  - `engine`: metadata/settings
  - `gameplay`: runtime defaults (auto-save etc.)
  - `ui`: theme + font preferences

## Modding and scripting
- `sagacraft.tools.modding`:
  - Event model: `EventType` values like `ON_ENTER_ROOM`, `ON_COMMAND`, `ON_UNKNOWN_COMMAND`
  - Custom commands: `CustomCommand`
  - Execution context: `ScriptContext` (restricted imports + helper accessors)

## Sanity checks
Without a test suite, basic validation is typically:
- Import check: `PYTHONPATH=src python -c "import sagacraft; import sagacraft.ui.player; import sagacraft.ui.ide"`
- Engine check: `PYTHONPATH=src python -m sagacraft.ui.player --check`
- Load check: `PYTHONPATH=src python -m sagacraft.ui.player --load adventures/infinite_archive.json --cmd "help"`
