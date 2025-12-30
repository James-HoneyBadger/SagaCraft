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
- **Extensibility**: Plugin system for custom mechanics

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
  "start_room": "entrance",
  "rooms": [...],
  "player_start_inventory": [...]
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
  "start_room": "entrance",
  "rooms": [
    {
      "id": "entrance",
      "title": "Dungeon Entrance",
      "description": "You stand at the entrance of an ancient dungeon. A stone corridor stretches before you, and you can hear the drip of water echoing in the distance.",
      "exits": {
        "north": "chamber"
      },
      "items": [
        {
          "id": "rusty_key",
          "name": "Rusty Key",
          "description": "An old, rusty iron key. It looks like it might still work."
        }
      ]
    },
    {
      "id": "chamber",
      "title": "Main Chamber",
      "description": "You've entered a large circular chamber. Torches flicker on the walls, casting dancing shadows. In the center stands a stone pedestal with a locked chest.",
      "exits": {
        "south": "entrance"
      },
      "items": []
    }
  ],
  "player_start_inventory": []
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

Use room descriptions that change based on player actions:

```json
{
  "id": "garden",
  "title": "The Secret Garden",
  "description": "A beautiful garden with flowers in full bloom. [If player has visited before: The flowers seem to recognize you and wave gently in the breeze.]",
  "items": []
}
```

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
  "id": "excalibur",
  "name": "Excalibur",
  "description": "The legendary sword of King Arthur. It glows with an inner light.",
  "item_type": "Weapon",
  "weight": 3,
  "value": 1000,
  "is_weapon": true,
  "weapon_type": 5,
  "weapon_dice": 2,
  "weapon_sides": 6,
  "is_takeable": true,
  "is_wearable": false
}
```

### Item Properties

| Property | Description | Example |
|----------|-------------|---------|
| `id` | Unique identifier | "magic_sword" |
| `name` | Display name | "Magic Sword" |
| `description` | Detailed description | "A sword imbued with magic" |
| `item_type` | Category | "Weapon", "Armor", "Treasure" |
| `weight` | Weight in kg | 2.5 |
| `value` | Gold value | 100 |
| `is_weapon` | Can be used in combat | true |
| `weapon_dice` | Damage dice count | 1 |
| `weapon_sides` | Damage dice sides | 8 |
| `is_armor` | Provides protection | true |
| `armor_value` | Protection amount | 3 |

### Special Items

Create unique items with special effects:

```json
{
  "id": "teleport_ring",
  "name": "Ring of Teleportation",
  "description": "This golden ring allows you to teleport between known locations.",
  "item_type": "Treasure",
  "weight": 0,
  "value": 500,
  "special_effect": "teleport"
}
```

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
  "friendliness": "Friendly",
  "courage": 3,
  "weapon_id": null,
  "armor_worn": 0,
  "gold": 50,
  "is_dead": false
}
```

### NPC Behaviors

- **Friendly**: Will help or provide information
- **Neutral**: May respond to questions but won't assist
- **Hostile**: Will attack the player on sight

### Dialogue Systems

Implement NPC conversations:

```json
{
  "npc_id": 1,
  "dialogue_tree": {
    "greeting": "Welcome, adventurer! What brings you to our village?",
    "responses": {
      "quest": "I'm looking for the ancient temple.",
      "trade": "I'd like to buy some supplies.",
      "goodbye": "Farewell!"
    }
  }
}
```

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
  "friendliness": "Hostile",
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

```json
{
  "id": "main_quest_1",
  "title": "Find the Lost Temple",
  "description": "Locate the ancient temple hidden in the mountains.",
  "objectives": [
    {
      "id": "find_map",
      "description": "Find the map in the village library",
      "completed": false
    },
    {
      "id": "gather_supplies",
      "description": "Collect food and water for the journey",
      "completed": false
    },
    {
      "id": "reach_temple",
      "description": "Travel to the temple location",
      "completed": false
    }
  ],
  "reward": {
    "experience": 100,
    "items": ["magic_amulet"],
    "gold": 200
  }
}
```

### Quest Types

1. **Collection Quests**: Gather specific items
2. **Defeat Quests**: Eliminate certain enemies
3. **Exploration Quests**: Visit specific locations
4. **Dialogue Quests**: Complete conversations
5. **Time-based Quests**: Complete within time limits

## Testing and Debugging

### Testing Checklist

- [ ] All rooms are accessible
- [ ] All items can be picked up and used
- [ ] Combat is balanced
- [ ] Quests can be completed
- [ ] No dead ends or soft locks
- [ ] Save/load functionality works
- [ ] Performance is acceptable

### Common Issues

1. **Missing Exits**: Players can't reach certain areas
2. **Unobtainable Items**: Quest items that can't be found
3. **Broken Combat**: Monsters that can't be defeated
4. **Poor Descriptions**: Rooms that aren't immersive

### Testing Tools

Use SagaCraft's built-in testing features:

```bash
# Validate adventure structure
cargo run --bin sagacraft_player -- --validate path/to/adventure.json

# Run automated tests
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

Extend SagaCraft with custom mechanics:

```rust
// Example: Weather system
pub struct WeatherSystem {
    current_weather: WeatherType,
    weather_effects: HashMap<WeatherType, Vec<String>>,
}
```

### Mod Support

Design adventures that support modifications:

```json
{
  "mod_support": {
    "custom_items": true,
    "custom_rooms": true,
    "custom_quests": false
  }
}
```

### Multiplayer Considerations

While SagaCraft is single-player focused, consider:

- **Shared Universes**: Adventures that can be experienced together
- **Competitive Elements**: Score-based challenges
- **Cooperative Play**: Split-screen or turn-based multiplayer

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