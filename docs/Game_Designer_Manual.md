# SagaCraft Game Designer Manual

## Creating Adventures with SagaCraft

This comprehensive guide will teach you how to design, create, and publish your own text-based adventures using the SagaCraft engine. Whether you're a first-time designer or an experienced developer, this manual covers everything you need to know.

## Table of Contents

1. [Introduction](#introduction)
2. [Adventure Structure](#adventure-structure)
3. [Creating Your First Adventure](#creating-your-first-adventure)
4. [Advanced Design Techniques](#advanced-design-techniques)
5. [Item and Inventory Design](#item-and-inventory-design)
6. [Character and NPC Design](#character-and-npc-design)
7. [Combat Design](#combat-design)
8. [Quest System](#quest-system)
9. [Testing and Debugging](#testing-and-debugging)
10. [Publishing Your Adventure](#publishing-your-adventure)
11. [Best Practices](#best-practices)

## Introduction

### What is SagaCraft?

SagaCraft is a text-based adventure game engine that focuses on:
- **Simplicity**: Easy to learn, powerful to use
- **Flexibility**: Support for various game genres
- **Performance**: Fast loading and execution
- **Extensibility**: System trait for custom mechanics

### Design Philosophy

SagaCraft adventures emphasize:
- **Storytelling**: Rich narratives and character development
- **Exploration**: Discovery and player choice
- **Immersion**: Detailed descriptions and atmosphere
- **Replayability**: Multiple paths and endings

## Adventure Structure

### JSON Format Overview

All SagaCraft adventures are stored in JSON format:

```json
{
  "id": "my_adventure",
  "title": "My First Adventure",
  "start_room": 1,
  "rooms": [...],
  "items": [...],
  "monsters": [...],
  "quests": []
}
```

### Core Components

1. **Metadata**: ID, title, starting location
2. **Rooms**: Locations players can visit
3. **Items**: Objects players can interact with
4. **Characters**: NPCs and monsters
5. **Connections**: How rooms link together

## Creating Your First Adventure

### Step 1: Plan Your Story

Before writing code, plan your adventure:

1. **Theme**: What genre? Fantasy, sci-fi, mystery?
2. **Plot**: What's the main story?
3. **Characters**: Who will the player meet?
4. **Locations**: Where does the action take place?
5. **Puzzles**: What challenges will players face?
6. **Ending**: How does the story conclude?

### Step 2: Create the Basic Structure

Start with a simple two-room adventure:

```json
{
  "id": "tutorial_adventure",
  "title": "The Tutorial Dungeon",
  "start_room": 1,
  "rooms": [
    {
      "id": 1,
      "name": "Dungeon Entrance",
      "description": "You stand at the entrance of an ancient dungeon. A stone corridor stretches before you, and you can hear the drip of water echoing in the distance.",
      "exits": {
        "north": 2
      }
    },
    {
      "id": 2,
      "name": "Main Chamber",
      "description": "You've entered a large circular chamber. Torches flicker on the walls, casting dancing shadows. In the center stands a stone pedestal with a locked chest.",
      "exits": {
        "south": 1
      }
    }
  ],
  "items": [
    {
      "id": 101,
      "name": "Rusty Key",
      "description": "An old, rusty iron key. It looks like it might still work.",
      "type": "normal",
      "weight": 0,
      "value": 0,
      "is_takeable": true,
      "location": 1
    }
  ],
  "monsters": [],
  "quests": []
}
```

### Step 3: Test Your Adventure

Use the SagaCraft editors to test:

```bash
# Terminal UI Editor
cargo run --bin sagacraft_ide_tui

# GUI Editor (if available)
cargo run --bin sagacraft_ide_gui

# Play your adventure
cargo run --bin sagacraft_player -- path/to/your/adventure.json
```

## Advanced Design Techniques

### Branching Narratives

Create multiple paths through your story:

```json
{
  "id": "crossroads",
  "title": "The Crossroads",
  "description": "You stand at a crossroads. A signpost points in three directions.",
  "exits": {
    "north": "dark_forest",
    "east": "peaceful_village",
    "west": "dangerous_mountains"
  }
}
```

### Conditional Content

SagaCraft does not currently support conditional room descriptions. Instead, use quest objectives and item placement to gate narrative progression. Players discover story through exploration and item examination.

### Puzzles and Challenges

Design engaging puzzles:

1. **Logic Puzzles**: "Use the key to unlock the door"
2. **Item Combination**: "Mix the potion with the herb"
3. **Riddles**: "Answer the sphinx's question correctly"
4. **Exploration**: "Find the hidden passage"

## Item and Inventory Design

### Item Types

SagaCraft supports various item types:

```json
{
  "id": 101,
  "name": "Excalibur",
  "description": "The legendary sword of King Arthur. It glows with an inner light.",
  "type": "weapon",
  "weight": 3,
  "value": 1000,
  "is_weapon": true,
  "weapon_type": 5,
  "weapon_dice": 2,
  "weapon_sides": 6,
  "is_takeable": true,
  "is_wearable": false,
  "location": 1
}
```

### Item Properties

| Property | Description | Example |
|----------|-------------|---------|
| `id` | Unique integer identifier | 101 |
| `name` | Display name | "Magic Sword" |
| `description` | Detailed description | "A sword imbued with magic" |
| `type` | Category (JSON key is `type`) | "weapon", "armor", "treasure" |
| `weight` | Weight (integer) | 3 |
| `value` | Gold value (or HP healed for consumables) | 100 |
| `is_weapon` | Can be used in combat | true |
| `weapon_dice` | Damage dice count | 1 |
| `weapon_sides` | Damage dice sides | 8 |
| `is_armor` | Provides protection | true |
| `armor_value` | Protection amount | 3 |
| `location` | Room ID where item starts (0 = inventory) | 1 |

### Special Items

For unique items, use descriptive text in the `description` field. The engine does not support a `special_effect` field — special behaviour requires a custom Rust system.

## Character and NPC Design

### NPC Types

```json
{
  "id": 1,
  "name": "Village Elder",
  "description": "An old man with a long white beard and wise eyes.",
  "room_id": 1,
  "hardiness": 8,
  "agility": 5,
  "friendliness": "friendly",
  "courage": 3,
  "weapon_id": null,
  "armor_worn": 0,
  "gold": 50,
  "is_dead": false
}
```

### NPC Behaviors

- **Friendly**: Cannot be attacked. Will respond when the player uses `say` nearby.
- **Neutral**: Cannot be attacked by default. May respond to `say`.
- **Hostile**: Will fight back when attacked by the player.

SagaCraft does not have a dialogue tree system. NPC interaction is through the `say` command and quest `talk_to_npc` objectives.

## Combat Design

### Monster Creation

```json
{
  "id": 100,
  "name": "Giant Spider",
  "description": "A massive spider with venomous fangs and eight glowing eyes.",
  "room_id": 5,
  "hardiness": 12,
  "agility": 8,
  "friendliness": "hostile",
  "courage": 7,
  "weapon_id": 200,
  "armor_worn": 1,
  "gold": 25,
  "is_dead": false,
  "current_health": 12
}
```

### Combat Balance

Consider these factors:
- **Difficulty Scaling**: Harder enemies in later areas
- **Reward Balance**: Better loot from tougher enemies
- **Player Progression**: Allow players to gain better equipment
- **Multiple Strategies**: Different ways to win fights

### Environmental Combat

Use room descriptions to enhance combat:

```
The narrow corridor forces you to fight the orc one-on-one.
The high ground gives you an advantage in this battle.
The magical wards weaken undead creatures in this area.
```

## Quest System

### Quest Structure

Quests use integer IDs and have objectives that auto-track during gameplay:

```json
{
  "id": 1,
  "title": "Find the Lost Temple",
  "description": "Locate the ancient temple hidden in the mountains.",
  "objectives": [
    {
      "type": "collect_item",
      "target_id": 105,
      "description": "Find the map in the village library"
    },
    {
      "type": "reach_room",
      "target_id": 10,
      "description": "Travel to the temple location"
    }
  ]
}
```

Rewards (gold and XP) are defined as flat values on quest completion.

### Quest Types

1. **Collection Quests**: Gather specific items
2. **Defeat Quests**: Eliminate certain enemies
3. **Exploration Quests**: Visit specific locations
4. **Talk Quests**: Speak near matching NPCs

## Testing and Debugging

### Testing Checklist

- [ ] All rooms are accessible
- [ ] All items can be picked up and used
- [ ] Combat is balanced
- [ ] Quests can be completed
- [ ] No dead ends or soft locks
- [ ] JSON validates (`python3 -m json.tool adventure.json`)

### Common Issues

1. **Missing Exits**: Players can't reach certain areas
2. **Unobtainable Items**: Quest items that can't be found
3. **Broken Combat**: Monsters that can't be defeated
4. **Poor Descriptions**: Rooms that aren't immersive

### Testing

Play-test directly with the CLI player:

```bash
# Play your adventure
cargo run --bin sagacraft_player -- path/to/adventure.json

# Run engine unit tests
cargo test
```

## Publishing Your Adventure

### Preparation

1. **Final Testing**: Test on multiple systems
2. **Documentation**: Write clear instructions
3. **Screenshots**: Capture gameplay moments
4. **Metadata**: Include proper credits and licensing

### Distribution

```json
{
  "metadata": {
    "author": "Your Name",
    "version": "1.0.0",
    "genre": "Fantasy",
    "difficulty": "Medium",
    "estimated_time": "2-3 hours",
    "target_audience": "All ages"
  }
}
```

### Sharing Platforms

- **GitHub**: Host adventure files and source code
- **Itch.io**: Game distribution platform
- **Personal Website**: Direct download links
- **Community Forums**: Share with other SagaCraft users

## Best Practices

### Writing Tips

1. **Show, Don't Tell**: Use descriptive language
   - ❌ "The room was scary."
   - ✅ "Shadows danced on the walls, and a cold draft carried the scent of decay."

2. **Vary Sentence Length**: Mix short and long sentences for rhythm

3. **Use Sensory Details**: Appeal to sight, sound, smell, touch

4. **Create Atmosphere**: Set the mood with your descriptions

### Design Principles

1. **Progressive Difficulty**: Start easy, get harder
2. **Clear Objectives**: Players should know what to do
3. **Multiple Solutions**: Allow different approaches
4. **Save Frequently**: Don't frustrate players with lost progress
5. **Feedback**: Let players know when they succeed or fail

### Technical Best Practices

1. **Validate JSON**: Use a JSON validator before testing
2. **Consistent IDs**: Use clear, consistent naming conventions
3. **Modular Design**: Break large adventures into sections
4. **Version Control**: Use Git to track changes
5. **Documentation**: Comment your adventure files

### Player Experience

1. **Intuitive Interface**: Commands should be obvious
2. **Helpful Feedback**: Explain what happens when players act
3. **Fair Challenges**: Puzzles should be solvable with available information
4. **Emotional Impact**: Create moments that affect players
5. **Memorable Ending**: Conclude in a satisfying way

## Advanced Topics

### Custom Systems

Extend SagaCraft with custom mechanics by implementing the `System` trait in Rust:

```rust
// Example: Weather system
use sagacraft_rs::{System, AdventureGame, GameEvent};

pub struct WeatherSystem {
    current_weather: String,
}

impl System for WeatherSystem {
    fn on_command(&mut self, command: &str, _args: &[&str], _game: &mut AdventureGame) -> Option<String> {
        match command {
            "weather" => Some(format!("The weather is {}.", self.current_weather)),
            _ => None,
        }
    }
}
```

Register your system on the `Engine` before loading:

```rust
let mut engine = Engine::new("adventure.json");
engine.game.add_system(Box::new(WeatherSystem { current_weather: "sunny".into() }));
engine.start()?;
```

## Resources

### Tools and Templates

- **Adventure Template**: Start with a basic structure
- **Item Database**: Pre-made items for common tropes
- **Room Generator**: Tools for creating room descriptions
- **Dialogue Editor**: Visual dialogue tree creation

### Community Resources

- **SagaCraft Forums**: Share tips and get feedback
- **Adventure Showcase**: See what others have created
- **Asset Library**: Shared art, music, and sound effects
- **Tutorials**: Video and written guides

### Learning Resources

- **Example Adventures**: Study published works
- **Design Theory**: Books on game design and writing
- **Programming**: Learn Rust for advanced features
- **Writing**: Improve your descriptive writing skills

---

**Ready to create your masterpiece?** Start small, test often, and most importantly, have fun creating worlds that others will love to explore. Your adventure could be the next great SagaCraft story!

For technical details, see the [Technical Reference](Technical_Reference.md). For API documentation, check the [API Reference](API_Reference.md).