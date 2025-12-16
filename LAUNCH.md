# Quick Launch Scripts

SagaCraft includes two convenient launcher scripts for rapid access:

Manuals:
- `docs/User_Manual.md`
- `docs/Game_Designer_Manual.md`
- `docs/Technical_Reference.md`

## IDE - Adventure Creator
```bash
./Saga.sh
```

Opens the SagaCraft Adventure IDE for creating, editing, and testing adventures.

## Player - Adventure Player
```bash
./Play.sh
```

Launches the lightweight SagaCraft Player to load and play adventures.

Optional adventure file parameter:
```bash
./Play.sh adventures/my_adventure.json
```

## Direct module commands (no scripts)

```bash
PYTHONPATH=src python -m sagacraft.ui.ide
PYTHONPATH=src python -m sagacraft.ui.player
```

---

Both scripts automatically handle:
- Virtual environment activation
- Python path configuration
- Working directory setup
- Argument forwarding

No complex command-line parameters needed!
