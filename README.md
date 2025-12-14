# SagaCraft

A streamlined, text-first adventure engine and player.

## Quickstart

Run the SagaCraft player:

```bash
PYTHONPATH=src python -m src.sagacraft.ui.player
```

## Headless Usage

Run the player without GUI for automation, CI, or servers.

- `--check`: Verify engine import.
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --check
  ```
- `--load <path>`: Load an adventure and print intro + first look.
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json
  ```
- `--cmd "<command>"`: Execute one command after load.
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json --cmd "look"
  ```
- `--cmds <file>`: Execute a sequence of commands from a file (non-empty lines; `#` for comments).
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json --cmds commands_demo.txt
  ```
- `--save <slot>`: Save the current state to `saves/save_slot_<slot>.json`.
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json --cmds commands_demo.txt --save 1
  ```
- `--load-slot <slot>`: Load a saved slot and print current room.
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json --load-slot 1
  ```
- `--transcript <file>`: Append all output to a transcript file while printing to stdout.
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json --cmds commands_demo.txt --transcript transcripts/run.txt
  ```
- `--seed <int>`: Set random seed for deterministic gameplay (optional with any headless flag).
  ```bash
  PYTHONPATH=src python -m src.sagacraft.ui.player --load adventures/infinite_archive.json --seed 42
  ```

Example end-to-end:

```bash
PYTHONPATH=src python -m src.sagacraft.ui.player \
  --load adventures/infinite_archive.json \
  --cmds commands_demo.txt \
  --save 1 \
  --load-slot 1 \
  --transcript transcripts/run2.txt \
  --seed 42
```
