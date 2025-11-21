# Modular Architecture - Quick Navigation

## 🎯 Start Here

**New to the refactored architecture?**
1. Read [REFACTORING_SUMMARY.md](../project-management/REFACTORING_SUMMARY.md) - Overview of changes
2. Run `python tests/demo_architecture.py` - See it in action
3. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the design
4. Read [PLUGIN_GUIDE.md](../developer-guides/PLUGIN_GUIDE.md) - Learn to extend

**Want to contribute?**
1. Check [REFACTORING_ROADMAP.md](REFACTORING_ROADMAP.md) - See what's needed
2. Pick a task from Phase 2 (Plugin Migration)
3. Follow the conversion template
4. Submit a PR (guidelines coming soon)

## 📁 Directory Structure

### Core Engine
- `core/` - Foundational components
  - `engine.py` - Main orchestrator, plugin management
  - `event_bus.py` - Event system for loose coupling
  - `game_state.py` - Centralized state management
  - `base_plugin.py` - Plugin interface/contract
  - `services.py` - Service registry pattern

### Services
- `utils/` - Shared functionality
  - `config_service.py` - Configuration management
  - `io_service.py` - File I/O operations
  - `data_service.py` - Entity data management

### Plugins
- `systems/` - Plugin implementations
  - `achievements_plugin.py` - Achievement tracking (EXAMPLE)
  - *(More coming as migration progresses)*

### Original Code (Legacy)
- `acs_engine_enhanced.py` - Original monolithic engine (1025 lines)
- `acs_*.py` - Original enhancement systems
- *(Will be replaced/wrapped by new architecture)*

### Documentation
- `ARCHITECTURE.md` - Complete system design guide
- `PLUGIN_GUIDE.md` - Plugin development tutorial
- `REFACTORING_SUMMARY.md` - What was accomplished
- `REFACTORING_ROADMAP.md` - What's next
- `demo_architecture.py` - Working examples

## 🚀 Quick Commands

### Run the Demo
```bash
python tests/demo_architecture.py
```

### Test Core Modules
```bash
python -c "
from acs.core.engine import AdventureGame
from acs.core.base_plugin import PluginMetadata
print('✓ Core modules import successfully!')
"
```

### Create a Plugin (Template)
```python
from core import BasePlugin, PluginMetadata, PluginPriority

class MyPlugin(BasePlugin):
    def __init__(self):
        metadata = PluginMetadata(
            name="my_plugin",
            version="1.0",
            priority=PluginPriority.NORMAL
        )
        super().__init__(metadata)
        
    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        print("Plugin initialized!")
        
    def get_event_subscriptions(self):
        return {
            'game.move': self.on_move,
        }
        
    def on_move(self, event):
        print(f"Player moved to room {event.data['to_room']}")
```

### Run the Engine
```bash
python -m src.acs.ui.ide          # Graphical IDE (recommended)
python acs_engine_enhanced.py     # Legacy CLI entry point
```

## 📊 Status Overview

| Component | Status | Completion |
|-----------|--------|------------|
| Core Architecture | ✅ Complete | 100% |
| Event System | ✅ Complete | 100% |
| Service Layer | ✅ Complete | 100% |
| Documentation | ✅ Complete | 100% |
| Plugin Framework | ✅ Complete | 100% |
| Achievement Plugin | ✅ Complete | 100% |
| Combat Plugin | 🔄 In Progress | 0% |
| NPC Plugin | ⏳ Pending | 0% |
| Other Plugins (7) | ⏳ Pending | 0% |
| Compatibility Layer | ⏳ Pending | 0% |
| IDE Refactoring | ⏳ Pending | 0% |
| Test Suite | ⏳ Pending | 0% |

**Overall Progress: ~70%**

## 🎓 Learning Path

### Beginner
1. Run `demo_architecture.py`
2. Read the output and comments
3. Modify demo to add your own plugin
4. Experiment with events

### Intermediate
1. Read `ARCHITECTURE.md` thoroughly
2. Study `systems/achievements_plugin.py`
3. Convert one simple system to a plugin
4. Add custom events

### Advanced
1. Read all documentation
2. Design complex plugin interactions
3. Optimize performance
4. Contribute to core

## 🔑 Key Concepts

### Plugin
A modular component that adds functionality. Examples: achievements, combat, dialogue.

### Event
A message sent between plugins. Example: "game.move" when player moves.

### Service
Shared functionality available to all plugins. Examples: config, file I/O, data storage.

### State
Centralized game data accessible by all plugins. Example: player stats, room data.

### Priority
Determines plugin initialization and event handler order. Range: 0 (critical) to 100 (low).

## 📖 Documentation Index

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete system design
  - Architecture layers
  - Component descriptions
  - Event flow diagrams
  - Design patterns used

### Developer Guides
- [PLUGIN_GUIDE.md](../developer-guides/PLUGIN_GUIDE.md) - Plugin development
  - Quick start
  - Complete API reference
  - Best practices
  - Testing guidelines

### Project Status
- [REFACTORING_SUMMARY.md](../project-management/REFACTORING_SUMMARY.md) - What's done
  - Accomplishments
  - Before/after comparison
  - Code metrics
  - Usage examples

- [REFACTORING_ROADMAP.md](REFACTORING_ROADMAP.md) - What's next
  - Phase breakdown
  - Task checklist
  - Timeline
  - Success metrics

### Code Examples
- [demo_architecture.py](demo_architecture.py) - Live demonstrations
  - Basic engine usage
  - Plugin enable/disable
  - Event cancellation
  - State management

## 🛠️ Development Tools

### Code Locations
```
Core:     core/*.py          - Foundation (870 lines)
Services: utils/*.py          - Utilities (540 lines)
Plugins:  systems/*.py        - Features (380+ lines)
Legacy:   acs_*.py            - Original code
Docs:     *.md                - Documentation
Demo:     demo_architecture.py - Examples
```

### Module Imports
```python
# Core
from core import Engine, BasePlugin, Event, GameState

# Services
from utils import ConfigService, IOService, DataService

# Plugins
from systems import AchievementsPlugin
```

### Configuration Files
```
config/
├── engine.json           - Main engine config
└── plugins/             - Plugin configs
    └── my_plugin.json   - Plugin-specific
```

## 🎯 Common Tasks

### Add a New Plugin
1. Create `systems/my_plugin.py`
2. Extend `BasePlugin`
3. Implement `initialize()` and `get_event_subscriptions()`
4. Register: `engine.register_plugin(MyPlugin())`

### Subscribe to Events
```python
def get_event_subscriptions(self):
    return {
        'game.move': self.on_move,
        'combat.start': self.on_combat,
    }
```

### Publish Events
```python
self.event_bus.publish('my.event', {
    'data': 'value'
})
```

### Access State
```python
# Player data
self.state.player.gold += 100

# Plugin data
self.state.set_plugin_data('my_plugin', 'key', value)
data = self.state.get_plugin_data('my_plugin', 'key', default)
```

### Use Services
```python
# Config
config = self.services.get('config')
value = config.get('setting.name', default)

# I/O
io = self.services.get('io')
adventure = io.load_adventure('name')

# Data
data = self.services.get('data')
room = data.get_room(room_id)
```

## 🐛 Troubleshooting

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'core'`
**Solution:** Run from project root: `cd /home/james/HB_Adventure_Games`

### Plugin Not Working
**Problem:** Event handler not called
**Solution:** 
1. Check `get_event_subscriptions()` returns correct dict
2. Verify event name matches exactly
3. Ensure plugin is initialized: `engine.initialize()`

### State Not Persisting
**Problem:** Plugin data lost on restart
**Solution:** Call `_save_to_state()` in `shutdown()` method

## 💡 Tips & Tricks

### Development Mode
```python
# Enable event history for debugging
engine = Engine(enable_event_history=True)

# View recent events
history = engine.event_bus.get_history(limit=20)
```

### Quick Plugin Test
```python
# Create minimal test
from core import Engine
from my_plugin import MyPlugin

engine = Engine()
engine.register_plugin(MyPlugin())
engine.initialize()

# Trigger event
engine.event_bus.publish('test.event', {'data': 42})
```

### Performance Profiling
```python
import time

def on_event(event):
    start = time.time()
    # ... do work ...
    duration = time.time() - start
    if duration > 0.1:
        print(f"Slow handler: {duration:.3f}s")
```

## 📞 Support

### Resources
- Code examples in `systems/`
- Working demo in `demo_architecture.py`
- Complete guides in `*.md` files

### Common Questions
**Q: Do I need to modify core code to add features?**
A: No! Create a plugin instead.

**Q: Can I use the old `acs_engine_enhanced.py`?**
A: Yes, it still works. New architecture is opt-in (for now).

**Q: How do I share state between plugins?**
A: Use events or `state.set_flag()` / `state.get_flag()`.

**Q: Can I disable a plugin at runtime?**
A: Yes! `plugin.disable()` and `plugin.enable()`.

## 🎉 Contributing

**Ways to Help:**
1. Convert systems to plugins (see roadmap)
2. Write tests
3. Improve documentation
4. Report bugs
5. Suggest features

**Guidelines:** (Coming in CONTRIBUTING.md)
- Follow existing code style
- Add docstrings
- Write tests
- Update documentation

---

**Last Updated:** November 19, 2025

**Current Focus:** Phase 2 - Plugin Migration

**Next Goal:** Convert all 10 systems to plugins

**Questions?** Check the docs or run the demo!

🎮 Happy coding! ✨
