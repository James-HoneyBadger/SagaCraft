# 📁 Project Structure

**SagaCraft v3.0.0**
Last Updated: February 2025

---

## 🗂️ Directory Organization

> Diagrams below use the branded name for clarity.

```
SagaCraft/
├── adventures/           # Bundled flagship adventure JSON
├── archive/              # Historical engines and Apple II assets
├── config/               # Engine defaults (e.g., engine.json)
├── docs/                 # Documentation grouped by audience
├── plugins/              # Optional plugin modules
├── src/                  # Engine source code (package: acs)
├── tests/                # Pytest suites
├── acs_engine_enhanced.py
├── quickstart.sh
├── README.md
└── START_HERE.md
```

---

## 📚 Documentation Organization

Documentation is organized by user role and purpose:

### **docs/user-guides/**
Documentation for players and adventure creators:
- `USER_MANUAL.md` - Complete guide for players and creators
- `QUICKSTART.md` - Get started in 5 minutes
- `IDE_GUIDE.md` - Using the graphical IDE
- `PLAY_IN_IDE_GUIDE.md` - Playing games in the IDE
- `GAME_CREATION_GUIDE.md` - Building new adventures step by step
- `EXAMPLE_GAMEPLAY.md` - Sample gameplay sessions

### **docs/developer-guides/**
Documentation for contributors and plugin developers:
- `CONTRIBUTING.md` - How to contribute to the project
- `PLUGIN_GUIDE.md` - Creating custom plugins
- `ENHANCED_PARSER_GUIDE.md` - Parser internals and extensions
- `ENHANCED_FEATURES_GUIDE.md` - Advanced feature implementation

### **docs/reference/**
Technical specifications and API documentation:
- `TECHNICAL_REFERENCE.md` - Architecture, APIs, internals
- `ARCHITECTURE.md` - System architecture overview
- `MODULAR_ARCHITECTURE.md` - Module structure and design
- `COMMANDS.md` - Command catalogue with examples
- `DOCUMENTATION_INDEX.md` - Master documentation index
- `DOCUMENTATION_REVIEW.md` - Documentation audit results

### **docs/project-management/**
Planning, organization, and status documents:
- `PROJECT_SUMMARY.md` - Project overview and goals
- `PROJECT_ORGANIZATION.md` - Organization and structure
- `FILE_ORGANIZATION.md` - File structure documentation
- `ENHANCEMENT_PLAN.md` - Planned enhancements
- `REFACTORING_ROADMAP.md` - Refactoring plans

## 🎮 Adventures Library

### `adventures/`

| Adventure | Rooms | Items | NPCs | Puzzles | Quests | Highlights |
|-----------|-------|-------|------|---------|--------|------------|
| `colossal_storyworks_showcase.json` | 22 | 24 | 8 | 5 | 3 | Comprehensive flagship adventure demonstrating every system |

- **Total Content**: 22 rooms, 24 items, 8 NPCs, 5 puzzles, 3 quests.
- Designed to exercise combat, quests, puzzles, environmental effects, and dialog trees out of the box.
- Use this file as a template when authoring new adventures.

See `ADVENTURE_LIBRARY.md` for encounter breakdowns and storytelling guidance.

---

## 🔧 Source Code Layout (`src/acs/`)

```
src/acs/
├── core/        # Engine orchestration, state, parser, event bus
├── data/        # Data access and configuration services
├── systems/     # Gameplay systems layered on top of the engine
├── tools/       # Helper utilities for authors and developers
└── ui/          # IDE and UI components
```

### `core/`
| File | Purpose |
|------|---------|
| `engine.py` | `AdventureGame` runtime loop, command dispatch, plugin hooks |
| `engine_enhanced.py` | Enhanced engine dataclasses and load helpers |
| `parser.py` | Natural language parsing and command normalization |
| `natural_language.py` | Grammar structures and interpretation helpers |
| `game_state.py` | Dataclasses representing player, world, and plugin state |
| `event_bus.py` | Publish/subscribe infrastructure for decoupled systems |
| `services.py` | Lightweight service locator used by systems and plugins |
| `base_plugin.py` | Base class shared by optional plugin packages |
| `inform_integration.py` | Compatibility helpers for Inform-style content |

### `data/`
- `config_service.py` – Reads/writes engine configuration and persists changes.
- `data_service.py` – In-memory repository for rooms, items, NPCs, and quests.
- `io_service.py` – File system helpers for adventures and save data.

### `systems/`
Built-in gameplay systems that the core engine wires in automatically:
- `achievements.py` – Tracks milestones and awards achievements.
- `combat.py` – Tactical combat loop with status effects and AI reactions.
- `environment.py` – Handles weather, lighting, and environmental modifiers.
- `journal.py` – Quest log and narrative journaling.
- `npc_context.py` – Relationship tracking and conversational state.
- `tutorial.py` – Adaptive hinting and onboarding sequences.

### `tools/`
- Utility helpers that authors can reuse (command helpers, data inspectors).

### `ui/`
- `ide.py` (exposed via `python -m src.acs.ui.ide`) – Tkinter IDE for editing adventures.
- Supporting modules for themes, accessibility, and I/O adapters.

---

## ⚙️ Configuration & Plugins

- `config/engine.json` defines engine defaults such as auto-save, theme, and tutorial hints.
- `plugins/achievements_plugin.py` demonstrates how to extend the engine via the plugin API.
- Additional plugins can live alongside the built-in example; enable them through configuration.

---

## 🧪 Testing & Quality

Current automated tests live in `tests/`:
- `test_simple.py` – Smoke test for engine startup and basic commands.
- `test_all_commands.py` – Verifies the parser vocabulary.
- `test_all_systems.py` – Exercises combat, achievements, tutorial, and environment systems.
- `test_parser_detailed.py` – Deep regression suite for parsing edge cases.
- `demo_architecture.py` – Illustrative architecture checks and assertions.

Run the full suite with:
```bash
python -m pytest
```

---

## 🚀 Entry Points

| Role | Command |
|------|---------|
| Play or create adventures | `python -m src.acs.ui.ide` |
| Quick launcher menu | `./quickstart.sh` |
| Scripted engine usage | `python acs_engine_enhanced.py` |

Refer to `START_HERE.md` for onboarding and setup guidance.

---

## 📊 Useful Counts (February 2025)

- 1 curated flagship adventure bundled under `adventures/`.
- 6 built-in gameplay systems available in `src/acs/systems/`.
- 5 primary test modules ensuring parser and system coverage.
- 22 documentation files organized across four role-based categories.
- 1 reference plugin illustrating optional extension points.

---

## 🗺️ Navigation Tips

1. New to the project? Open `START_HERE.md`.
2. Want to play or build immediately? Launch `python -m src.acs.ui.ide`.
3. Looking to contribute code? Read `docs/developer-guides/CONTRIBUTING.md`.
4. Exploring APIs? Start with `docs/reference/TECHNICAL_REFERENCE.md`.
5. Need a structural refresher? Return to this document or `FILE_ORGANIZATION_SUMMARY.md`.

---

**Organizational Scheme**: User-facing content (adventures, user guides) is separated from engine code (`src/`), optional extensions (`plugins/`), and governance (`docs/project-management/`). This clarity keeps the SagaCraft engine approachable for players, creators, and contributors alike.

Copyright © 2025 Honey Badger Universe | MIT License
