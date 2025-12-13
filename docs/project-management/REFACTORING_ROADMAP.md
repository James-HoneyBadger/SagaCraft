# Refactoring Roadmap

## Mission

Transform SagaCraft from a monolithic architecture to a fully modular, plugin-based system that is easy to maintain, extend, and adapt for future features.

## Progress Overview

**Overall Completion: 70%** 🔄

- ✅ Core Architecture: 100%
- ✅ Service Layer: 100%
- ✅ Documentation: 100%
- 🔄 Plugin Migration: 10%
- ⏳ UI Refactoring: 0%
- ⏳ Testing: 0%
- ⏳ Compatibility: 0%

## Phase 1: Foundation ✅ COMPLETE

**Status:** 100% complete
**Time:** ~4 hours (completed)

### Deliverables (All Complete)

- ✅ `core/` package
  - ✅ `engine.py` - Main orchestrator
  - ✅ `event_bus.py` - Event system
  - ✅ `game_state.py` - State management
  - ✅ `base_plugin.py` - Plugin interface
  - ✅ `services.py` - Service registry

- ✅ `utils/` package
  - ✅ `config_service.py` - Configuration
  - ✅ `io_service.py` - File I/O
  - ✅ `data_service.py` - Entity management

- ✅ Documentation
  - ✅ `ARCHITECTURE.md`
  - ✅ `PLUGIN_GUIDE.md`
  - ✅ `REFACTORING_SUMMARY.md`
  - ✅ `demo_architecture.py`

## Phase 2: Plugin Migration 🔄 IN PROGRESS

**Status:** 10% complete (1/10 systems)
**Estimated Time:** 6-8 hours
**Priority:** HIGH

### System Conversion Checklist

#### Completed
- ✅ Achievement System → `systems/achievements_plugin.py`

#### In Progress
- 🔄 Combat System → `systems/combat_plugin.py`

#### Pending
- ⏳ NPC Context → `systems/npc_plugin.py`
- ⏳ Environment → `systems/environment_plugin.py`
- ⏳ Commands → `systems/commands_plugin.py`
- ⏳ Party → `systems/party_plugin.py`
- ⏳ Journal → `systems/journal_plugin.py`
- ⏳ Tutorial → `systems/tutorial_plugin.py`
- ⏳ Modding → `systems/modding_plugin.py`
- ⏳ Accessibility → `systems/accessibility_plugin.py`

### Conversion Process (Per System)

1. **Create Plugin File** (30 min)
   - Copy from `systems/achievements_plugin.py` template
   - Update metadata
   - Import original classes

2. **Implement Event Handlers** (45 min)
   - Identify what events to subscribe to
   - Convert direct calls to event handlers
   - Emit events for other plugins

3. **Add State Management** (30 min)
   - Load/save from GameState
   - Use plugin_data storage
   - Handle configuration

4. **Test Integration** (15 min)
   - Run with demo
   - Verify events work
   - Check state persistence

**Estimated Time Per System:** ~2 hours
**Total for 9 Systems:** ~18 hours

### Quick Start Guide for Each System

```python
# Template for each plugin
from core import BasePlugin, PluginMetadata, PluginPriority
from acs_SYSTEM_NAME import OriginalClass  # Reuse existing

class SystemNamePlugin(BasePlugin):
    def __init__(self):
        metadata = PluginMetadata(
            name="system_name",
            version="2.0",
            priority=PluginPriority.NORMAL,  # Adjust as needed
        )
        super().__init__(metadata)
        self.system = None
        
    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        self.system = OriginalClass()  # Wrap existing
        self._load_from_state()
        
    def get_event_subscriptions(self):
        return {
            'game.move': self.on_move,
            # Add other events
        }
        
    def on_move(self, event):
        # Handle event
        pass
        
    def _load_from_state(self):
        # Load plugin data
        pass
        
    def _save_to_state(self):
        # Save plugin data
        pass
```

## Phase 3: Compatibility Layer ⏳ PENDING

**Status:** 0% complete
**Estimated Time:** 3-4 hours
**Priority:** HIGH

### Goal

Create a wrapper that makes the new engine compatible with the old `acs_engine_enhanced.py` API so existing code doesn't break.

### Tasks

1. **Create Wrapper** (2 hours)
   - `compat/legacy_engine.py`
   - Implements old `Engine` class interface
   - Auto-registers all plugins
   - Translates old method calls to events

2. **Update Entry Points** (1 hour)
   - `python -m src.acs.ui.ide` - Primary launch target
   - Retire the standalone CLI path and funnel testing through the IDE play tab
   - Ensure any helper scripts delegate to the IDE module

3. **Test Backward Compatibility** (1 hour)
   - Load existing adventures
   - Run test suite
   - Verify all features work

### Example Wrapper

```python
# compat/legacy_engine.py
from core import Engine
from systems import *  # All plugins

class LegacyEngine:
    """Wrapper for old Engine API"""
    
    def __init__(self):
        self.engine = Engine()
        # Auto-register all plugins
        self._register_all_plugins()
        
    def move(self, direction):
        # Translate to event
        self.engine.event_bus.publish('command.input', {
            'command': f'go {direction}'
        })
        
    # ... implement all old methods
```

## Phase 4: IDE Refactoring ⏳ PENDING

**Status:** 0% complete
**Estimated Time:** 8-10 hours
**Priority:** MEDIUM

### Goal

Refactor `python -m src.acs.ui.ide` (1450 lines) into MVC pattern with reusable components.

### Structure

```
ui/
├── __init__.py
├── ide/
│   ├── __init__.py
│   ├── model.py          # Data management
│   ├── view.py           # UI components
│   ├── controller.py     # Logic/events
│   └── components/       # Reusable widgets
│       ├── code_editor.py
│       ├── entity_list.py
│       ├── property_panel.py
│       └── game_terminal.py
└── themes/
    ├── dark.json
    └── light.json
```

### Tasks

1. **Extract Model** (2 hours)
   - Adventure data management
   - Validation logic
   - State management

2. **Create View Components** (3 hours)
   - Reusable widgets
   - Layout managers
   - Theme support

3. **Implement Controller** (2 hours)
   - Event handlers
   - Engine integration
   - Command processing

4. **Update Main IDE** (2 hours)
   - Use new components
   - Wire MVC together
   - Test all features

## Phase 5: Testing ⏳ PENDING

**Status:** 0% complete
**Estimated Time:** 6-8 hours
**Priority:** HIGH

### Test Coverage Goals

- Core: 90%+
- Plugins: 80%+
- Services: 85%+
- Integration: 70%+

### Test Structure

```
tests/
├── unit/
│   ├── test_engine.py
│   ├── test_event_bus.py
│   ├── test_game_state.py
│   ├── test_base_plugin.py
│   └── test_services.py
├── integration/
│   ├── test_plugin_system.py
│   ├── test_event_flow.py
│   └── test_save_load.py
├── plugins/
│   ├── test_achievements.py
│   ├── test_combat.py
│   └── ...
└── fixtures/
    ├── sample_adventure.json
    └── test_config.json
```

### Tasks

1. **Unit Tests** (3 hours)
   - Test each core component
   - Mock dependencies
   - Edge cases

2. **Integration Tests** (2 hours)
   - Plugin interactions
   - Event flow
   - State management

3. **Plugin Tests** (2 hours)
   - Test each plugin
   - Event handling
   - State persistence

4. **CI/CD Setup** (1 hour)
   - GitHub Actions
   - Auto-run tests
   - Coverage reports

## Phase 6: Documentation & Polish ⏳ PENDING

**Status:** 50% complete (foundation done)
**Estimated Time:** 4-6 hours
**Priority:** MEDIUM

### Tasks

1. **API Documentation** (2 hours)
   - Auto-generate from docstrings
   - Sphinx or MkDocs
   - Host online

2. **Tutorial Videos** (2 hours)
   - Quick start
   - Plugin development
   - IDE usage

3. **Example Projects** (1 hour)
   - Simple adventure
   - Complex adventure
   - Custom plugin

4. **CONTRIBUTING.md** (1 hour)
   - Contribution guidelines
   - Code style
   - PR process

## Phase 7: Advanced Features ⏳ FUTURE

**Status:** 0% complete
**Estimated Time:** 12+ hours
**Priority:** LOW

### Features

1. **Plugin Marketplace** (4 hours)
   - Discover plugins
   - Install/uninstall
   - Version management

2. **Hot Reload** (3 hours)
   - Reload plugins without restart
   - Live code updates
   - Development mode

3. **Visual Plugin Editor** (4 hours)
   - Drag-drop plugin creation
   - Visual event connections
   - Code generation

4. **Remote Debugging** (2 hours)
   - Debug protocol
   - Event inspector
   - State viewer

## Timeline

### Week 1 (Current)
- ✅ Day 1-2: Core architecture (DONE)
- 🔄 Day 3-4: Plugin migration (IN PROGRESS)
- ⏳ Day 5-6: Compatibility layer
- ⏳ Day 7: Testing framework

### Week 2
- ⏳ Day 1-2: Complete plugin migration
- ⏳ Day 3-5: IDE refactoring
- ⏳ Day 6-7: Integration testing

### Week 3
- ⏳ Day 1-2: Bug fixes
- ⏳ Day 3-4: Documentation
- ⏳ Day 5-6: Performance optimization
- ⏳ Day 7: Release preparation

### Week 4+
- ⏳ Advanced features
- ⏳ Community feedback
- ⏳ Continuous improvement

## Success Metrics

### Quantitative

- ✅ Core modules created: 8/8 (100%)
- 🔄 Systems migrated to plugins: 1/10 (10%)
- ⏳ Test coverage: 0% (Target: 80%)
- ⏳ Documentation coverage: 50% (Target: 100%)
- ⏳ Performance: TBD (Target: <5% overhead)

### Qualitative

- ✅ Code is more modular
- ✅ Easier to understand
- ✅ Better separation of concerns
- ⏳ Backward compatible
- ⏳ Well documented
- ⏳ Fully tested

## Risk Mitigation

### Risks

1. **Breaking Changes**
   - Mitigation: Compatibility layer
   - Status: Planned

2. **Performance Overhead**
   - Mitigation: Profiling, optimization
   - Status: To be tested

3. **Incomplete Migration**
   - Mitigation: Phase approach, wrapper
   - Status: On track

4. **Community Adoption**
   - Mitigation: Documentation, examples
   - Status: In progress

## Next Actions

### Immediate (Today)

1. ✅ Create core architecture
2. ✅ Write documentation
3. ✅ Build demo
4. 🔄 Start plugin migration

### This Week

1. Complete all 10 plugin migrations
2. Create compatibility wrapper
3. Update IDE to use new engine
4. Write comprehensive tests

### This Month

1. Full test coverage
2. Performance optimization
3. Complete documentation
4. Community release

## Resources

- **Code:** `/home/james/SagaCraft/`
- **Docs:** `ARCHITECTURE.md`, `PLUGIN_GUIDE.md`
- **Demo:** `demo_architecture.py`
- **Original:** `acs_*.py` files (reference)

## Contact

For questions or contributions, see `CONTRIBUTING.md` (coming soon).

---

**Last Updated:** November 19, 2025
**Current Phase:** 2 - Plugin Migration
**Next Milestone:** Complete 10 plugin conversions
