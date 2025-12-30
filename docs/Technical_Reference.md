# SagaCraft Technical Reference

## Architecture and Implementation Details

This document provides comprehensive technical information about the SagaCraft engine, including architecture, APIs, data structures, and implementation details for developers and advanced users.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Systems](#core-systems)
3. [Data Structures](#data-structures)
4. [API Reference](#api-reference)
5. [File Formats](#file-formats)
6. [Performance Considerations](#performance-considerations)
7. [Extensibility](#extensibility)
8. [Debugging and Development](#debugging-and-development)

## Architecture Overview

### Component Architecture

SagaCraft follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   sagacraft_    │    │   sagacraft_    │    │   sagacraft_    │
│     player      │    │    ide_tui      │    │    ide_gui      │
│                 │    │                 │    │                 │
│ • CLI Interface │    │ • Terminal UI   │    │ • Graphical UI  │
│ • Command Input │    │ • Text Editor   │    │ • Visual Editor │
│ • Game Loop     │    │ • File Mgmt     │    │ • Drag & Drop   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   sagacraft_    │
                    │       rs        │
                    │                 │
                    │ • Core Engine   │
                    │ • Game State    │
                    │ • Systems       │
                    │ • Data Models   │
                    └─────────────────┘
```

### Core Principles

1. **Modularity**: Each component has a single responsibility
2. **Performance**: Rust's zero-cost abstractions and memory safety
3. **Extensibility**: Plugin system for custom mechanics
4. **Data-Driven**: JSON-based adventure format
5. **Cross-Platform**: Works on Linux, macOS, and Windows

## Core Systems

### Game State Management

The `GameState` struct manages all game data:

```rust
pub struct GameState {
    pub player: Player,
    pub current_room_id: i32,
    pub rooms: HashMap<i32, Room>,
    pub items: HashMap<i32, Item>,
    pub monsters: HashMap<i32, Monster>,
    pub game_over: bool,
    pub turn_count: i32,
}
```

### System Architecture

SagaCraft uses an Entity-Component-System (ECS) inspired approach:

```rust
pub trait System {
    fn update(&mut self, game_state: &mut GameState, command: &Command) -> Vec<String>;
    fn get_name(&self) -> &str;
}
```

Built-in systems include:
- `BasicWorldSystem`: Room navigation and description
- `InventorySystem`: Item management
- `CombatSystem`: Turn-based combat
- `QuestSystem`: Objective tracking

### Command Processing

Commands are parsed and dispatched through a central processor:

```rust
pub enum Command {
    Help,
    Look,
    Inventory,
    Move(Direction),
    Take(String),
    Drop(String),
    Use(String),
    Say(String),
    Quit,
    Unknown(String),
}
```

## Data Structures

### Adventure Structure

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Adventure {
    pub id: String,
    pub title: String,
    pub start_room: String,
    pub rooms: Vec<AdventureRoom>,
    #[serde(default)]
    pub player_start_inventory: Vec<AdventureItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdventureRoom {
    pub id: String,
    pub title: String,
    pub description: String,
    #[serde(default)]
    pub exits: HashMap<String, String>,
    #[serde(default)]
    pub items: Vec<AdventureItem>,
}
```

### Player and Characters

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Player {
    pub name: String,
    pub hardiness: i32,
    pub agility: i32,
    pub current_health: Option<i32>,
    pub inventory: Vec<i32>, // Item IDs
    pub location: i32,       // Room ID
    pub gold: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Monster {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub room_id: i32,
    pub hardiness: i32,
    pub agility: i32,
    pub friendliness: MonsterStatus,
    pub courage: i32,
    pub weapon_id: Option<i32>,
    pub armor_worn: i32,
    pub gold: i32,
    pub is_dead: bool,
    pub current_health: Option<i32>,
}
```

### Items and Equipment

```rust
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ItemType {
    Weapon, Armor, Treasure, Readable, Edible, Drinkable, Container, Normal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub item_type: ItemType,
    pub weight: i32,
    pub value: i32,
    pub is_weapon: bool,
    pub weapon_type: i32,
    pub weapon_dice: i32,
    pub weapon_sides: i32,
    pub is_armor: bool,
    pub armor_value: i32,
    pub is_takeable: bool,
    pub is_wearable: bool,
    pub location: i32,
}
```

## API Reference

### Core Engine API

#### AdventureGame

The main game controller:

```rust
pub struct AdventureGame {
    game_state: GameState,
    systems: Vec<Box<dyn System>>,
    adventure: Option<Adventure>,
}

impl AdventureGame {
    pub fn new(adventure_path: Option<String>) -> Self;
    pub fn load_adventure(&mut self) -> Result<(), Box<dyn std::error::Error>>;
    pub fn add_system(&mut self, system: Box<dyn System>);
    pub fn process_command(&mut self, input: &str) -> Vec<String>;
    pub fn look(&mut self) -> Vec<String>;
    pub fn is_game_over(&self) -> bool;
}
```

#### System Trait

Interface for game systems:

```rust
pub trait System {
    fn update(&mut self, game_state: &mut GameState, command: &Command) -> Vec<String>;
    fn get_name(&self) -> &str;
    fn init(&mut self, _game_state: &mut GameState) {}
    fn cleanup(&mut self, _game_state: &mut GameState) {}
}
```

### Command API

#### Command Parsing

```rust
impl Command {
    pub fn parse(input: &str) -> Result<Self, ParseError>;
    pub fn is_movement(&self) -> bool;
    pub fn requires_target(&self) -> bool;
}
```

#### Direction Enum

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Direction {
    North, South, East, West,
}

impl Direction {
    pub fn from_str(s: &str) -> Option<Self>;
    pub fn opposite(&self) -> Self;
}
```

### File I/O API

#### Adventure Loading

```rust
impl Adventure {
    pub fn load_from_file(path: &Path) -> Result<Self, AdventureError>;
    pub fn save_to_file(&self, path: &Path) -> Result<(), AdventureError>;
    pub fn validate(&self) -> Result<(), AdventureError>;
}
```

#### Save/Load System

```rust
pub struct SaveManager {
    save_directory: PathBuf,
}

impl SaveManager {
    pub fn new() -> Self;
    pub fn save_game(&self, game_state: &GameState, slot: &str) -> Result<(), Box<dyn std::error::Error>>;
    pub fn load_game(&self, slot: &str) -> Result<GameState, Box<dyn std::error::Error>>;
    pub fn list_saves(&self) -> Result<Vec<String>, Box<dyn std::error::Error>>;
}
```

## File Formats

### Adventure JSON Format

Complete adventure specification:

```json
{
  "$schema": "https://raw.githubusercontent.com/James-HoneyBadger/SagaCraft/main/docs/adventure.schema.json",
  "id": "example_adventure",
  "title": "Example Adventure",
  "description": "A sample adventure for demonstration",
  "author": "Game Designer",
  "version": "1.0.0",
  "start_room": "entrance",
  "player_start_inventory": [
    {
      "id": "backpack",
      "name": "Leather Backpack",
      "description": "A sturdy leather backpack for carrying items."
    }
  ],
  "rooms": [
    {
      "id": "entrance",
      "title": "Castle Entrance",
      "description": "You stand before the massive oak doors of an ancient castle. The stone walls loom high above you, and you can hear the distant sound of waves crashing against the cliffs below.",
      "exits": {
        "north": "great_hall",
        "south": "courtyard"
      },
      "items": [
        {
          "id": "iron_key",
          "name": "Iron Key",
          "description": "A heavy iron key, cold to the touch."
        }
      ],
      "npcs": [
        {
          "id": 1,
          "name": "Gate Guard",
          "description": "A stern-looking guard in chain mail armor."
        }
      ]
    }
  ],
  "items": [
    {
      "id": 100,
      "name": "Rusty Sword",
      "description": "An old sword with a dull blade. It has seen better days.",
      "item_type": "Weapon",
      "weight": 3,
      "value": 10,
      "is_weapon": true,
      "weapon_type": 5,
      "weapon_dice": 1,
      "weapon_sides": 8
    }
  ],
  "monsters": [
    {
      "id": 200,
      "name": "Goblin Warrior",
      "description": "A small but fierce goblin armed with a crude spear.",
      "room_id": 2,
      "hardiness": 6,
      "agility": 8,
      "friendliness": "Hostile",
      "courage": 5,
      "weapon_id": 300,
      "armor_worn": 0,
      "gold": 5
    }
  ],
  "quests": [
    {
      "id": "main_quest",
      "title": "Escape the Castle",
      "description": "Find a way out of the castle and return to freedom.",
      "objectives": [
        {
          "id": "find_key",
          "description": "Locate the key to the main gate",
          "type": "item",
          "target": "master_key"
        },
        {
          "id": "unlock_gate",
          "description": "Use the key to unlock the main gate",
          "type": "location",
          "target": "main_gate"
        }
      ],
      "reward": {
        "gold": 100,
        "experience": 50
      }
    }
  ]
}
```

### Save Game Format

```json
{
  "version": "1.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "adventure_id": "example_adventure",
  "game_state": {
    "player": {
      "name": "Hero",
      "hardiness": 12,
      "agility": 10,
      "current_health": 12,
      "inventory": [100, 101],
      "location": 1,
      "gold": 25
    },
    "current_room_id": 1,
    "rooms": {...},
    "items": {...},
    "monsters": {...},
    "game_over": false,
    "turn_count": 45
  },
  "active_quests": ["main_quest"],
  "completed_quests": []
}
```

## Performance Considerations

### Memory Management

- **Zero-copy parsing**: JSON data is parsed once and reused
- **Arena allocation**: Game objects use ID-based lookup for efficiency
- **Lazy loading**: Large assets loaded on demand

### CPU Optimization

- **Command caching**: Frequently used commands are cached
- **Incremental updates**: Only changed state is processed
- **Async I/O**: File operations don't block the game loop

### Benchmarks

Typical performance metrics:
- **Adventure loading**: < 100ms for 100-room adventures
- **Command processing**: < 1ms per command
- **Memory usage**: ~50MB for large adventures
- **Save/load time**: < 50ms for typical game states

## Extensibility

### Custom Systems

Create custom game mechanics:

```rust
pub struct CustomSystem {
    custom_data: HashMap<String, String>,
}

impl System for CustomSystem {
    fn update(&mut self, game_state: &mut GameState, command: &Command) -> Vec<String> {
        match command {
            Command::CustomCommand(data) => {
                // Custom logic here
                vec!["Custom action performed!".to_string()]
            }
            _ => vec![],
        }
    }

    fn get_name(&self) -> &str {
        "Custom System"
    }
}
```

### Plugin Architecture

```rust
pub trait Plugin {
    fn init(&mut self, game: &mut AdventureGame) -> Result<(), Box<dyn std::error::Error>>;
    fn get_systems(&self) -> Vec<Box<dyn System>>;
    fn get_commands(&self) -> Vec<String>;
}

pub struct PluginManager {
    plugins: Vec<Box<dyn Plugin>>,
}

impl PluginManager {
    pub fn load_plugin(&mut self, path: &Path) -> Result<(), Box<dyn std::error::Error>>;
    pub fn init_plugins(&mut self, game: &mut AdventureGame) -> Result<(), Box<dyn std::error::Error>>;
}
```

### Event System

```rust
#[derive(Debug, Clone)]
pub enum GameEvent {
    PlayerMoved { from: i32, to: i32 },
    ItemTaken { item_id: i32 },
    CombatStarted { monster_id: i32 },
    QuestCompleted { quest_id: String },
    Custom { event_type: String, data: serde_json::Value },
}

pub struct EventBus {
    listeners: HashMap<String, Vec<Box<dyn Fn(&GameEvent)>>>,
}

impl EventBus {
    pub fn subscribe(&mut self, event_type: &str, callback: Box<dyn Fn(&GameEvent)>);
    pub fn publish(&self, event: GameEvent);
}
```

## Debugging and Development

### Logging

SagaCraft uses the `tracing` crate for logging:

```rust
use tracing::{info, warn, error, debug};

// Enable debug logging
RUST_LOG=debug cargo run --bin sagacraft_player
```

### Debug Commands

Built-in debug commands (only in debug builds):

```
debug show_state    - Display current game state
debug teleport <room_id>  - Teleport to room
debug give_item <item_id> - Add item to inventory
debug kill_monster <id>   - Remove monster
debug show_quests         - Display quest status
```

### Testing

Comprehensive test suite:

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_combat_system

# Run with coverage
cargo tarpaulin

# Integration tests
cargo test --test integration
```

### Profiling

Performance profiling tools:

```bash
# CPU profiling
cargo flamegraph --bin sagacraft_player

# Memory profiling
cargo build --release
valgrind ./target/release/sagacraft_player
```

### Development Tools

- **VS Code Extensions**: Rust Analyzer, CodeLLDB
- **Cargo Tools**: cargo-expand, cargo-tree, cargo-outdated
- **Documentation**: `cargo doc --open`
- **Formatting**: `cargo fmt`
- **Linting**: `cargo clippy`

## Error Handling

### Error Types

```rust
#[derive(Debug)]
pub enum SagaCraftError {
    Io(std::io::Error),
    Json(serde_json::Error),
    Validation(String),
    GameLogic(String),
    PluginError(String),
}

impl std::error::Error for SagaCraftError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            SagaCraftError::Io(e) => Some(e),
            SagaCraftError::Json(e) => Some(e),
            _ => None,
        }
    }
}
```

### Error Recovery

- **Graceful degradation**: Continue with partial functionality
- **Save state preservation**: Don't lose progress on errors
- **User-friendly messages**: Clear error descriptions
- **Logging**: Detailed error information for developers

## Configuration

### Engine Configuration

```toml
# sagacraft.toml
[engine]
max_rooms = 1000
max_items = 5000
max_monsters = 500
save_directory = "saves/"
log_level = "info"

[ui]
enable_colors = true
show_timestamps = false
command_history_size = 100

[gameplay]
auto_save = true
auto_save_interval = 300  # seconds
difficulty_modifier = 1.0
```

### Adventure Configuration

```json
{
  "config": {
    "allow_save": true,
    "allow_load": true,
    "time_limit": null,
    "difficulty": "normal",
    "custom_commands": ["cast", "pray", "search"],
    "plugins": ["weather_system", "magic_system"]
  }
}
```

## Security Considerations

### Input Validation

- **Command sanitization**: All input is validated and sanitized
- **Path traversal protection**: File paths are normalized and checked
- **JSON schema validation**: Adventure files must conform to schema

### Plugin Security

- **Sandboxing**: Plugins run in isolated environments
- **Permission system**: Plugins declare required capabilities
- **Code review**: Plugin marketplace with community review

### Data Integrity

- **Checksums**: Save files include integrity checks
- **Version compatibility**: Automatic migration for save files
- **Backup system**: Automatic backups before major operations

## Future Roadmap

### Planned Features

- **Multiplayer support**: Real-time collaborative adventures
- **3D environments**: Integration with 3D rendering engines
- **Voice synthesis**: Text-to-speech for accessibility
- **Mobile platforms**: iOS and Android support
- **Web deployment**: Browser-based adventures
- **Mod marketplace**: Community plugin ecosystem

### API Stability

- **Semantic versioning**: Major.Minor.Patch
- **Deprecation warnings**: Advance notice of breaking changes
- **Migration guides**: Tools to upgrade adventures and saves

---

This technical reference is continuously updated. For the latest information, check the [GitHub repository](https://github.com/James-HoneyBadger/SagaCraft) and join the developer community.