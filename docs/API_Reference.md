# SagaCraft API Reference

## Core Library API

This document provides comprehensive API documentation for the SagaCraft core library (`sagacraft_rs`). The API is designed to be modular, extensible, and easy to use for building text-based adventure games.

## Table of Contents

1. [Core Types](#core-types)
2. [Game State Management](#game-state-management)
3. [Command System](#command-system)
4. [System Architecture](#system-architecture)
5. [Adventure Format](#adventure-format)
6. [Error Handling](#error-handling)
7. [Serialization](#serialization)
8. [Examples](#examples)

## Core Types

### GameState

The central structure representing the current state of the game.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameState {
    pub player: Player,
    pub current_room: String,
    pub inventory: HashMap<String, Item>,
    pub flags: HashMap<String, bool>,
    pub variables: HashMap<String, i32>,
    pub quest_states: HashMap<String, QuestState>,
    pub game_time: DateTime<Utc>,
}
```

#### Methods

```rust
impl GameState {
    /// Creates a new game state with default values
    pub fn new() -> Self

    /// Creates a game state from a save file
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Self, GameError>

    /// Saves the game state to a file
    pub fn save_to_file<P: AsRef<Path>>(&self, path: P) -> Result<(), GameError>

    /// Gets a flag value, returns false if not set
    pub fn get_flag(&self, key: &str) -> bool

    /// Sets a flag value
    pub fn set_flag(&mut self, key: &str, value: bool)

    /// Gets a variable value, returns 0 if not set
    pub fn get_variable(&self, key: &str) -> i32

    /// Sets a variable value
    pub fn set_variable(&mut self, key: &str, value: i32)

    /// Adds an item to inventory
    pub fn add_item(&mut self, item: Item)

    /// Removes an item from inventory
    pub fn remove_item(&mut self, item_id: &str) -> Option<Item>

    /// Checks if player has an item
    pub fn has_item(&self, item_id: &str) -> bool
}
```

### Player

Represents the player character and their attributes.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Player {
    pub id: String,
    pub name: String,
    pub health: i32,
    pub max_health: i32,
    pub level: i32,
    pub experience: i32,
    pub stats: PlayerStats,
    pub equipment: HashMap<String, Item>,
}
```

#### Methods

```rust
impl Player {
    /// Creates a new player with default stats
    pub fn new(name: &str) -> Self

    /// Calculates the player's total damage from weapon and stats
    pub fn weapon_damage(&self) -> i32

    /// Calculates the player's total armor value
    pub fn armor_value(&self) -> i32

    /// Checks if the player is alive
    pub fn is_alive(&self) -> bool

    /// Applies damage to the player
    pub fn take_damage(&mut self, damage: i32)

    /// Heals the player
    pub fn heal(&mut self, amount: i32)

    /// Adds experience and handles level ups
    pub fn add_experience(&mut self, exp: i32) -> bool // returns true if leveled up

    /// Gets the experience needed for next level
    pub fn experience_to_next_level(&self) -> i32
}
```

### Item

Represents items in the game world.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub id: String,
    pub name: String,
    pub description: String,
    pub item_type: ItemType,
    pub properties: HashMap<String, String>,
    pub stats: ItemStats,
}
```

#### ItemType

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ItemType {
    Weapon,
    Armor,
    Consumable,
    Key,
    Quest,
    Miscellaneous,
}
```

#### ItemStats

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemStats {
    pub damage: i32,
    pub armor: i32,
    pub healing: i32,
    pub value: i32,
}
```

## Game State Management

### AdventureGame

The main game engine that coordinates all systems and manages game state.

```rust
pub struct AdventureGame {
    state: GameState,
    adventure: Option<Adventure>,
    systems: Vec<Box<dyn System>>,
    command_parser: CommandParser,
}
```

#### Methods

```rust
impl AdventureGame {
    /// Creates a new game instance
    pub fn new(adventure_path: Option<String>) -> Self

    /// Loads an adventure from a JSON file
    pub fn load_adventure(&mut self) -> Result<(), GameError>

    /// Adds a system to the game
    pub fn add_system(&mut self, system: Box<dyn System>)

    /// Processes a command and returns output lines
    pub fn process_command(&mut self, input: &str) -> Vec<String>

    /// Gets the current game state (read-only)
    pub fn get_state(&self) -> &GameState

    /// Gets mutable access to game state
    pub fn get_state_mut(&mut self) -> &mut GameState

    /// Saves the current game state
    pub fn save_game(&self, path: &str) -> Result<(), GameError>

    /// Loads a saved game state
    pub fn load_game(&mut self, path: &str) -> Result<(), GameError>

    /// Checks if the game is over
    pub fn is_game_over(&self) -> bool
}
```

## Command System

### Command

Represents a parsed command with its arguments.

```rust
#[derive(Debug, Clone)]
pub struct Command {
    pub verb: String,
    pub noun: Option<String>,
    pub preposition: Option<String>,
    pub object: Option<String>,
    pub raw_input: String,
}
```

### CommandParser

Parses text input into structured commands.

```rust
pub struct CommandParser {
    // Internal state for parsing
}
```

#### Methods

```rust
impl CommandParser {
    /// Creates a new command parser
    pub fn new() -> Self

    /// Parses input text into a command
    pub fn parse(&self, input: &str) -> Result<Command, ParseError>

    /// Gets available commands for autocomplete
    pub fn get_available_commands(&self) -> Vec<&str>

    /// Validates if a command is well-formed
    pub fn validate_command(&self, command: &Command) -> Result<(), ParseError>
}
```

### ParseError

```rust
#[derive(Debug, thiserror::Error)]
pub enum ParseError {
    #[error("Unknown command: {0}")]
    UnknownCommand(String),

    #[error("Invalid syntax: {0}")]
    InvalidSyntax(String),

    #[error("Missing required argument: {0}")]
    MissingArgument(String),
}
```

## System Architecture

### System Trait

The core trait that all game systems must implement.

```rust
pub trait System: Send + Sync {
    /// Gets the name of the system
    fn name(&self) -> &str;

    /// Initializes the system with the game state
    fn initialize(&mut self, game: &mut AdventureGame) -> Result<(), SystemError>;

    /// Processes a command and returns output
    fn process_command(&mut self, command: &Command, game: &mut AdventureGame) -> Option<Vec<String>>;

    /// Updates the system (called each game tick)
    fn update(&mut self, game: &mut AdventureGame, delta_time: f64);

    /// Gets the priority of this system (higher = processed first)
    fn priority(&self) -> i32 { 0 }

    /// Checks if this system can handle a command
    fn can_handle(&self, command: &Command) -> bool;
}
```

### Built-in Systems

#### BasicWorldSystem

Handles room navigation and basic world interactions.

```rust
pub struct BasicWorldSystem {
    // Internal state
}
```

**Commands handled:**
- `go <direction>` - Move to another room
- `look` - Describe current room
- `examine <object>` - Examine an object in the room

#### CombatSystem

Manages combat mechanics and turn-based battles.

```rust
pub struct CombatSystem {
    pub in_combat: bool,
    pub current_enemy: Option<String>,
}
```

**Commands handled:**
- `attack <target>` - Attack an enemy
- `defend` - Enter defensive stance
- `use <item>` - Use an item in combat
- `flee` - Attempt to flee from combat

#### InventorySystem

Manages player inventory and item interactions.

```rust
pub struct InventorySystem {
    // Internal state
}
```

**Commands handled:**
- `inventory` - Show current inventory
- `take <item>` - Pick up an item
- `drop <item>` - Drop an item
- `use <item>` - Use an item
- `equip <item>` - Equip an item

#### QuestSystem

Tracks quest progress and objectives.

```rust
pub struct QuestSystem {
    active_quests: HashMap<String, Quest>,
}
```

**Commands handled:**
- `quests` - Show active quests
- `quest <id>` - Show quest details
- `objective <id>` - Show objective details

## Adventure Format

### Adventure

The top-level structure for an adventure definition.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Adventure {
    pub metadata: AdventureMetadata,
    pub rooms: HashMap<String, Room>,
    pub items: HashMap<String, ItemTemplate>,
    pub characters: HashMap<String, Character>,
    pub quests: HashMap<String, Quest>,
    pub dialogues: HashMap<String, Dialogue>,
}
```

### Room

Represents a location in the game world.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Room {
    pub id: String,
    pub name: String,
    pub description: String,
    pub exits: HashMap<String, Exit>,
    pub items: Vec<String>, // Item IDs
    pub characters: Vec<String>, // Character IDs
    pub properties: HashMap<String, String>,
}
```

### Exit

Defines a connection between rooms.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Exit {
    pub to: String, // Target room ID
    pub description: Option<String>,
    pub locked: bool,
    pub key_item: Option<String>, // Required item ID to unlock
    pub hidden: bool,
}
```

### Quest

Represents a quest with objectives and rewards.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quest {
    pub id: String,
    pub title: String,
    pub description: String,
    pub objectives: Vec<Objective>,
    pub rewards: Vec<Reward>,
    pub prerequisites: Vec<String>, // Other quest IDs
}
```

### Objective

A single objective within a quest.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Objective {
    pub id: String,
    pub description: String,
    pub objective_type: ObjectiveType,
    pub target: String, // Target item, room, character, etc.
    pub count: i32, // How many times to complete
    pub completed: bool,
}
```

### ObjectiveType

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ObjectiveType {
    VisitRoom,
    CollectItem,
    DefeatEnemy,
    TalkToCharacter,
    UseItem,
    Custom(String),
}
```

## Error Handling

### GameError

The main error type for game operations.

```rust
#[derive(Debug, thiserror::Error)]
pub enum GameError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("JSON parsing error: {0}")]
    Json(#[from] serde_json::Error),

    #[error("Invalid adventure format: {0}")]
    InvalidAdventure(String),

    #[error("Room not found: {0}")]
    RoomNotFound(String),

    #[error("Item not found: {0}")]
    ItemNotFound(String),

    #[error("Command not recognized: {0}")]
    InvalidCommand(String),

    #[error("System error: {0}")]
    SystemError(String),

    #[error("Save file corrupted: {0}")]
    CorruptedSave(String),
}
```

### SystemError

Errors specific to system operations.

```rust
#[derive(Debug, thiserror::Error)]
pub enum SystemError {
    #[error("System initialization failed: {0}")]
    InitializationFailed(String),

    #[error("Command processing failed: {0}")]
    CommandFailed(String),

    #[error("State update failed: {0}")]
    UpdateFailed(String),
}
```

## Serialization

### Save Format

Game saves use JSON format with versioning support.

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "version")]
pub enum SaveFormat {
    #[serde(rename = "1.0")]
    V1_0 {
        game_state: GameState,
        adventure_path: String,
        timestamp: DateTime<Utc>,
    },
    #[serde(rename = "1.1")]
    V1_1 {
        game_state: GameState,
        adventure_path: String,
        timestamp: DateTime<Utc>,
        checksum: String,
    },
}
```

### Adventure Format Version

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "format_version")]
pub enum AdventureFormat {
    #[serde(rename = "1.0")]
    V1_0(AdventureV1),
    #[serde(rename = "1.1")]
    V1_1(AdventureV1_1),
}
```

## Examples

### Creating a Simple Game

```rust
use sagacraft_rs::{AdventureGame, BasicWorldSystem, InventorySystem};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a new game
    let mut game = AdventureGame::new(Some("my_adventure.json".to_string()));

    // Load the adventure
    game.load_adventure()?;

    // Add systems
    game.add_system(Box::new(BasicWorldSystem::default()));
    game.add_system(Box::new(InventorySystem::default()));

    // Process some commands
    let output = game.process_command("look");
    for line in output {
        println!("{}", line);
    }

    let output = game.process_command("go north");
    for line in output {
        println!("{}", line);
    }

    Ok(())
}
```

### Implementing a Custom System

```rust
use sagacraft_rs::{System, Command, AdventureGame, SystemError};

pub struct WeatherSystem {
    current_weather: String,
    weather_timer: f64,
}

impl WeatherSystem {
    pub fn new() -> Self {
        Self {
            current_weather: "clear".to_string(),
            weather_timer: 0.0,
        }
    }
}

impl System for WeatherSystem {
    fn name(&self) -> &str {
        "weather"
    }

    fn initialize(&mut self, _game: &mut AdventureGame) -> Result<(), SystemError> {
        Ok(())
    }

    fn process_command(&mut self, command: &Command, _game: &mut AdventureGame) -> Option<Vec<String>> {
        match command.verb.as_str() {
            "weather" => Some(vec![format!("The weather is currently {}.", self.current_weather)]),
            _ => None,
        }
    }

    fn update(&mut self, _game: &mut AdventureGame, delta_time: f64) {
        self.weather_timer += delta_time;
        if self.weather_timer > 60.0 { // Change weather every minute
            self.weather_timer = 0.0;
            self.current_weather = match rand::random::<u8>() % 4 {
                0 => "clear",
                1 => "cloudy",
                2 => "rainy",
                _ => "stormy",
            }.to_string();
        }
    }

    fn can_handle(&self, command: &Command) -> bool {
        matches!(command.verb.as_str(), "weather")
    }
}
```

### Loading and Saving Games

```rust
use sagacraft_rs::AdventureGame;

fn save_game_example(game: &AdventureGame) -> Result<(), Box<dyn std::error::Error>> {
    game.save_game("savegame.json")?;
    println!("Game saved successfully!");
    Ok(())
}

fn load_game_example() -> Result<AdventureGame, Box<dyn std::error::Error>> {
    let mut game = AdventureGame::new(Some("my_adventure.json".to_string()));
    game.load_game("savegame.json")?;
    println!("Game loaded successfully!");
    Ok(game)
}
```

### Creating Adventure Content

```rust
use sagacraft_rs::*;
use std::collections::HashMap;

fn create_simple_adventure() -> Adventure {
    let mut rooms = HashMap::new();

    // Create a starting room
    let mut exits = HashMap::new();
    exits.insert("north".to_string(), Exit {
        to: "forest_clearing".to_string(),
        description: Some("A path leads north into the forest.".to_string()),
        locked: false,
        key_item: None,
        hidden: false,
    });

    rooms.insert("starting_cabin".to_string(), Room {
        id: "starting_cabin".to_string(),
        name: "Old Cabin".to_string(),
        description: "You are in an old, dusty cabin. Sunlight filters through cracks in the wooden walls.".to_string(),
        exits,
        items: vec!["rusty_key".to_string()],
        characters: vec![],
        properties: HashMap::new(),
    });

    // Create a forest clearing
    let mut clearing_exits = HashMap::new();
    clearing_exits.insert("south".to_string(), Exit {
        to: "starting_cabin".to_string(),
        description: Some("The cabin is visible to the south.".to_string()),
        locked: false,
        key_item: None,
        hidden: false,
    });

    rooms.insert("forest_clearing".to_string(), Room {
        id: "forest_clearing".to_string(),
        name: "Forest Clearing".to_string(),
        description: "A small clearing in the forest. Tall trees surround you on all sides.".to_string(),
        exits: clearing_exits,
        items: vec![],
        characters: vec!["mysterious_stranger".to_string()],
        properties: HashMap::new(),
    });

    // Create items
    let mut items = HashMap::new();
    items.insert("rusty_key".to_string(), ItemTemplate {
        id: "rusty_key".to_string(),
        name: "Rusty Key".to_string(),
        description: "An old, rusty key. It might open something.".to_string(),
        item_type: ItemType::Key,
        properties: HashMap::new(),
        stats: ItemStats::default(),
    });

    // Create characters
    let mut characters = HashMap::new();
    characters.insert("mysterious_stranger".to_string(), Character {
        id: "mysterious_stranger".to_string(),
        name: "Mysterious Stranger".to_string(),
        description: "A hooded figure stands silently in the clearing.".to_string(),
        dialogue_id: Some("stranger_greeting".to_string()),
        properties: HashMap::new(),
    });

    // Create dialogues
    let mut dialogues = HashMap::new();
    dialogues.insert("stranger_greeting".to_string(), Dialogue {
        id: "stranger_greeting".to_string(),
        text: "Greetings, traveler. What brings you to these woods?".to_string(),
        responses: vec![
            DialogueResponse {
                text: "I'm looking for adventure.".to_string(),
                next_dialogue: None,
                action: Some("set_flag adventuring true".to_string()),
            },
            DialogueResponse {
                text: "Just passing through.".to_string(),
                next_dialogue: None,
                action: None,
            },
        ],
    });

    Adventure {
        metadata: AdventureMetadata {
            title: "Simple Forest Adventure".to_string(),
            author: "Game Developer".to_string(),
            version: "1.0".to_string(),
            description: "A simple adventure in the forest.".to_string(),
        },
        rooms,
        items,
        characters,
        quests: HashMap::new(),
        dialogues,
    }
}
```

This API reference provides the foundation for building rich, interactive text-based adventures with SagaCraft. The modular system architecture allows for easy extension and customization of game mechanics.