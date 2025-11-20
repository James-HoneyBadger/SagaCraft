# 📁 Project Structure

**Adventure Construction System v2.0**
Last Updated: January 2025

---

## 🗂️ Directory Organization

```
HB_Adventure_Games/
├── adventures/           # Adventure game JSON files
├── archive/             # Historical/archived code
├── config/              # Configuration files
│   ├── engine.json      # Engine settings
│   └── plugins/         # Plugin configurations
├── docs/                # Documentation (organized by category)
│   ├── user-guides/     # Player and creator documentation
│   ├── developer-guides/ # Contributor and plugin development
│   ├── reference/       # Technical specs and API docs
│   ├── project-management/ # Planning and organization docs
│   ├── legacy/          # Historical/completed status docs
│   └── README.md        # Documentation navigation hub
├── examples/            # Example code and tutorials
├── plugins/             # Plugin modules
├── saves/               # Player save games
├── src/                 # Source code
│   └── acs/             # Main package
│       ├── core/        # Core engine functionality
│       ├── data/        # Data models and schemas
│       ├── systems/     # Game systems (combat, NPCs, etc.)
│       ├── tools/       # Development tools
│       └── ui/          # User interface modules
├── tests/               # Test suites
│   ├── integration/     # Integration tests
│   └── unit/            # Unit tests
├── acs_engine_enhanced.py # Main engine entry point
├── README.md            # Project overview
└── START_HERE.md        # Quick start guide
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
- `EXAMPLE_GAMEPLAY.md` - Sample gameplay sessions

### **docs/developer-guides/**
Documentation for contributors and plugin developers:
- `CONTRIBUTING.md` - How to contribute to the project
- `PLUGIN_GUIDE.md` - Creating custom plugins
- `DSK_CONVERSION_GUIDE.md` - Converting classic .DSK files
- `ENHANCED_PARSER_GUIDE.md` - Parser internals and extensions
- `ENHANCED_FEATURES_GUIDE.md` - Advanced feature implementation
- `INFORM7_INTEGRATION.md` - Inform7 compatibility

### **docs/reference/**
Technical specifications and API documentation:
- `TECHNICAL_REFERENCE.md` - Architecture, APIs, internals
- `COMMANDS.md` - All 30 commands with examples
- `ARCHITECTURE.md` - System architecture overview
- `MODULAR_ARCHITECTURE.md` - Module structure and design
- `DOCUMENTATION_INDEX.md` - Master documentation index
- `DOCUMENTATION_REVIEW.md` - Documentation audit results
- `QUICK_REFERENCE.txt` - Quick command reference
- `DSK_CONVERTER_QUICKREF.txt` - Converter quick reference

### **docs/project-management/**
Planning, organization, and status documents:
- `PROJECT_SUMMARY.md` - Project overview and goals
- `PROJECT_ORGANIZATION.md` - Organization and structure
- `FILE_ORGANIZATION.md` - File structure documentation
- `ENHANCEMENT_PLAN.md` - Planned enhancements
- `REFACTORING_ROADMAP.md` - Refactoring plans
- `REFACTORING_SUMMARY.md` - Refactoring status

### **docs/legacy/**
Historical and completed status documents:
- `COMPLETION_SUMMARY.txt` - Project completion status
- `DOCUMENTATION_STATUS.txt` - Documentation review status
- `IMPLEMENTATION_COMPLETE.md` - Implementation milestones
- `NEW_ENHANCEMENTS.md` - Enhancement history
- `ORGANIZATION_COMPLETE.md` - Organization completion
- `PARSER_IMPROVEMENTS.md` - Parser enhancement history
- `PARSER_TEST_REPORT.md` - Parser testing results
- `PROJECT_COMPLETE.txt` - Project completion notes
- Plus backup files (.bak) and old indexes

---

## 🎮 Adventures Library

### **adventures/**
Complete adventure game files (JSON format):

| Adventure | Rooms | Items | NPCs | Quests | Description |
|-----------|-------|-------|------|--------|-------------|
| `mind_forever_voyaging.json` | 16 | 8 | 6 | 6 | Explore a simulated city's future |
| `mindwheel.json` | 23 | 13 | 9 | 5 | Surreal psychological dreamscapes |
| `planetfall.json` | 18 | 10 | 3 | 4 | Sci-fi space station survival |
| `leather_goddesses.json` | 17 | 8 | 4 | 3 | Pulp adventure parody |
| `hitchhikers_guide.json` | 23 | 8 | 6 | 5 | Absurdist sci-fi comedy |
| `zork.json` | 33 | 13 | 3 | 3 | Classic underground adventure |
| `colossal_cave.json` | 39 | 10 | 3 | 1 | The original text adventure |
| `hunt_the_wumpus.json` | 20 | 1 | 1 | 1 | Cave hunting game |
| `ballyhoo.json` | 18 | 9 | 4 | 2 | Murder mystery under the big top |
| `doctor_who_temporal_paradox.json` | 31 | 17 | 7 | 6 | Time-traveling adventure |

**Total Content**: 238 rooms, 96 items, 46 NPCs, 36 quests

See `ADVENTURE_LIBRARY.md` for detailed descriptions.

---

## 🔧 Source Code Organization

### **src/acs/core/**
Core engine functionality:
- Game loop and state management
- Command processing
- Save/load system
- Error handling

### **src/acs/data/**
Data models and schemas:
- JSON schemas for adventures
- Data validation
- Type definitions

### **src/acs/systems/**
Game systems:
- Combat system
- NPC interaction
- Quest management
- Achievement tracking

### **src/acs/tools/**
Development and conversion tools:
- DSK file converter
- Adventure validator
- Debug utilities

### **src/acs/ui/**
User interface modules:
- Text-based UI
- Graphical IDE
- Theme engine (5 themes)
- Input/output formatting

---

## 🚀 Quick Start

Launch the IDE:
```bash
python3 -m src.acs.ui.ide
```

All scripts are Python modules using `python3 -m` syntax.

---

## 🧪 Testing

### **tests/**
Comprehensive test suite:

| Directory/File | Purpose |
|----------------|---------|
| `unit/` | Unit tests for individual modules |
| `integration/` | Integration tests for systems |
| `test_engine.py` | Engine functionality tests |
| `test_parser_detailed.py` | Parser accuracy tests (99.2%) |
| `test_all_commands.py` | Command coverage tests |
| `test_all_systems.py` | System integration tests |
| `test_converter.py` | DSK converter tests |

---

## 🔌 Plugins

### **plugins/**
Extension modules:
- `achievements_plugin.py` - Achievement system

### **config/plugins/**
Plugin configuration files

---

## 📦 Configuration

### **config/**
System configuration:
- `engine.json` - Engine settings (theme, auto-save, etc.)
- `plugins/` - Plugin configurations

---

## 💾 Save Games

### **saves/**
Player save game files (auto-saved and manual)

---

## 📜 Archive

### **archive/**
Historical code and old game files:
- `old_core_engine.py` - Original engine version
- `archive/` - Legacy code and historical files

---

## 🎯 Entry Points

### For Players:
```bash
python3 -m src.acs.ui.ide  # Play or create in IDE
```

### For Creators:
```bash
python3 -m src.acs.ui.ide  # Create adventures in GUI
```

### For Developers:
```bash
python3 acs_engine_enhanced.py  # Run engine directly
```

---

## 📋 Key Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `START_HERE.md` | New user orientation |
| `ADVENTURE_LIBRARY.md` | Catalog of all adventures |
| `PROJECT_STRUCTURE.md` | This file - organization guide |
| `LICENSE` | MIT License |
| `acs_engine_enhanced.py` | Main engine entry point |
| `quickstart.sh` | Quick start script |

---

## 📊 Project Statistics

- **Total Documentation Files**: 35+
- **Total Adventures**: 10 complete games
- **Total Rooms**: 238
- **Total Items**: 96
- **Total NPCs**: 46
- **Total Quests**: 36
- **Parser Accuracy**: 99.2%
- **Commands**: 30 natural language commands
- **Themes**: 5 visual themes

---

## 🗺️ Navigation Tips

1. **New to the project?** → `START_HERE.md`
2. **Want to play?** → `docs/user-guides/QUICKSTART.md`
3. **Want to create?** → `docs/user-guides/USER_MANUAL.md`
4. **Want to contribute?** → `docs/developer-guides/CONTRIBUTING.md`
5. **Need API docs?** → `docs/reference/TECHNICAL_REFERENCE.md`
6. **All documentation?** → `docs/README.md`

---

**Organizational Scheme**: Files are organized by function and user role, with clear separation between user-facing content (adventures, documentation), development content (source, tests), and configuration (config, plugins).

Copyright © 2025 Honey Badger Universe | MIT License
