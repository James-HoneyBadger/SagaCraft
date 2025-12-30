# SagaCraft User Manual

## Welcome to SagaCraft

Welcome to **SagaCraft**, a text-based adventure game engine that brings interactive fiction to life! This manual will guide you through playing adventures, understanding game mechanics, and making the most of your SagaCraft experience.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Commands](#basic-commands)
3. [Game Mechanics](#game-mechanics)
4. [Combat System](#combat-system)
5. [Inventory Management](#inventory-management)
6. [Quest System](#quest-system)
7. [Saving and Loading](#saving-and-loading)
8. [Tips and Tricks](#tips-and-tricks)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### Launching the Game

SagaCraft offers multiple ways to play:

#### Command Line Player
```bash
# Using the provided script
./Play.sh

# Or directly with cargo
cargo run --bin sagacraft_player -- path/to/adventure.json
```

#### Terminal UI Version
```bash
./Saga.sh
# or
cargo run --bin sagacraft_ide_tui
```

### Starting Your First Adventure

When you launch SagaCraft, you'll see:
```
SagaCraft (Rust) — CLI Player
Type 'help' for commands. Type 'quit' to exit.
```

The game will automatically load the default adventure or the one specified on the command line.

## Basic Commands

### Movement
```
go north    (or just 'n')
go south    (or just 's')
go east     (or just 'e')
go west     (or just 'w')
```

### Information
```
look        (or 'l')    - Examine your current location
inventory   (or 'i')    - View your carried items
help        (or 'h')    - Show available commands
```

### Item Interaction
```
take <item>           - Pick up an item
drop <item>           - Drop an item
use <item>            - Use an item
```

### Communication
```
say <message>         - Speak to NPCs or characters
```

### Game Control
```
quit        (or 'q')    - Exit the game
save                     - Save your progress
load                     - Load a saved game
```

## Game Mechanics

### Rooms and Navigation

Adventures are built around interconnected rooms. Each room has:
- A **title** and **description**
- **Items** that can be found and collected
- **Exits** to other rooms (north, south, east, west)
- **NPCs** or **monsters** that may inhabit the area

### Items

Items in SagaCraft have different types and properties:

| Type | Description | Example |
|------|-------------|---------|
| Weapon | Used in combat | Sword, axe, bow |
| Armor | Provides protection | Leather armor, shield |
| Treasure | Valuable collectibles | Gold coins, gems |
| Consumable | Can be eaten/drunk | Food, potions |
| Readable | Contains information | Books, scrolls |
| Container | Can hold other items | Backpack, chest |

### Characters and NPCs

You'll encounter various characters:
- **Friendly NPCs**: Can provide information, quests, or assistance
- **Neutral NPCs**: May ignore you or respond minimally
- **Hostile NPCs**: Will attack you on sight

## Combat System

### Basic Combat

Combat in SagaCraft is turn-based. When you encounter a hostile creature:

1. **Initiative**: Combat begins automatically
2. **Your Turn**: Choose your action (attack, use item, flee)
3. **Enemy Turn**: The monster attacks you
4. **Resolution**: Combat continues until one side is defeated

### Combat Stats

Every character has three main attributes:
- **Hardiness**: Physical strength and health
- **Agility**: Speed and dexterity
- **Courage**: Willingness to fight

### Weapons and Damage

Weapons deal damage based on dice rolls:
- **Sword**: 1d8 damage
- **Axe**: 1d10 damage
- **Bow**: 1d6 damage (ranged)
- **Club**: 1d4 damage
- **Spear**: 1d6 damage

### Armor and Defense

Armor reduces incoming damage:
- **Leather Armor**: 2 points of protection
- **Chain Mail**: 4 points of protection
- **Plate Armor**: 6 points of protection

## Inventory Management

### Managing Items

Your inventory has weight limits. Be mindful of what you carry:

```
> Inventory (12/20 kg capacity):
- Rusty sword (2kg, weapon)
- Health potion (0.5kg, consumable)
- Gold coins x 50 (0.1kg, treasure)
```

### Item Actions

- **Take**: Pick up items from the current room
- **Drop**: Leave items behind
- **Use**: Activate item effects (eat food, drink potions, read books)
- **Equip**: Wear armor or wield weapons

### Container Items

Some items can hold other items:
```
backpack contains:
- rope (1kg)
- lantern (2kg)
- map (0.1kg)
```

## Quest System

### Quest Types

Quests provide structure and goals:

- **Main Quests**: Drive the main story
- **Side Quests**: Optional objectives
- **Collection Quests**: Gather specific items
- **Defeat Quests**: Eliminate certain enemies

### Tracking Progress

Use the `quests` command to view your current objectives:

```
Active Quests:
1. [Main] Find the Ancient Temple
   - Locate the hidden entrance
   - Retrieve the sacred artifact
   - Return to the village elder

2. [Side] Collect Forest Herbs
   - Gather 5 healing herbs (2/5 collected)
```

## Saving and Loading

### Save Points

- **Manual Saves**: Use the `save` command anytime
- **Auto-saves**: Some adventures save automatically at checkpoints
- **Quick Saves**: Available in some game modes

### Save Files

Save files are stored in the `saves/` directory:
```
saves/
├── adventure_name_save1.json
├── adventure_name_save2.json
└── quicksave.json
```

### Loading Games

```
load save1    - Load a specific save file
load quick    - Load the quicksave
load          - Show available save files
```

## Tips and Tricks

### Exploration
- Always `look` when entering a new room
- Check for hidden items or exits
- Talk to every NPC you encounter
- Map your surroundings as you explore

### Combat
- Use the environment to your advantage
- Save before difficult fights
- Manage your health with potions
- Upgrade weapons and armor when possible

### Inventory
- Don't carry unnecessary weight
- Use containers to organize items
- Sell unwanted items for gold
- Keep important quest items safe

### General
- Read all text carefully - clues are everywhere
- Experiment with different commands
- Save frequently
- Take notes of important information

## Troubleshooting

### Common Issues

**"Command not recognized"**
- Check your spelling
- Use `help` to see available commands
- Some commands may not be available in certain situations

**"Cannot take item"**
- Check if the item exists in the current room
- Some items may be too heavy
- Certain items may be quest-specific

**"Cannot move in that direction"**
- Check available exits with `look`
- Some paths may be blocked or locked
- You may need special items to proceed

**"Game crashes"**
- Save your game frequently
- Report bugs with specific steps to reproduce
- Check the terminal for error messages

### Getting Help

- Use the `help` command in-game
- Check the [Technical Reference](Technical_Reference.md) for advanced commands
- Visit the [GitHub Issues](https://github.com/James-HoneyBadger/SagaCraft/issues) for bug reports
- Join the community discussions for tips and strategies

## Advanced Features

### Command Shortcuts

Most commands have abbreviations:
- `l` for `look`
- `i` for `inventory`
- `n/s/e/w` for directions
- `q` for `quit`

### Special Commands

Some adventures include custom commands:
- `examine <object>` - Detailed inspection
- `search <area>` - Look for hidden items
- `talk <person>` - Start conversation
- `cast <spell>` - Use magic (in fantasy adventures)

### Game Modes

Different adventures may offer:
- **Story Mode**: Linear narrative
- **Exploration Mode**: Open-world discovery
- **Survival Mode**: Resource management focus
- **Speed Run Mode**: Time-based challenges

---

**Enjoy your adventure in SagaCraft!** Remember, the best stories are the ones you create yourself. If you create an adventure you'd like to share, consider contributing it to the community.