# SagaCraft — File Organization

## Overview

SagaCraft now uses a lean, role-focused directory layout. Documentation, configuration, plugins, and the flagship adventure sit alongside the modular Python package that powers the engine and IDE.

## Directory Structure

```
SagaCraft/
├── adventures/          # Bundled flagship adventure JSON (colossal_storyworks_showcase.json)
├── archive/             # Legacy engine code and historical assets
├── config/              # Engine defaults and plugin configuration
├── docs/                # User guides, developer docs, references, project planning
├── plugins/             # Optional plugin modules (e.g., achievements)
├── src/acs/             # SagaCraft Python package
│   ├── core/            # Engine, parser, state, event bus, services
│   ├── data/            # Configuration and data access services
│   ├── systems/         # Gameplay systems (combat, journal, tutorial, etc.)
│   ├── tools/           # Author utilities (command helpers, modding support)
│   └── ui/              # Tk-based IDE and accessibility modules
├── tests/               # Pytest suites covering parser and systems
├── acs_engine_enhanced.py  # Enhanced engine module leveraged by the IDE play tab
├── quickstart.sh           # Menu-based launcher script
├── README.md               # Project overview
└── START_HERE.md           # Onboarding checklist
```

## Import Paths

The Python package namespace remains `src.acs` for compatibility with existing tools. Use the modern imports:

```python
from acs.core.engine import GameEngine
from acs.core.parser import NaturalLanguageParser
```

## Running the Application

```bash
./quickstart.sh           # Guided launcher
python -m src.acs.ui.ide  # Launch the SagaCraft IDE
```

## Benefits of the Current Layout

1. **Brand-aligned structure** – All documentation and assets reference SagaCraft.
2. **Clear separation of concerns** – Engine code, data services, systems, and UI live in dedicated modules.
3. **Testability** – Pytest suites live at the top level and mirror package structure.
4. **Extensibility** – Plugins and configuration overrides sit outside the core package.
5. **Discoverability** – Documentation is grouped by audience, and the flagship adventure is easy to locate.

## Migration Notes

- Legacy scripts, examples, and multiple bundled adventures were retired in favor of the comprehensive `colossal_storyworks_showcase.json`.
- All legacy branding references have been updated to SagaCraft across documentation and code comments.
- Module paths continue to use `src.acs` until a future namespace migration is scheduled.

## Next Steps

- If you plan to distribute the engine as a package, add standard packaging metadata (e.g., `pyproject.toml`).
- Keep the documentation indices (`docs/README.md`, `PROJECT_STRUCTURE.md`) in sync when new modules or guides are added.

