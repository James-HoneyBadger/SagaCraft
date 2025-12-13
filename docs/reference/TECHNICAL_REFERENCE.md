# SagaCraft - Technical Reference

**Version 3.0.0**  
**Copyright © 2025 Honey Badger Universe**  
**License: MIT**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Systems](#core-systems)
3. [Natural Language Parser](#natural-language-parser)
4. [Game Engine](#game-engine)
5. [Plugin System](#plugin-system)
6. [Data Structures](#data-structures)
7. [API Reference](#api-reference)
8. [Extension Guide](#extension-guide)
9. [Performance](#performance)
10. [Security](#security)

---

## Architecture Overview

### System Design

SagaCraft follows a modular, event-driven architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│                    (python -m src.acs.ui.ide)                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Command Parser                          │
│                  (acs_parser.py)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Game Engine                            │
│              (acs_engine_enhanced.py)                            │
├─────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  Combat   │  │   NPC    │  │   Environment    │    │
│  │  System   │  │ Context  │  │     System       │    │
│  └───────────┘  └──────────┘  └──────────────────┘    │
│                                                          │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ Journal   │  │  Achieve │  │   Modding        │    │
│  │  System   │  │   ments  │  │   Support        │    │
│  └───────────┘  └──────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Data Layer                              │
│        (JSON files, Save system, Config)                │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
SagaCraft/
├── src/acs/                # Application source code (package)
│   ├── core/               # Engine, parser, state, event infrastructure
│   ├── data/               # Config/data services (IO, persistence)
│   ├── systems/            # Gameplay systems (combat, achievements, journal...)
│   ├── tools/              # Author tooling (commands, modding)
│   └── ui/                 # Tkinter IDE and accessibility modules
│
├── adventures/             # Adventure JSON bundles
├── config/                 # Engine and plugin configuration
├── docs/                   # Documentation (guides, references)
├── plugins/                # Optional plugin packages
├── saves/                  # Player save data
├── scripts/                # Maintenance/util scripts
├── tests/                  # Pytest suites (parser + integration)
├── quickstart.sh           # Menu-based launcher
├── acs_engine_enhanced.py  # Legacy CLI engine entry point
├── LICENSE                 # MIT License
└── README.md               # Project overview
```

### Design Principles

1. **Modularity** - Independent, reusable components
2. **Extensibility** - Plugin system for custom features
3. **Separation of Concerns** - Clear component boundaries
4. **Event-Driven** - Loose coupling via event bus
5. **Data-Driven** - Configuration over code
6. **Test-Driven** - Comprehensive test coverage

---

## Core Systems

### Engine Core (`acs_engine_enhanced.py`)

#### GameEngine Class

Main orchestrator for game logic.

```python
class GameEngine:
    def __init__(self, adventure_file):
        """Initialize game engine with adventure data."""
        self.adventure = self.load_adventure(adventure_file)
        self.state = GameState()
        self.parser = CommandParser()
        self.systems = self.initialize_systems()
        
    def process_command(self, command_text):
        """Parse and execute player command."""
        parsed = self.parser.parse_sentence(command_text)
        result = self.execute_action(parsed)
        self.update_systems()
        return result
        
    def update_systems(self):
        """Update all game systems."""
        for system in self.systems:
            system.update(self.state)
```

**Key Methods**:

- `load_adventure(file)` - Load adventure from JSON
- `process_command(text)` - Handle player input
- `execute_action(parsed)` - Execute parsed command
- `update_systems()` - Update all subsystems
- `save_game(slot)` - Save current state
- `load_game(slot)` - Restore saved state

#### GameState Class

Manages current game state.

```python
class GameState:
    def __init__(self):
        self.player = Player()
        self.current_room = None
        self.inventory = []
        self.npcs = {}
        self.quests = []
        self.flags = {}
        self.time = 0
        
    def get_room(self, room_id):
        """Get room by ID."""
        return self.rooms.get(room_id)
        
    def add_to_inventory(self, item):
        """Add item to player inventory."""
        self.inventory.append(item)
        
    def set_flag(self, flag_name, value):
        """Set game flag for tracking state."""
        self.flags[flag_name] = value
```

**State Components**:

- `player` - Player stats, health, position
- `current_room` - Current location
- `inventory` - Player items
- `npcs` - All NPC states
- `quests` - Active quest progress
- `flags` - Custom state variables
- `time` - Game time counter

### Command System

#### Command Flow

```
User Input → Parser → Validator → Executor → Systems → Output
```

1. **Input** - Raw text from player
2. **Parse** - Convert to structured command
3. **Validate** - Check if action is valid
4. **Execute** - Perform action
5. **Update** - Update game systems
6. **Output** - Return result message

#### Command Structure

```python
{
    "action": "move",           # Base action
    "direction": "north",       # Direction for movement
    "target": "sword",          # Target object/NPC
    "modifier": "carefully"     # Optional modifier
}
```

### Event System

#### EventBus

Decoupled communication between systems.

```python
class EventBus:
    def __init__(self):
        self.listeners = {}
        
    def subscribe(self, event_type, handler):
        """Register event handler."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(handler)
        
    def publish(self, event_type, data):
        """Publish event to all subscribers."""
        if event_type in self.listeners:
            for handler in self.listeners[event_type]:
                handler(data)
```

**Event Types**:

- `room_enter` - Player enters room
- `room_exit` - Player exits room
- `item_pickup` - Item added to inventory
- `item_drop` - Item removed from inventory
- `item_use` - Item activated
- `combat_start` - Combat initiated
- `combat_end` - Combat finished
- `npc_talk` - Dialogue initiated
- `quest_start` - Quest accepted
- `quest_complete` - Quest finished
- `achievement_unlock` - Achievement earned

**Usage Example**:

```python
# Subscribe to event
event_bus.subscribe('item_pickup', on_item_pickup)

# Handler function
def on_item_pickup(data):
    item = data['item']
    if item.name == 'magic_sword':
        event_bus.publish('achievement_unlock', 
                         {'achievement': 'find_sword'})

# Publish event
event_bus.publish('item_pickup', {'item': sword})
```

---

## Natural Language Parser

### Parser Architecture

The parser (`acs_parser.py`) converts natural language to structured commands.

#### Parse Flow

```
Input → Normalize → Tokenize → Pattern Match → Verb Map → Output
```

### Core Components

#### 1. Verb Mapping

Maps synonyms to canonical verbs:

```python
verb_map = {
    "move": ["go", "walk", "travel", "head", "move"],
    "look": ["look", "examine", "inspect", "check", "observe"],
    "get": ["get", "take", "grab", "pick up", "acquire"],
    "drop": ["drop", "discard", "put down", "leave"],
    "attack": ["attack", "hit", "strike", "fight", "kill"],
    # ... more mappings
}
```

**Benefits**:
- Players can use natural language
- Consistent internal representation
- Easy to extend with more synonyms

#### 2. Direction Normalization

Handles directional commands:

```python
def normalize_direction(direction):
    """Convert direction variations to canonical form."""
    direction_map = {
        'n': 'north', 'north': 'north',
        's': 'south', 'south': 'south',
        'e': 'east', 'east': 'east',
        'w': 'west', 'west': 'west',
        'ne': 'northeast', 'nw': 'northwest',
        'se': 'southeast', 'sw': 'southwest',
        'u': 'up', 'up': 'up',
        'd': 'down', 'down': 'down',
        'in': 'in', 'inside': 'in',
        'out': 'out', 'outside': 'out'
    }
    return direction_map.get(direction.lower(), direction)
```

#### 3. Multi-Word Verb Detection

Handles phrases like "pick up", "put down":

```python
multi_word_verbs = [
    "pick up", "put down", "look at", "talk to",
    "give to", "step into"
]

def detect_multi_word_verb(words):
    """Check if first words form a multi-word verb."""
    for verb in multi_word_verbs:
        verb_words = verb.split()
        if words[:len(verb_words)] == verb_words:
            return verb, words[len(verb_words):]
    return None, words
```

#### 4. Pattern Matching

Special patterns for common queries:

```python
# Question patterns
if re.match(r"^what (am i|do i) (carrying|have|hold)", sentence):
    return {"action": "inventory"}
    
if re.match(r"^where (am i|is)", sentence):
    return {"action": "look"}
    
if re.match(r"^who (is|are)", sentence):
    return {"action": "look", "target": extract_target(sentence)}
```

### Parse Algorithm

```python
def parse_sentence(sentence):
    """
    Parse natural language command into structured action.
    
    Args:
        sentence (str): Raw player input
        
    Returns:
        dict: Parsed command structure
    """
    # 1. Normalize
    sentence = sentence.lower().strip()
    
    # 2. Special patterns (questions)
    if match := check_question_patterns(sentence):
        return match
    
    # 3. Tokenize
    words = sentence.split()
    
    # 4. Extract verb
    verb, rest = detect_multi_word_verb(words)
    if not verb:
        verb = words[0]
        rest = words[1:]
    
    # 5. Normalize verb
    verb = normalize_verb(verb)
    
    # 6. Handle special cases
    if verb == "go":
        # "go north" → move
        direction = normalize_direction(rest[0] if rest else "")
        return {"action": "move", "direction": direction}
    
    # 7. Extract target/parameters
    target = " ".join(rest) if rest else ""
    
    # 8. Return structured command
    return {
        "action": verb,
        "target": target
    }
```

### Edge Case Handling

#### Ambiguous Verbs

Some verbs have multiple meanings:

**Problem**: "leave" can mean "exit" or "drop"

**Solution**: Context-aware resolution

```python
if verb == "leave":
    if rest:
        # "leave the sword" → drop
        return {"action": "drop", "target": rest}
    else:
        # "leave" → exit
        return {"action": "exit"}
```

#### Party Commands

**Pattern**: "tell [npc] to [action]"

```python
if verb in ["tell", "order", "command"]:
    if " to " in rest:
        npc, action = rest.split(" to ", 1)
        return {
            "action": "party_order",
            "target": npc.strip(),
            "command": action.strip()
        }
```

#### Directional Movement

**Special cases**: "go in", "go out"

```python
if verb == "go":
    if rest in ["in", "inside"]:
        return {"action": "move", "direction": "in"}
    elif rest in ["out", "outside"]:
        return {"action": "move", "direction": "out"}
```

### Parser Performance

**Metrics** (from test suite):
- **Success Rate**: 99.2% (128/129 tests)
- **Average Parse Time**: <1ms
- **Memory Usage**: ~100KB

**Optimization Techniques**:
1. Pre-compiled regex patterns
2. Cached verb mappings
3. Early returns for common patterns
4. Minimal string operations

---

## Game Engine

### Core Loop

```python
def game_loop():
    """Main game loop."""
    running = True
    
    while running:
        # 1. Display current state
        display_room(current_room)
        
        # 2. Get player input
        command = get_input("> ")
        
        # 3. Parse command
        parsed = parser.parse_sentence(command)
        
        # 4. Execute action
        result = execute_action(parsed)
        
        # 5. Display result
        print(result)
        
        # 6. Update systems
        update_all_systems()
        
        # 7. Check end conditions
        if check_game_over():
            running = False
```

### Action Execution

```python
def execute_action(parsed_command):
    """
    Execute parsed command.
    
    Args:
        parsed_command (dict): Structured command
        
    Returns:
        str: Result message
    """
    action = parsed_command.get('action')
    target = parsed_command.get('target', '')
    
    # Dispatch to appropriate handler
    handlers = {
        'move': handle_movement,
        'look': handle_look,
        'get': handle_get,
        'drop': handle_drop,
        'attack': handle_combat,
        # ... more handlers
    }
    
    handler = handlers.get(action, handle_unknown)
    return handler(parsed_command)
```

### Movement System

```python
def handle_movement(command):
    """Handle player movement."""
    direction = command.get('direction')
    
    # Check if exit exists
    if direction not in current_room['exits']:
        return "You can't go that way."
    
    # Get destination
    next_room_id = current_room['exits'][direction]
    
    # Trigger exit events
    event_bus.publish('room_exit', {
        'from': current_room['id'],
        'direction': direction
    })
    
    # Move player
    current_room = get_room(next_room_id)
    
    # Trigger enter events
    event_bus.publish('room_enter', {
        'to': current_room['id'],
        'from_direction': opposite_direction(direction)
    })
    
    # Return description
    return describe_room(current_room)
```

### Inventory System

```python
def handle_get(command):
    """Handle picking up items."""
    item_name = command['target']
    
    # Find item in room
    item = find_item_in_room(current_room, item_name)
    if not item:
        return f"There's no {item_name} here."
    
    # Check if takeable
    if not item.get('takeable', True):
        return f"You can't take the {item_name}."
    
    # Check weight limit
    current_weight = sum(i['weight'] for i in inventory)
    if current_weight + item['weight'] > max_weight:
        return "You're carrying too much!"
    
    # Add to inventory
    inventory.append(item)
    current_room['items'].remove(item)
    
    # Trigger event
    event_bus.publish('item_pickup', {'item': item})
    
    return f"You take the {item_name}."
```

### Combat System

```python
def handle_combat(command):
    """Handle combat action."""
    target_name = command['target']
    
    # Find NPC
    npc = find_npc_in_room(current_room, target_name)
    if not npc:
        return f"There's no {target_name} here to attack."
    
    # Check if already hostile
    if npc['friendliness'] > 0:
        npc['friendliness'] = -100
        return f"The {npc['name']} turns hostile!"
    
    # Calculate damage
    player_damage = calculate_damage(player, npc)
    npc_damage = calculate_damage(npc, player)
    
    # Apply damage
    npc['health'] -= player_damage
    player['health'] -= npc_damage
    
    result = f"You hit the {npc['name']} for {player_damage} damage.\n"
    result += f"The {npc['name']} hits you for {npc_damage} damage."
    
    # Check death
    if npc['health'] <= 0:
        result += f"\nThe {npc['name']} is defeated!"
        handle_npc_death(npc)
        event_bus.publish('combat_end', {'victor': 'player'})
    
    if player['health'] <= 0:
        result += "\nYou have been defeated!"
        event_bus.publish('combat_end', {'victor': 'npc'})
        game_over()
    
    return result
```

---

## Plugin System

### Plugin Architecture

Plugins extend functionality without modifying core code.

#### Base Plugin Class

```python
class Plugin:
    """Base class for all plugins."""
    
    def __init__(self, engine):
        self.engine = engine
        self.name = "Base Plugin"
        self.version = "1.0"
        self.enabled = True
        
    def initialize(self):
        """Called when plugin is loaded."""
        pass
        
    def on_command(self, command, result):
        """Called after command execution."""
        return result
        
    def on_room_enter(self, room):
        """Called when player enters room."""
        pass
        
    def on_combat(self, attacker, defender):
        """Called during combat."""
        pass
        
    def shutdown(self):
        """Called when plugin is unloaded."""
        pass
```

#### Creating a Plugin

Example: Weather plugin

```python
from plugins.base import Plugin
import random

class WeatherPlugin(Plugin):
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "Weather System"
        self.version = "1.0"
        self.current_weather = "clear"
        
    def initialize(self):
        """Set up weather system."""
        self.engine.event_bus.subscribe('room_enter', 
                                        self.on_room_enter)
        self.weather_types = ["clear", "rainy", "foggy", "stormy"]
        
    def on_room_enter(self, data):
        """Change weather randomly."""
        if random.random() < 0.1:  # 10% chance
            old = self.current_weather
            self.current_weather = random.choice(self.weather_types)
            if old != self.current_weather:
                self.notify_weather_change()
                
    def notify_weather_change(self):
        """Tell player about weather."""
        messages = {
            "rainy": "It begins to rain.",
            "foggy": "A thick fog rolls in.",
            "stormy": "Thunder rumbles in the distance.",
            "clear": "The weather clears up."
        }
        print(messages[self.current_weather])
```

#### Plugin Manager

```python
class PluginManager:
    def __init__(self, engine):
        self.engine = engine
        self.plugins = {}
        
    def load_plugin(self, plugin_path):
        """Load plugin from file."""
        module = importlib.import_module(plugin_path)
        plugin_class = module.Plugin
        plugin = plugin_class(self.engine)
        
        self.plugins[plugin.name] = plugin
        plugin.initialize()
        
        return plugin
        
    def unload_plugin(self, plugin_name):
        """Unload plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].shutdown()
            del self.plugins[plugin_name]
            
    def call_hook(self, hook_name, *args, **kwargs):
        """Call hook on all plugins."""
        for plugin in self.plugins.values():
            if plugin.enabled:
                method = getattr(plugin, hook_name, None)
                if method:
                    method(*args, **kwargs)
```

---

## Data Structures

### Adventure File Format

```json
{
  "metadata": {
    "title": "The Dark Tower",
    "author": "Honey Badger",
    "version": "1.0",
    "difficulty": "medium",
    "description": "A classic dungeon crawl"
  },
  
  "settings": {
    "starting_room": "entrance",
    "starting_gold": 100,
    "max_inventory_weight": 50,
    "combat_enabled": true,
    "permadeath": false
  },
  
  "rooms": {
    "entrance": {
      "name": "Cave Entrance",
      "description": "A dark cave opening...",
      "exits": {
        "north": "hall",
        "east": "chamber"
      },
      "items": ["torch"],
      "npcs": ["guard"],
      "light_level": 5,
      "temperature": 15
    }
  },
  
  "items": {
    "torch": {
      "name": "torch",
      "description": "A wooden torch",
      "weight": 1,
      "value": 5,
      "takeable": true,
      "provides_light": true
    },
    "sword": {
      "name": "iron sword",
      "description": "A basic iron sword",
      "weight": 3,
      "value": 50,
      "damage": 5,
      "takeable": true,
      "wearable": true,
      "slot": "weapon"
    }
  },
  
  "npcs": {
    "guard": {
      "name": "guard",
      "display_name": "Castle Guard",
      "description": "A stern guard in armor",
      "health": 50,
      "max_health": 50,
      "damage": 5,
      "armor": 3,
      "friendliness": 0,
      "ai_type": "guard",
      "dialogue": [
        "State your business!",
        "The castle is restricted."
      ],
      "inventory": ["key"]
    }
  },
  
  "quests": [
    {
      "id": "find_sword",
      "name": "The Lost Sword",
      "description": "Find the legendary sword",
      "objectives": [
        "Enter the ruins",
        "Defeat the guardian",
        "Retrieve the sword"
      ],
      "rewards": {
        "gold": 100,
        "experience": 50
      }
    }
  ]
}
```

### Save File Format

```json
{
  "metadata": {
    "adventure": "dark_tower",
    "save_time": "2025-11-20T10:30:00",
    "play_time": 3600,
    "version": "2.0"
  },
  
  "player": {
    "name": "Hero",
    "health": 75,
    "max_health": 100,
    "gold": 250,
    "experience": 150,
    "level": 2,
    "current_room": "hall"
  },
  
  "inventory": [
    {"item_id": "sword", "equipped": true},
    {"item_id": "torch", "equipped": false}
  ],
  
  "quest_progress": {
    "find_sword": {
      "status": "active",
      "objectives_complete": [0, 1]
    }
  },
  
  "world_state": {
    "rooms": {
      "entrance": {
        "items": [],
        "npcs": []
      }
    },
    "npcs": {
      "guard": {
        "health": 30,
        "friendliness": -50,
        "alive": true
      }
    }
  },
  
  "flags": {
    "gate_opened": true,
    "met_wizard": true
  }
}
```

---

## API Reference

### Parser API

```python
# Parse command
parsed = parse_sentence("go north")
# Returns: {"action": "move", "direction": "north"}

# Normalize verb
verb = normalize_verb("examine")
# Returns: "look"

# Normalize direction
direction = normalize_direction("n")
# Returns: "north"
```

### Engine API

```python
# Initialize engine
engine = GameEngine("adventure.json")

# Process command
result = engine.process_command("look")

# Save game
engine.save_game("slot1")

# Load game
engine.load_game("slot1")

# Get current state
state = engine.get_state()
```

### Event API

```python
# Subscribe to event
event_bus.subscribe('item_pickup', handler)

# Publish event
event_bus.publish('item_pickup', {'item': item})

# Unsubscribe
event_bus.unsubscribe('item_pickup', handler)
```

---

## Extension Guide

### Adding New Commands

1. **Add verb to parser**:
```python
verb_map["dance"] = ["dance", "boogie", "jig"]
```

2. **Create handler**:
```python
def handle_dance(command):
    return "You dance joyfully!"
```

3. **Register handler**:
```python
command_handlers["dance"] = handle_dance
```

### Creating Custom NPCs

```python
class CustomNPC(BaseNPC):
    def __init__(self, data):
        super().__init__(data)
        self.mood = "neutral"
        
    def on_talk(self, player):
        if self.mood == "happy":
            return "Hello, friend!"
        else:
            return "I'm busy."
            
    def on_gift_received(self, item):
        if item.value > 50:
            self.mood = "happy"
            self.friendliness += 25
```

### Adding Environmental Effects

```python
class ToxicGasEffect(EnvironmentEffect):
    def __init__(self):
        self.name = "toxic_gas"
        self.damage_per_turn = 5
        
    def apply(self, player, room):
        if room.get('has_gas'):
            player.health -= self.damage_per_turn
            return "The toxic gas burns your lungs!"
        return None
```

---

## Performance

### Optimization Tips

1. **Cache frequently accessed data**
2. **Use efficient data structures** (dicts, sets)
3. **Minimize string operations**
4. **Pre-compile regex patterns**
5. **Profile before optimizing**

### Benchmarks

- **Command parsing**: <1ms
- **Room rendering**: <5ms
- **Combat calculation**: <10ms
- **Save/Load**: <50ms

---

## Security

### Input Validation

All user input is sanitized:
- Length limits
- Character whitelist
- No code execution
- Safe JSON parsing

### File Safety

- Sandboxed file access
- No arbitrary file operations
- Save files validated
- Adventure files checked

---

**End of Technical Reference**

For user documentation, see `docs/USER_MANUAL.md`  
For plugin development, see `docs/PLUGIN_GUIDE.md`  
For contributing, see `docs/CONTRIBUTING.md`
