# Plugin Development Guide

## Introduction

This guide shows you how to create plugins for the SagaCraft engine. Plugins allow you to add new features, modify game behavior, and extend functionality without changing the core engine code.

## Quick Start

### Minimal Plugin Example

```python
from core import BasePlugin, PluginMetadata, PluginPriority

class HelloWorldPlugin(BasePlugin):
    def __init__(self):
        metadata = PluginMetadata(
            name="hello_world",
            version="1.0",
            description="A simple example plugin"
        )
        super().__init__(metadata)
        
    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        print("Hello World Plugin initialized!")
        
    def get_event_subscriptions(self):
        return {
            'game.start': self.on_game_start,
        }
        
    def on_game_start(self, event):
        print("Game started! Hello from the plugin!")
```

### Using the Plugin

```python
from core import Engine
from my_plugin import HelloWorldPlugin

engine = Engine()
engine.register_plugin(HelloWorldPlugin())
engine.initialize()
engine.run()
```

## Plugin Structure

### 1. Metadata

Every plugin must have metadata:

```python
from core import PluginMetadata, PluginPriority

metadata = PluginMetadata(
    name="my_plugin",              # Unique identifier
    version="1.0.0",                # Semantic versioning
    author="Your Name",             # Optional
    description="What it does",     # Optional
    dependencies=["other_plugin"],  # Optional
    priority=PluginPriority.NORMAL, # Execution order
    enabled=True                     # Start enabled
)
```

### 2. Priority Levels

```python
PluginPriority.CRITICAL = 0   # Core systems (state, I/O)
PluginPriority.HIGH = 10      # Game logic (combat, items)
PluginPriority.NORMAL = 50    # Features (achievements)
PluginPriority.LOW = 100      # UI/UX (tutorial, hints)
```

Priority determines:
- Initialization order (lower first)
- Event handler execution order
- Shutdown order (higher first)

### 3. Lifecycle Methods

```python
class MyPlugin(BasePlugin):
    def __init__(self):
        """Create plugin instance"""
        # Set up metadata
        # Initialize instance variables
        
    def initialize(self, state, event_bus, services):
        """Called once during engine initialization"""
        super().initialize(state, event_bus, services)
        # Access to state, events, and services now available
        # Load saved data
        # Set up internal state
        
    def on_enable(self):
        """Called when plugin is activated"""
        # Start background tasks
        # Register dynamic handlers
        
    def on_disable(self):
        """Called when plugin is deactivated"""
        # Stop background tasks
        # Save state
        
    def shutdown(self):
        """Called before engine stops"""
        # Final cleanup
        # Save data
        # Release resources
```

## Event System

### Subscribing to Events

```python
def get_event_subscriptions(self):
    return {
        'game.move': self.on_move,
        'combat.start': self.on_combat_start,
        'item.pickup': self.on_item_pickup,
        '*': self.on_any_event,  # Wildcard - all events
    }
```

### Event Handler

```python
def on_move(self, event):
    """Handle movement events"""
    # Access event data
    from_room = event.data.get('from_room')
    to_room = event.data['to_room']  # Required field
    player = event.data.get('player')
    
    # Cancel event (if cancellable)
    if some_condition:
        event.cancel()
        
    # Check if event was cancelled
    if event.is_cancelled():
        return
```

### Publishing Events

```python
def do_something(self):
    # Simple event
    self.event_bus.publish('my_plugin.action', {
        'foo': 'bar',
        'value': 42
    })
    
    # Cancellable event
    event = self.event_bus.publish(
        'my_plugin.validate',
        {'data': some_data},
        cancellable=True
    )
    
    if event.is_cancelled():
        print("Action was cancelled by another plugin")
        return False
```

## Common Event Names

### Game Events
- `engine.initialized` - Engine ready
- `game.start` - Game begins
- `game.shutdown` - Engine stopping
- `game.move` - Player moved
- `game.look` - Player examined room
- `game.save` - Game saved
- `game.load` - Game loaded

### Command Events
- `command.input` - Player entered command
- `command.unknown` - Command not recognized

### Combat Events
- `combat.start` - Combat initiated
- `combat.hit` - Attack landed
- `combat.miss` - Attack missed
- `combat.victory` - Player won
- `combat.defeat` - Player lost

### Item Events
- `item.pickup` - Item collected
- `item.drop` - Item dropped
- `item.use` - Item used
- `item.equip` - Item equipped

### NPC Events
- `npc.interaction` - Player talked to NPC
- `npc.dialogue.start` - Dialogue began
- `npc.dialogue.end` - Dialogue ended

## State Management

### Accessing Game State

```python
def on_move(self, event):
    # Access player data
    player = self.state.player
    player.gold += 10
    current_room = player.current_room
    
    # Access entities
    room = self.state.rooms.get(current_room)
    items = self.state.items
    monsters = self.state.monsters
    
    # Game phase
    if self.state.phase == GamePhase.COMBAT:
        print("In combat!")
```

### Plugin-Specific Data

```python
def initialize(self, state, event_bus, services):
    super().initialize(state, event_bus, services)
    
    # Load plugin data
    my_data = self.state.get_plugin_data('my_plugin', 'counter', 0)
    
def save_data(self):
    # Save plugin data
    self.state.set_plugin_data('my_plugin', 'counter', self.counter)
    self.state.set_plugin_data('my_plugin', 'items', self.special_items)
```

### Global Flags

```python
# Set flag
self.state.set_flag('dragon_defeated', True)

# Check flag
if self.state.get_flag('dragon_defeated'):
    print("Dragon is already defeated")
```

## Using Services

### Configuration Service

```python
def initialize(self, state, event_bus, services):
    super().initialize(state, event_bus, services)
    
    # Get config service
    config = services.get('config')
    
    # Read plugin config
    enabled = config.get_plugin_config('my_plugin', 'enabled', True)
    threshold = config.get_plugin_config('my_plugin', 'threshold', 10)
    
    # Write plugin config
    config.set_plugin_config('my_plugin', 'last_run', datetime.now())
```

### I/O Service

```python
def load_custom_data(self):
    io = self.services.get('io')
    
    # Load JSON file
    data = io.load_json(Path('my_data.json'))
    
    # Save JSON file
    io.save_json(Path('output.json'), {'result': 42})
    
    # Load adventure
    adventure = io.load_adventure('forest_quest')
    
    # Save game
    io.save_game('slot1', self.state.to_dict())
```

### Data Service

```python
def find_special_items(self):
    data = self.services.get('data')
    
    # Get specific entity
    room = data.get_room(5)
    item = data.get_item(10)
    
    # Query entities
    items_here = data.find_items_by_location(5)
    monsters_here = data.find_monsters_by_room(5)
    
    # Add custom entity
    data.add_entity('special_objects', 1, my_object)
```

## Configuration Files

Create `config/plugins/my_plugin.yaml`:

```yaml
enabled: true
settings:
  difficulty: normal
  max_value: 100
  features:
    - feature1
    - feature2
custom_data:
  some_key: some_value
```

Access in code:

```python
config = self.services.get('config')
difficulty = config.get_plugin_config('my_plugin', 'settings.difficulty')
max_val = config.get_plugin_config('my_plugin', 'settings.max_value')
```

## Example Plugins

### Achievement Tracker

```python
from core import BasePlugin, PluginMetadata, PluginPriority

class AchievementPlugin(BasePlugin):
    def __init__(self):
        metadata = PluginMetadata(
            name="achievements",
            version="1.0",
            priority=PluginPriority.NORMAL
        )
        super().__init__(metadata)
        self.achievements = {}
        self.unlocked = set()
        
    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        # Load from state
        self.unlocked = set(state.get_plugin_data(
            'achievements', 'unlocked', []
        ))
        
    def get_event_subscriptions(self):
        return {
            'game.move': self.check_movement_achievements,
            'combat.victory': self.check_combat_achievements,
        }
        
    def check_movement_achievements(self, event):
        if 'explorer' not in self.unlocked:
            rooms_visited = len(self.state.player.inventory)  # Example
            if rooms_visited >= 10:
                self.unlock_achievement('explorer')
                
    def unlock_achievement(self, ach_id):
        self.unlocked.add(ach_id)
        self.event_bus.publish('achievement.unlocked', {
            'achievement': ach_id
        })
        # Save to state
        self.state.set_plugin_data(
            'achievements', 'unlocked', list(self.unlocked)
        )
```

### Auto-Save Plugin

```python
class AutoSavePlugin(BasePlugin):
    def __init__(self):
        metadata = PluginMetadata(
            name="autosave",
            version="1.0",
            priority=PluginPriority.LOW
        )
        super().__init__(metadata)
        self.save_interval = 5
        self.turn_counter = 0
        
    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        config = services.get('config')
        self.save_interval = config.get_plugin_config(
            'autosave', 'interval', 5
        )
        
    def get_event_subscriptions(self):
        return {
            'game.move': self.on_turn,
            'combat.victory': self.on_turn,
        }
        
    def on_turn(self, event):
        self.turn_counter += 1
        if self.turn_counter >= self.save_interval:
            self.auto_save()
            self.turn_counter = 0
            
    def auto_save(self):
        io = self.services.get('io')
        io.save_game('autosave', self.state.to_dict())
        print("[Auto-saved]")
```

## Best Practices

### 1. Don't Modify Core State Directly
```python
# Bad
self.state.player.gold = 100

# Good
old_gold = self.state.player.gold
self.state.player.gold += 10
self.event_bus.publish('player.gold_changed', {
    'old': old_gold,
    'new': self.state.player.gold
})
```

### 2. Handle Missing Dependencies
```python
def initialize(self, state, event_bus, services):
    super().initialize(state, event_bus, services)
    
    config = services.get('config')
    if not config:
        self.logger.warning("Config service not available")
        return
```

### 3. Validate Event Data
```python
def on_move(self, event):
    to_room = event.data.get('to_room')
    if not to_room:
        self.logger.error("Move event missing 'to_room'")
        return
```

### 4. Save State on Disable
```python
def on_disable(self):
    self._save_to_state()
    
def shutdown(self):
    self._save_to_state()
```

### 5. Use Logging
```python
import logging

class MyPlugin(BasePlugin):
    def __init__(self):
        # ...
        self.logger = logging.getLogger(f'Plugin.{metadata.name}')
        
    def some_method(self):
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
```

## Testing Your Plugin

Create `tests/test_my_plugin.py`:

```python
import unittest
from core import Engine, GameState, EventBus, ServiceRegistry
from my_plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.state = GameState()
        self.event_bus = EventBus()
        self.services = ServiceRegistry()
        self.plugin = MyPlugin()
        self.plugin.initialize(self.state, self.event_bus, self.services)
        
    def test_initialization(self):
        self.assertTrue(self.plugin.is_initialized)
        
    def test_event_handling(self):
        self.event_bus.publish('game.move', {'to_room': 5})
        # Assert expected behavior
```

## Distribution

To share your plugin:

1. Package as a Python module
2. Include `config/plugins/your_plugin.yaml`
3. Document dependencies
4. Provide installation instructions

## Next Steps

- Study example plugins in `systems/`
- Read `ARCHITECTURE.md` for system design
- Check `core/` modules for API details
- Join the community for support

Happy plugin development!
