# SagaCraft Technical Reference

**Version 4.0 · Audience: Developers & Advanced Modders**

This document describes the SagaCraft engine internals: architecture, data structures, the adventure JSON schema, the system trait API, and build instructions. All information reflects the actual source at `sagacraft_rs/`.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Crate Overview](#crate-overview)
3. [Core Types](#core-types)
4. [The System Trait](#the-system-trait)
5. [Built-in Systems](#built-in-systems)
6. [Command Parsing](#command-parsing)
7. [Engine and AdventureGame](#engine-and-adventuregame)
8. [Adventure JSON Schema](#adventure-json-schema)
9. [Game Events](#game-events)
10. [Quest System Internals](#quest-system-internals)
11. [Build and Test](#build-and-test)
12. [Contributing](#contributing)

---

## Project Structure

```
SagaCraft/
├── Cargo.toml                  # Workspace manifest
├── sagacraft_rs/               # Core engine library
│   └── src/
│       ├── lib.rs              # Public re-exports
│       ├── engine.rs           # High-level Engine wrapper
│       ├── game_state.rs       # AdventureGame, Room, Item, Monster, Player
│       ├── command.rs          # Command enum, Direction, parser
│       ├── adventure.rs        # Adventure / AdventureRoom types (secondary format)
│       └── systems/
│           ├── mod.rs          # System trait definition
│           ├── basic_world.rs  # Movement, look, say
│           ├── inventory.rs    # Item management
│           ├── combat.rs       # Attack/fight, status
│           └── quests.rs       # Quest tracker, QuestSystem
├── sagacraft_player/           # CLI binary
├── sagacraft_ide_tui/          # Ratatui terminal IDE
└── sagacraft_ide_gui/          # egui graphical IDE
```

---

## Crate Overview

The `sagacraft_rs` library is the only dependency shared by all three front-ends. The three binaries are thin shells that set up the engine and pass user input through it.

### Public re-exports (`lib.rs`)

```rust
pub use game_state::{
    AdventureGame, GameState, Item, ItemType,
    Monster, MonsterStatus, Player, Room,
};
pub use command::{Command, Direction};
pub use engine::{Engine, EngineEvent, EngineOutput};
pub use systems::{
    BasicWorldSystem, CombatSystem, InventorySystem,
    quests::QuestSystem,
};
```

---

## Core Types

### `Item`

Defined in `game_state.rs`.

```rust
pub struct Item {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub item_type: ItemType,     // see ItemType enum
    pub weight: i32,
    pub value: i32,
    pub is_weapon: bool,
    pub weapon_type: i32,        // 1=axe 2=bow 3=club 4=spear 5=sword
    pub weapon_dice: i32,
    pub weapon_sides: i32,
    pub is_armor: bool,
    pub armor_value: i32,
    pub is_takeable: bool,       // default true
    pub is_wearable: bool,
    pub location: i32,           // room_id | 0=inventory | -1=worn
}
```

`Item::get_damage()` rolls `weapon_dice` * `weapon_sides` using `rand::thread_rng`.

**`ItemType` variants (JSON lowercase strings):**

| Rust variant | JSON string | Notes |
|---|---|---|
| `ItemType::Weapon` | `"weapon"` | use `is_weapon:true` for combat |
| `ItemType::Armor` | `"armor"` | use `is_armor:true` + `armor_value` |
| `ItemType::Treasure` | `"treasure"` | decorative value items |
| `ItemType::Readable` | `"readable"` | prints description on `use` |
| `ItemType::Edible` | `"edible"` | heals `value` HP on `use`, consumed |
| `ItemType::Drinkable` | `"drinkable"` | same as edible |
| `ItemType::Container` | `"container"` | no special engine logic yet |
| `ItemType::Normal` | `"normal"` / unrecognised | default |

### `Monster`

```rust
pub struct Monster {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub room_id: i32,
    pub hardiness: i32,          // max health
    pub agility: i32,            // counter-attack strength
    pub friendliness: MonsterStatus,
    pub courage: i32,
    pub weapon_id: Option<i32>,  // item ID of their weapon
    pub armor_worn: i32,         // static armor reduction (unused by player)
    pub gold: i32,               // dropped on death
    pub is_dead: bool,
    pub current_health: Option<i32>,  // None = full health
}
```

`MonsterStatus` variants: `Friendly`, `Neutral`, `Hostile`. Only `Hostile` monsters can be attacked.

Counter-attack damage formula: `1 ..= (monster.agility / 3 + 1).max(2)` → subtract player's equipped `armor_value`.

### `Room`

```rust
pub struct Room {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub exits: HashMap<String, i32>,  // direction string -> room id
    pub is_dark: bool,
}
```

Items are not stored in `Room`; they are found via `Item::location == room.id`.

### `Player`

```rust
pub struct Player {
    pub name: String,
    pub hardiness: i32,           // default 12; health pool & carry multiplier
    pub agility: i32,             // default 12
    pub charisma: i32,            // default 12
    pub weapon_ability: HashMap<i32, i32>, // weapon_type -> ability (1-5 → 5)
    pub armor_expertise: i32,
    pub gold: i32,                // default 200
    pub current_room: i32,
    pub current_health: Option<i32>,  // None = full health
    pub inventory: Vec<i32>,      // item IDs
    pub equipped_weapon: Option<i32>,
    pub equipped_armor: Option<i32>,
    pub experience_points: i32,
    pub level: i32,               // default 1
}
```

Max carry weight = `player.hardiness * 10`.

### `AdventureGame`

The central mutable game object. Holds all state and the list of active systems.

```rust
pub struct AdventureGame {
    pub adventure_file: String,
    pub rooms: HashMap<i32, Room>,
    pub items: HashMap<i32, Item>,
    pub monsters: HashMap<i32, Monster>,
    pub player: Player,
    pub companions: Vec<String>,
    pub turn_count: i32,
    pub game_over: bool,
    pub adventure_title: String,
    pub adventure_intro: String,
    pub effects: Vec<serde_json::Value>,
    pub systems: Vec<Box<dyn System>>,
    pub quests: Vec<serde_json::Value>,
    pub events: Vec<GameEvent>,
}
```

**Key methods:**

| Method | Description |
|--------|-------------|
| `load_adventure() -> Result<String, _>` | Parses JSON; returns opening header string |
| `process_command(&str) -> Vec<String>` | Main dispatch; runs primary + observer passes |
| `look() -> String` | Renders current room |
| `move_player(&str) -> Option<String>` | Moves player, emits `RoomEntered` event |
| `take_item(&str) -> Result<String, String>` | Picks up item, checks weight, emits `ItemCollected` |
| `drop_item(&str) -> bool` | Drops item, clears equip slots if needed |
| `equip_item(&str) -> Result<String, String>` | Equips weapon or wearable armor |
| `unequip_slot(&str) -> Result<String, String>` | Unequips `"weapon"` or `"armor"` slot |
| `use_item(&str) -> Result<String, String>` | Consumes, reads, or activates item |
| `examine_item(&str) -> Option<String>` | Returns full item details from inventory or room |
| `carry_weight() -> (i32, i32)` | Returns `(current, max)` carry weight |
| `get_items_in_room(room_id) -> Vec<&Item>` | Items whose `location == room_id` |
| `get_monsters_in_room(room_id) -> Vec<&Monster>` | Alive monsters in room |

---

## The System Trait

All game logic is plugged in via the `System` trait (`systems/mod.rs`):

```rust
pub trait System: Send + Sync {
    /// Primary handler: return Some(output) to claim the command; None to pass.
    fn on_command(
        &mut self,
        command: &str,
        args: &[&str],
        game: &mut AdventureGame,
    ) -> Option<String>;
}
```

**Dispatch in `process_command`:**

1. The verb is extracted and lowercased.
2. Systems are iterated in registration order. The **first** system that returns `Some(...)` claims the command.
3. After the primary pass, every system is called with the special verb `"__events__"` and an empty args slice. This is the observer pass — systems react to pending `GameEvent`s without owning the command.
4. The `events` buffer is cleared after the observer pass.

To add a custom system:

```rust
game.add_system(Box::new(MySystem::default()));
```

Register before `load_adventure` to ensure `init`-style behaviour in the first observer pass.

---

## Built-in Systems

### `BasicWorldSystem`

Handles: `look`/`l`, direction movement (all six cardinal directions plus aliases), `go`/`move <dir>`, `say`/`shout`/`yell`.

When `say` is used and a non-hostile NPC is present, the NPC's name is included in the response.

### `InventorySystem`

Handles: `inventory`/`inv`/`i`, `take`/`get`, `drop`, `equip`/`wield`/`wear`, `unequip`/`remove`, `use`, `examine`/`inspect`/`x`.

### `CombatSystem`

Handles: `attack`/`fight <target>`, `status`/`stats`.

Combat flow per `attack` call:
1. Find matching monster in current room (case-insensitive partial name match).
2. Refuse if monster is not `Hostile`.
3. Calculate player damage and apply to monster HP.
4. If monster dies: set `is_dead = true`, transfer gold, push `MonsterKilled` event.
5. If monster survives: calculate monster counter-attack with armor mitigation, apply to player HP. If player HP ≤ 0, set `game_over = true`.

### `QuestSystem`

Handles: `quests`, `accept <id>`, `complete <id>`, and the `__events__` observer pass.

On first call, loads quests from `game.quests` (the raw JSON array). Supports `Kill` and `Collect` objective auto-progress via the observer pass.

---

## Command Parsing

`Command::parse(input: &str) -> Result<Command, ParseError>` in `command.rs`:

```rust
pub enum Command {
    Help,
    Look,
    Inventory,
    Move(Direction),
    Take(String),
    Drop(String),
    Use(String),
    Equip(String),
    Examine(String),
    Say(String),
    Quit,
    Unknown(String),
}

pub enum Direction { North, South, East, West, Up, Down }
```

The `Engine::step` method converts `Command` back to a string and feeds it to `AdventureGame::process_command`, which handles all matching in lowercase. Custom commands that are not in the `Command` enum are passed through as `Command::Unknown(raw)` and dispatched to systems as-is.

---

## Engine and AdventureGame

`Engine` (`engine.rs`) is a thin wrapper that pre-wires all four default systems:

```rust
impl Engine {
    pub fn new(adventure_path: impl Into<String>) -> Self;
    pub fn load_from_path(path: impl Into<String>) -> Result<Self, Box<dyn Error>>;
    pub fn step(&mut self, event: EngineEvent) -> EngineOutput;
    pub fn look(&self) -> String;
    pub fn is_over(&self) -> bool;
}
```

`EngineOutput` wraps `Vec<String>` lines. `EngineEvent` is currently `EngineEvent::Command(Command)`.

Use `Engine::load_from_path` for a one-liner that creates and loads:
```rust
let mut engine = Engine::load_from_path("demo_adventure.json")?;
let intro = engine.look();
```

---

## Adventure JSON Schema

This section documents every field accepted by `AdventureGame::load_adventure`.

### Top-level object

```json
{
  "id": "my_adventure",          // string; adventure identifier
  "title": "My Adventure",       // string; shown in banner
  "intro": "Once upon a time…",  // string; optional intro text
  "description": "…",            // string; metadata only
  "start_room": 1,               // integer; starting room id
  "rooms":    [ … ],
  "items":    [ … ],
  "monsters": [ … ],
  "quests":   [ … ],
  "effects":  [ … ]              // reserved for future use
}
```

### Room object

```json
{
  "id": 1,                           // integer, must be unique
  "name": "Village Square",          // string
  "description": "Cobblestones…",    // string
  "is_dark": false,                  // boolean, optional (default false)
  "exits": {                         // object: direction string -> room id int
    "north": 2,
    "east": 3,
    "palace": 5
  },
  "items": [1, 2, 3]                 // array of item ids starting in this room
}
```

`exits` keys can be any string; standard values are `north`, `south`, `east`, `west`, `up`, `down`.

Rooms referenced in `exits` must exist in the `rooms` array or the exit will be silently ignored.

The `items` array in a room lists item IDs whose `location` field will be interpreted as that room's ID. Alternatively, set `"location": <room_id>` on each item directly.

### Item object

```json
{
  "id": 101,
  "name": "Iron Sword",
  "description": "A dependable one-handed blade.",
  "type": "weapon",          // see ItemType table; key is "type" not "item_type"
  "weight": 3,
  "value": 25,
  "is_weapon": true,
  "weapon_type": 5,          // 1=axe 2=bow 3=club 4=spear 5=sword
  "weapon_dice": 1,
  "weapon_sides": 8,
  "is_armor": false,
  "armor_value": 0,
  "is_takeable": true,       // default true
  "is_wearable": false,
  "location": 1              // room_id where item starts; 0 = player inventory
}
```

For **armor** items set `"is_armor": true` and `"is_wearable": true`.

For **consumables** set `type` to `"edible"` or `"drinkable"` and set `value` to the HP restored.

### Monster object

```json
{
  "id": 201,
  "name": "Goblin Warrior",
  "description": "A small but fierce goblin.",
  "room_id": 3,
  "hardiness": 8,            // max health
  "agility": 6,              // counter-attack strength
  "friendliness": "hostile", // "friendly" | "neutral" | "hostile"
  "courage": 80,             // unused by default combat logic (future)
  "weapon_id": 301,          // optional; item id of monster's weapon
  "armor_worn": 1,           // static armor reduction for monster (future)
  "gold": 10
}
```

### Quest object

```json
{
  "id": 1,
  "title": "Slay the Goblin King",
  "description": "The Goblin King terrorises the village.",
  "objectives": [
    {
      "type": "kill_monster",   // "kill_monster"|"collect_item"|"reach_room"|"talk_to_npc"
      "target_id": 202,         // integer id used as partial-name match string
      "description": "Kill the Goblin King"
    },
    {
      "type": "collect_item",
      "target_id": 105,
      "description": "Recover the stolen crown"
    }
  ]
}
```

> **Note:** Quest `id` must be an integer. Use the integer (e.g. `accept 1`, `complete 1`) in-game.

---

## Game Events

`GameEvent` (`game_state.rs`) is used as an inter-system bus:

```rust
pub enum GameEvent {
    MonsterKilled { monster_name: String, room_id: i32 },
    ItemCollected { item_name: String, item_id: i32 },
    RoomEntered   { room_id: i32 },
    ItemUsed      { item_name: String },
}
```

Events are pushed to `game.events` during the primary pass and consumed in the observer pass (`"__events__"` call). Custom systems can subscribe to events by handling `"__events__"` and reading `game.events`.

---

## Quest System Internals

`QuestSystem` (`systems/quests.rs`) manages `QuestTracker` and a pool of available quests.

**Key types:**

| Type | Purpose |
|------|---------|
| `Quest` | Named quest with stages, rewards, prerequisites |
| `QuestStage` | One phase of a quest; holds objectives |
| `QuestObjective` | Single goal with a progress counter |
| `QuestReward` | XP, gold, items, and reputation changes |
| `QuestTracker` | Owns active/completed/failed sets and history |

**Status lifecycle:**

```
Available → Active → Completed
                  → Failed
                  → Abandoned
```

**Level-adjusted rewards:** `get_level_adjusted_rewards(player_level)` scales XP by ±10% per level difference between player and quest giver, down to 50% for players 5+ levels above the quest.

---

## Build and Test

### Prerequisites

- Rust 1.70+ (`rustup update stable`)
- GUI build additionally requires system OpenGL/EGL headers

### Compile and run

```bash
# Debug build (faster compile, slower runtime)
cargo build

# Release build
cargo build --release

# Run CLI player
cargo run --bin sagacraft_player -- demo_adventure.json

# Run TUI IDE
cargo run --bin sagacraft_ide_tui

# Run GUI IDE
cargo run --bin sagacraft_ide_gui

# Run tests
cargo test

# Run tests for the core library only
cargo test -p sagacraft_rs

# Generate API documentation
cargo doc --open
```

### Compile-time warnings

`ashpd` (Linux portal integration used by egui) may emit future-incompatibility warnings as of Rust 1.85+. These are upstream issues and do not affect functionality.

---

## Contributing

1. Fork the repository: https://github.com/James-HoneyBadger/SagaCraft
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Implement and test your changes
4. Run `cargo fmt && cargo clippy` before committing
5. Open a pull request against `main`

**Adding a new system:**
1. Create `sagacraft_rs/src/systems/my_system.rs`
2. Implement `System` trait
3. Register in `engine.rs` inside `Engine::new`
4. Add `pub mod my_system;` to `systems/mod.rs`
5. Re-export from `lib.rs` if needed by front-ends
