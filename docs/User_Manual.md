# SagaCraft User Manual

## What SagaCraft is
SagaCraft is a text-first adventure engine with two interfaces:
- **Player**: a lightweight UI for playing adventures.
- **IDE**: an editor for creating, validating, and play-testing adventures.

## Install / setup
SagaCraft is a Python project using a `src/` layout.

- Player/IDE require Python 3 and Tkinter.
- If you use the included virtual environment, it lives in `.venv/`.

## Quickstart
Play an adventure:
- `./Play.sh`
- Optional: `./Play.sh adventures/infinite_archive.json`

Open the Adventure IDE:
- `./Saga.sh`

Equivalent direct commands (if you prefer not using the scripts):
- Player (GUI): `PYTHONPATH=src python -m sagacraft.ui.player`
- IDE (GUI): `PYTHONPATH=src python -m sagacraft.ui.ide`

## Playing basics
In the Player window:
- Use **Open Adventure** to load a `.json` adventure file.
- Type commands in the input box and press **Enter**.
- Use **Look** to re-print the current room description.

### Common commands
The engine exposes in-game help; type `help`.

Typical built-ins include:
- Movement: `north/south/east/west/up/down` (and `n/s/e/w/u/d`)
- Info: `look` (`l`), `inventory` (`i`), `status`
- Actions: `take <item>` / `get <item>`, `drop <item>`, `attack <target>`
- Party (if enabled): `party`, `recruit <npc>`
- Exit: `quit` (`q`)

## Saving and loading
- Player UI includes **Save Slot 1** and **Load Slot 1**.
- Save files are written to `saves/save_slot_<slot>.json`.

Note: An adventure may disable saving via its `settings.allow_save` value.

## Themes and fonts
UI preferences are stored in `config/engine.json` under the `ui` object (theme + font).

## Headless mode (CLI)
The Player module also supports headless flags for automation:

- `--check`: verify the engine module loads
  - `PYTHONPATH=src python -m sagacraft.ui.player --check`
- `--load <path>`: load an adventure, print intro + first `look`
  - `PYTHONPATH=src python -m sagacraft.ui.player --load adventures/infinite_archive.json`
- Optional with `--load`:
  - `--seed <int>` deterministic RNG
  - `--cmd "<command>"` run one command
  - `--cmds <file>` run commands from a text file (`#` comments allowed)
  - `--save <slot>` save state
  - `--load-slot <slot>` load a saved slot and print current room
  - `--transcript <file>` append output to a transcript file

## Troubleshooting
- If `./Play.sh` or `./Saga.sh` fails, try running with:
  - `PYTHONPATH=src python -m sagacraft.ui.player --check`
- On Linux, missing Tkinter often looks like an import error for `tkinter`.
