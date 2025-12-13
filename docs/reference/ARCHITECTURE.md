# Architecture Guide

## Overview

SagaCraft is built around a **modular, data-driven engine** that keeps authoring tools, runtime systems, and extension points cleanly separated. Core design goals:

- **Loose coupling** through a service registry and event bus hooks
- **Extensibility** via plugins and drop-in gameplay systems
- **Maintainability** with focused modules under `src/acs/`
- **Testability** using pytest suites for parser and system validation

---

## Architecture Layers

```
┌──────────────────────────────────────────────┐
│                 Adventure IDE                │
│             (src/acs/ui/ide.py)              │
└──────────────────────┬───────────────────────┘
                       │ invokes
┌──────────────────────▼───────────────────────┐
│              AdventureGame Engine            │
│          (src/acs/core/engine.py)            │
├──────────────┬─────────────┬─────────────────┤
│ Natural Lang.│ Gameplay    │ Services & Data │
│ Parser        │ Systems     │ (core/data/tools)│
└──────────────┴─────────────┴─────────────────┘
                       │ consumes
          Adventure JSON + Config Assets + Plugins
```

---

## Directory Map

```
SagaCraft/
├── adventures/               # Bundled adventure JSON scenarios
├── config/                   # Engine defaults + per-plugin settings
├── docs/                     # Guides, references, manuals
├── plugins/                  # Optional plugin packages (e.g. achievements)
├── saves/                    # Player save files
├── src/acs/                  # Application source
│   ├── core/                 # Engine, parser, state, plugin contract
│   ├── data/                 # Config, data, and I/O services
│   ├── systems/              # Built-in gameplay systems
│   ├── tools/                # Command helpers and modding hooks
│   └── ui/                   # Tkinter IDE and accessibility surfaces
├── tests/                    # Pytest suites (parser + integration)
└── quickstart.sh             # CLI launcher / maintenance script
```

Refer to `PROJECT_STRUCTURE.md` for an annotated walkthrough of every folder.

---

## Core Modules

### AdventureGame (`src/acs/core/engine.py`)

`AdventureGame` orchestrates runtime play:

- Loads adventure JSON (rooms, items, NPCs, effects) and builds domain objects
- Maintains `Player`, turn counter, party, and combat state
- Integrates optional systems (achievements, journal, environment, tutorial, accessibility)
- Routes parsed commands to handlers (`look`, `move`, `get`, combat verbs, etc.)
- Emits feedback to the console/IDE play panel

Minimal usage when embedding the engine:

```python
from acs.core.engine import AdventureGame

game = AdventureGame("adventures/colossal_storyworks_showcase.json")
game.load_adventure()
game.look()           # display current room
game.move("north")    # process a command
```

### Natural Language Parser (`src/acs/core/parser.py` & `natural_language.py`)

- Tokenizes player input, recognises verbs, directions, and objects
- Resolves synonyms (e.g. `take`, `grab`, `pick up`) into canonical actions
- Supplies higher-level models (`ParsedCommand`, grammar helpers) used by `AdventureGame`
- Provides companion handling and pronoun resolution when enhanced parser is enabled

### Event Bus & Services (`src/acs/core/event_bus.py`, `services.py`)

- `EventBus` implements publish/subscribe hooks so new systems can react to engine events without direct coupling
- `ServiceRegistry` manages shared services (config, data, I/O) exposed to plugins and gameplay systems
- Services derive from `Service` and support `initialize(config)` / `shutdown()` lifecycles

### GameState (`src/acs/core/game_state.py`)

- Central store for player stats, flags, quest progress, and plugin data
- Supports serialization for saving/loading via `data/io_service.py`
- Offers helpers like `set_flag`, `increment_stat`, and plugin-scoped storage

### Plugin Contract (`src/acs/core/base_plugin.py`)

- `BasePlugin` defines initialization, enable/disable, and shutdown hooks
- `PluginMetadata` describes name, version, dependencies, and `PluginPriority`
- Built-in systems adopt the same API, ensuring consistent lifecycle management

---

## Gameplay Systems (`src/acs/systems/`)

Modular systems extend the base engine by subscribing to events, reading state, or exposing helper APIs:

- `achievements.py` – Tracks player statistics, unlocks achievements, and persists progress snapshots
- `combat.py` – Handles turn-based combat resolution, attack rolls, and damage output
- `environment.py` – Simulates day/night cycles, weather, and ambient room flavour
- `journal.py` – Logs narrative events and quest updates for review in the IDE
- `npc_context.py` – Maintains NPC memory, relationship scores, and conversation context
- `tutorial.py` – Provides context-sensitive hints based on player actions

Systems can be enabled/disabled individually, and new modules can be added by following the plugin contract.

---

## Data & Tools Layers

### Services (`src/acs/data/`)

- `config_service.py` – Loads engine defaults and writes per-plugin overrides (JSON/YAML)
- `data_service.py` – Caches rooms, items, monsters, and offers lookup helpers used by systems
- `io_service.py` – Wraps file-system access for adventures and save slots

### Authoring Utilities (`src/acs/tools/`)

- `commands.py` – Smart command history, fuzzy suggestions, macro execution
- `modding.py` – Safe execution environment for scripted extensions and custom triggers

---

## User Interface (`src/acs/ui/`)

- `ide.py` is the Tk-based Adventure IDE (entry point `python -m src.acs.ui.ide`)
  - Tabs for rooms, items, NPCs, conversations, quests, testing, and analytics
  - Includes export/import workflows to JSON
  - Embeds a play panel for immediate testing
- `accessibility.py` adds adjustable fonts, high-contrast themes, and text-to-speech hooks

The IDE communicates with the engine by invoking API methods and streaming console output back into the UI.

---

## Plugins & Extensibility

- Example plugin: `plugins/achievements_plugin.py` demonstrates registering metadata, reading configuration, and responding to events
- Plugin configuration lives under `config/plugins/<plugin>.json` or `.yaml`
- Third-party plugins receive access to `GameState`, `EventBus`, and `ServiceRegistry` during `initialize`
- Set plugin priority using `PluginPriority` (`CRITICAL`, `HIGH`, `NORMAL`, `LOW`) to control load order

Lifecycle summary:

1. Engine discovers/instantiates plugin
2. `initialize(state, event_bus, services)` wired with dependencies
3. `get_event_subscriptions()` returns mapping of event names to handlers
4. `on_enable()` fires when plugin becomes active
5. `on_disable()` and `shutdown()` handle teardown

---

## Adventure Assets & Configuration

- **Adventures**: JSON definitions in `adventures/` include rooms, items, monsters, effects, and metadata consumed by `AdventureGame.load_adventure()`
- **Saves**: Player progress stored under `saves/` via `io_service`
- **Engine defaults**: `config/engine.json` toggles themes, auto-save, difficulty, and IDE defaults
- **Plugins**: Each plugin has a companion config file under `config/plugins/`

---

## Testing & Quality

- Pytest suites live in `tests/`
  - `test_all_commands.py` verifies parser verb coverage
  - `test_all_systems.py` runs integration checks for combat, journal, tutorial, achievements, etc.
  - `test_parser_detailed.py` covers complex parsing edge cases
- Execute locally with:

```bash
python -m pytest
python -m flake8
```

These checks guard against regressions as systems evolve.

---

## Event Flow (Conceptual)

```
Player enters command in IDE → NaturalLanguageParser → AdventureGame command handler
       ↓                                         ↓
Optional EventBus notifications ──────────────► Systems (achievements, journal, tutorial, etc.)
       ↓
ServiceRegistry for shared utilities (config, data, I/O)
```

Even when events are not explicitly published, systems read from shared state/services to react consistently.

---

## Related Documentation

- [PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md) – directory deep dive
- [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) – API reference and module catalog
- [PLUGIN_GUIDE.md](../developer-guides/PLUGIN_GUIDE.md) – building third-party extensions
- [CONTRIBUTING.md](../developer-guides/CONTRIBUTING.md) – coding standards and workflows

The architecture continues to evolve; keep an eye on `docs/legacy/` for historical context and `project-management/` for upcoming roadmap items.
