# Adventure Construction Set (ACS)

**Modern toolkit for building and playing rich text adventures**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

ACS combines a desktop IDE, a natural language parser, and a rules-driven engine so that authors can craft adventures without writing code while power users extend the simulation through Python modules.

---

## 🎮 Overview

- 🖥️ **Graphical IDE only** – launch the Tk-based editor to design rooms, items, NPCs, quests, and play-test in the same workspace.
- 🧠 **Natural language parser** – `src/acs/core/parser.py` translates conversational input into structured commands for the engine.
- ⚙️ **Modular systems** – combat, achievements, journal, context hints, accessibility, and environment logic live in `src/acs/systems/`.
- 🔌 **Extensible infrastructure** – service registry, event bus, and plugin scaffolding allow additional systems without touching the engine core.
- 📚 **Data-driven content** – adventures are JSON documents; configuration and plugin toggles live under `config/`.

---

## 🚀 Quick Start

1. Clone the repository and move into it:
   ```bash
   git clone https://github.com/James-HoneyBadger/HB_Adventure_Games.git
   cd HB_Adventure_Games
   ```
2. (Optional) Create a virtual environment and install local tooling:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   ```
   ACS relies on the Python standard library. Install additional tooling (flake8, pytest) if you do not have them globally.
3. Launch the IDE:
   ```bash
   python -m src.acs.ui.ide
   ```
   The interface starts in creation mode; switch to **Play** to test your adventure.
4. Prefer a guided entry point? Run `./quickstart.sh` for launcher shortcuts.

---

## 🧰 Capabilities

### Players
- Classic text adventure experience with party management, tactical combat, and environmental feedback.
- Save/load support and optional accessibility overlays for readability.
- Smart command history with typo correction (`SmartCommandSystem` in `src/acs/tools/commands.py`).

### Creators
- Drag-and-drop editors for rooms, props, monsters, effects, and quest lines.
- Inline validators highlight missing exits, orphaned items, or inconsistent NPC data.
- Export adventures as portable JSON bundles for sharing.

### Engine & Infrastructure
- `AdventureGame` (`src/acs/core/engine.py`) owns game state, command dispatch, and subsystem coordination.
- `NaturalLanguageParser` (`src/acs/core/parser.py`) and helper models (`src/acs/core/natural_language.py`) deliver multi-word verb handling and direction normalization.
- Systems in `src/acs/systems/` implement combat, achievements, journal, tutorials, NPC context, and environmental effects.
- Shared utilities live in `src/acs/data/` (config/data services) and `src/acs/tools/` (modding hooks, command tooling).
- `src/acs/core/base_plugin.py` and `plugins/achievements_plugin.py` illustrate the plugin contract for third-party extensions.

---

## 🏗️ Architecture at a Glance

```
┌──────────────────────────────────────────────┐
│                Adventure IDE                 │
│            (src/acs/ui/ide.py)               │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│               AdventureGame                   │
│         (src/acs/core/engine.py)              │
├──────────────┬─────────────┬─────────────────┤
│   Parser     │   Systems   │   Services &    │
│(core/parser) │(systems/*)  │  Registries     │
└──────────────┴─────────────┴─────────────────┘
                       │
          Adventure JSON + Config Assets
```

- **Event Bus** (`src/acs/core/event_bus.py`) and **Service Registry** (`src/acs/core/services.py`) supply loose coupling.
- **Data services** (`src/acs/data/*.py`) load/save adventures, persist settings, and expose domain queries.
- **Plugin surface** (`plugins/`, `config/plugins/`) provides opt-in features without editing the core engine.

---

## 📂 Project Layout

```
HB_Adventure_Games/
├── adventures/               # Bundled adventure JSON files
├── archive/                  # Legacy engine snapshots and assets
├── config/                   # Engine & plugin configuration (JSON/YAML)
│   └── plugins/
├── docs/                     # Manuals, technical references, guides
├── plugins/                  # Standalone plugin packages
├── saves/                    # Player save files
├── scripts/                  # Utility scripts and helpers
├── src/acs/
│   ├── core/                 # Engine, parser, state, infrastructure
│   ├── data/                 # Config/data access services
│   ├── systems/              # Gameplay systems (combat, achievements, …)
│   ├── tools/                # Modding and command utilities
│   └── ui/                   # Graphical IDE and accessibility modules
├── tests/                    # Pytest suites covering parser & systems
├── quickstart.sh             # Menu for common launch tasks
└── LICENSE                   # MIT license text
```

For a narrated walkthrough see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

---

## 📘 Documentation

| Topic | Primary Reference |
|-------|-------------------|
| Getting started | [START_HERE.md](START_HERE.md) |
| Player & creator guidance | [docs/user-guides/QUICKSTART.md](docs/user-guides/QUICKSTART.md) |
| IDE walkthrough | [docs/user-guides/IDE_GUIDE.md](docs/user-guides/IDE_GUIDE.md) |
| System architecture | [docs/reference/ARCHITECTURE.md](docs/reference/ARCHITECTURE.md) |
| API & module details | [docs/reference/TECHNICAL_REFERENCE.md](docs/reference/TECHNICAL_REFERENCE.md) |
| Contributing workflow | [docs/developer-guides/CONTRIBUTING.md](docs/developer-guides/CONTRIBUTING.md) |

`docs/README.md` lists every guide by role.

---

## 🧪 Development & Quality

Run the automated checks locally:

```bash
python -m pytest              # run the regression suite
python -m flake8              # lint using the repo configuration
```

The test suite focuses on parser correctness, command coverage, and system integration scenarios (`tests/test_all_*`).

---

## 🤝 Contributing

Pull requests are welcome! Review the coding standards, testing expectations, and issue triage process in [docs/developer-guides/CONTRIBUTING.md](docs/developer-guides/CONTRIBUTING.md).

---

## 📜 License

Distributed under the [MIT License](LICENSE). Crafted with ❤️ by Honey Badger Universe.
