# SagaCraft - User Manual

**Version 3.0.0**  
**Copyright © 2025 Honey Badger Universe**  
**License: MIT**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Using the IDE](#using-the-ide)
5. [Command Reference](#command-reference)
6. [Creating Adventures](#creating-adventures)
7. [Playing Adventures](#playing-adventures)
8. [Customization](#customization)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Features](#advanced-features)

---

## Introduction

### What is SagaCraft?

SagaCraft is a powerful, modern system for creating and playing text adventures with:

- **Modern Python Implementation** - Clean, maintainable code
- **Graphical IDE** - Create adventures without programming
- **Natural Language Parser** - Understanding conversational commands
- **Rich Features** - Combat, NPCs, puzzles, environmental effects
- **Extensible Architecture** - Plugin system for custom features
- **Cross-Platform** - Works on Windows, macOS, and Linux

### Who is This For?

- **Players** - Enjoy text adventures with modern enhancements
- **Creators** - Build your own adventures without coding
- **Developers** - Extend the system with plugins and custom features
- **Educators** - Teach creative writing and game design
- **Adventure Fans** - Experience interactive fiction with modern tools

---

## Installation

### System Requirements

- **Python 3.10 or higher**
- **Operating System**: Linux, macOS, or Windows
- **RAM**: 512 MB minimum
- **Disk Space**: 50 MB

### Quick Install

```bash
# Clone or download the repository
cd SagaCraft

# (Optional) Create a virtual environment and install tooling
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Launch the IDE
python -m src.acs.ui.ide
```

Want shortcuts? Run `./quickstart.sh` and choose **Launch IDE**.

### Manual Setup

1. **Download** the SagaCraft directory
2. **Open** a terminal in that directory
3. **Run** `python -m src.acs.ui.ide`

No additional dependencies are required; the IDE runs with the Python standard library.

---

## Getting Started

### Your First Game

1. **Launch the IDE**:
   ```bash
   python -m src.acs.ui.ide
   ```

2. **Load a Sample Adventure**:
   - Click **File → Open Adventure**
   - Navigate to `adventures/`
   - Select `sample_adventure.json`

3. **Play the Adventure**:
   - Click the **Play** tab
   - Click **Start/Resume Adventure**
   - Type commands like `look`, `go north`, `get sword`

### Quick Start Tutorial

The system includes a built-in tutorial:

```bash
# Run the tutorial adventure
python -m src.acs.ui.ide
# Select "Tutorial Quest" from the menu
```

Or within the IDE:
- Click **Help → Tutorial Mode**
- Follow the interactive guide

---

## Using the IDE

### IDE Overview

The Adventure Creation System IDE has five main tabs:

#### 1. **Overview Tab**
- Set adventure title, author, description
- Configure difficulty and intro text
- Manage global settings

#### 2. **Rooms Tab**
- Create and edit locations
- Set room descriptions
- Define exits (north, south, east, west, up, down, in, out)
- Add special features and environmental effects

#### 3. **Items Tab**
- Create weapons, armor, treasures, and objects
- Set properties (weight, value, damage, armor rating)
- Define special abilities and effects
- Mark items as takeable, wearable, edible, etc.

#### 4. **NPCs Tab**
- Create non-player characters
- Set personality traits and dialogue
- Configure combat stats
- Define AI behavior (friendly, hostile, merchant, quest-giver)

#### 5. **Play Tab**
- Test your adventure
- Full game engine with save/load
- Real-time debugging
- View game state

### Creating Your First Adventure

1. **Start a New Adventure**:
   - **File → New Adventure**
   - Enter title and author name
   - Write a brief description

2. **Create the Starting Room**:
   - Go to **Rooms** tab
   - Click **Add Room**
   - Name it "entrance" (lowercase, no spaces)
   - Description: "You stand at the entrance of a dark cave."
   - This becomes the spawn point

3. **Add an Item**:
   - Go to **Items** tab
   - Click **Add Item**
   - Name: "torch"
   - Description: "A wooden torch"
   - Check "Takeable"
   - Set weight: 1, value: 5

4. **Add an NPC**:
   - Go to **NPCs** tab
   - Click **Add NPC**
   - Name: "guard"
   - Description: "A stern-looking guard"
   - Friendliness: 50 (neutral)

5. **Place Items and NPCs**:
   - In **Rooms** tab, select "entrance"
   - Add "torch" to room items
   - Add "guard" to room NPCs

6. **Save Your Work**:
   - **File → Save Adventure**
   - Choose a filename (e.g., `my_adventure.json`)

7. **Test It**:
   - Go to **Play** tab
   - Click **Start/Resume Adventure**
   - Try: `look`, `get torch`, `talk to guard`

### IDE Features

#### Menu Bar

**File Menu**:
- New Adventure - Start fresh
- Open Adventure - Load existing
- Save Adventure - Save current work
- Save As - Save with new name
- Export - Export to different formats
- Recent Files - Quick access

**Edit Menu**:
- Undo/Redo - Change history
- Cut/Copy/Paste - Standard editing
- Find/Replace - Search text
- Preferences - IDE settings

**View Menu**:
- Theme Selection - 5 color schemes (Dark, Light, Dracula, Nord, Monokai)
- Font Settings - Customize UI and editor fonts
- Zoom - Adjust text size
- Reset View - Default settings

**Tools Menu**:
- Validate Adventure - Check for errors
- Statistics - Adventure metrics
- Import/Export - Data management
- Batch Operations - Bulk edits

**Help Menu**:
- User Manual - This document
- Tutorial - Interactive guide
- Command Reference - Full command list
- About - Version info

#### Themes

Choose from 5 professionally designed themes:

1. **Dark** (default) - Easy on eyes, good for long sessions
2. **Light** - Traditional bright interface
3. **Dracula** - Purple and pink highlights
4. **Nord** - Cool blue and gray tones
5. **Monokai** - Warm brown and orange

**To change theme**: View → Theme → Select theme

#### Font Customization

Customize fonts separately for UI and editor:

**UI Fonts**: Menus, buttons, labels
- View → Font → Family/Size

**Editor Fonts**: Text areas, code views
- View → Editor Font → Family/Size

**Recommended fonts**:
- UI: Sans-serif (Arial, Helvetica, Ubuntu)
- Editor: Monospace (Courier New, Monaco, Consolas)

---

## Command Reference

### Movement Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **go [direction]** | move, walk, travel, head | `go north`, `move west` |
| **north** | n | `north`, `n` |
| **south** | s | `south`, `s` |
| **east** | e | `east`, `e` |
| **west** | w | `west`, `w` |
| **up** | u, climb, ascend | `up`, `climb` |
| **down** | d, descend | `down`, `descend` |
| **enter [place]** | step into | `enter cave`, `go in` |
| **exit [place]** | depart | `exit building`, `go out` |

### Observation Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **look** | l, examine room | `look`, `l` |
| **look at [object]** | examine, inspect, check | `look at sword` |
| **read [object]** | - | `read book` |
| **search [object]** | - | `search chest` |

### Inventory Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **inventory** | i, inv, items | `inventory`, `i` |
| **get [item]** | take, grab, pick up | `get sword` |
| **drop [item]** | discard, put down | `drop torch` |
| **wear [item]** | equip, put on | `wear armor` |
| **remove [item]** | unequip, take off | `remove helmet` |

### Combat Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **attack [target]** | hit, strike, fight, kill | `attack goblin` |
| **defend** | block, parry | `defend` |
| **flee** | run, escape | `flee` |
| **ready [weapon]** | wield, equip | `ready sword` |

### Interaction Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **talk to [npc]** | speak, chat, ask | `talk to merchant` |
| **give [item] to [npc]** | offer, hand | `give gold to guard` |
| **buy [item]** | purchase | `buy potion` |
| **sell [item]** | trade | `sell sword` |
| **open [object]** | unlock | `open chest` |
| **close [object]** | shut, lock | `close door` |
| **use [item]** | activate, apply | `use key` |
| **pull [object]** | yank, tug | `pull lever` |
| **push [object]** | press, shove | `push button` |

### Consumption Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **eat [food]** | consume, devour | `eat bread` |
| **drink [liquid]** | sip, gulp | `drink potion` |

### Party Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **recruit [npc]** | hire, employ, invite to party | `recruit warrior` |
| **dismiss [npc]** | fire, remove from party | `dismiss thief` |
| **order [npc] to [action]** | command, tell, instruct | `order bob to attack` |

### Information Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **help** | ?, commands | `help` |
| **status** | stats, character, health | `status` |
| **journal** | log, quest log | `journal` |
| **map** | - | `map` |
| **time** | - | `time` |
| **score** | points | `score` |

### Game Control Commands

| Command | Synonyms | Example |
|---------|----------|---------|
| **save** | - | `save` |
| **load** | - | `load` |
| **quit** | exit, q | `quit` |

### Natural Language Examples

The parser understands conversational input:

- "what am I carrying?" → inventory
- "tell alice to defend" → order alice to defend
- "leave the heavy armor" → drop armor
- "go inside" → enter
- "look around" → look
- "talk with the merchant" → talk to merchant

---

## Creating Adventures

### Adventure Structure

Every adventure consists of:

1. **Metadata** - Title, author, description, version
2. **Rooms** - Locations with descriptions and exits
3. **Items** - Objects players can interact with
4. **NPCs** - Non-player characters
5. **Quests** (optional) - Objectives and progression
6. **Events** (optional) - Scripted sequences

### Room Design Best Practices

#### Good Room Description
```
You stand in a torch-lit hall with stone walls. Ancient tapestries 
depicting battles hang along the walls. A wooden door stands to the 
north, and a narrow passageway leads east.
```

#### Tips
- Use sensory details (sight, sound, smell)
- Mention visible exits
- Note important items or NPCs
- Create atmosphere
- Keep it concise (2-4 sentences)

#### Exit Configuration

Always define two-way exits:
- If Room A has "north" → Room B
- Then Room B should have "south" → Room A

Special exits:
- **up/down** - Stairs, ladders, cliffs
- **in/out** - Buildings, caves
- **secret** - Hidden passages (discovered via search)

### Item Design

#### Item Properties

| Property | Description | Example |
|----------|-------------|---------|
| **Name** | Unique identifier | "ancient_sword" |
| **Description** | What it looks like | "A rusty blade with runes" |
| **Weight** | Encumbrance (kg) | 3 |
| **Value** | Gold pieces | 50 |
| **Takeable** | Can be picked up | true |
| **Wearable** | Can be equipped | true |
| **Edible** | Can be eaten | false |
| **Drinkable** | Can be drunk | false |
| **Damage** | Attack bonus | +5 |
| **Armor** | Defense bonus | 0 |
| **Special** | Custom effects | "glows in dark" |

#### Item Types

1. **Weapons** - Swords, axes, bows
   - Set damage value (1-20+)
   - Add special effects (fire, poison)
   - Define required skill

2. **Armor** - Helmets, shields, chainmail
   - Set armor rating (1-10+)
   - Assign slots (head, chest, hands)
   - Note movement penalties

3. **Consumables** - Potions, food, scrolls
   - Mark as edible/drinkable
   - Define effects (heal, buff, debuff)
   - Single use or limited uses

4. **Quest Items** - Keys, letters, artifacts
   - Mark as not-droppable (optional)
   - Unique descriptions
   - Trigger events when used

5. **Treasures** - Gold, gems, art
   - High value, low weight
   - No special properties
   - Used for scoring

### NPC Design

#### NPC Properties

| Property | Description | Range |
|----------|-------------|-------|
| **Name** | Identifier | "guard_01" |
| **Display Name** | Shown to player | "Guard Captain" |
| **Description** | Appearance | "Tall, armored figure" |
| **Friendliness** | Attitude | -100 (hostile) to 100 (ally) |
| **Health** | Hit points | 10-100+ |
| **Damage** | Attack power | 1-20+ |
| **Armor** | Defense | 0-10+ |
| **AI Type** | Behavior | friendly, hostile, merchant, guard |
| **Dialogue** | Speech options | List of responses |
| **Inventory** | Items carried | List of items |

#### NPC Types

1. **Friendly NPCs**
   - Give quests and information
   - Offer help or items
   - Join party
   - Friendliness: 50-100

2. **Hostile NPCs**
   - Attack on sight or provocation
   - Guard treasures or areas
   - Drop loot when defeated
   - Friendliness: -100 to -50

3. **Merchants**
   - Buy and sell items
   - Have limited gold
   - Restock periodically
   - Friendliness: 25-75

4. **Guards**
   - Neutral by default
   - Become hostile if attacked
   - Enforce rules (no stealing)
   - Friendliness: 0-50

5. **Quest Givers**
   - Provide objectives
   - Reward completion
   - Track progress
   - Friendliness: 50-100

#### Dialogue System

NPCs can have multiple dialogue options:

```json
"dialogue": [
  "Hello, traveler! Welcome to our village.",
  "I need help finding my lost cat. Will you assist?",
  "The old castle is dangerous. Many enter, few return.",
  "Thank you for your help! Here's a reward."
]
```

Dialogue rotates or is context-sensitive.

### Quest System

#### Quest Structure

```json
"quests": [
  {
    "id": "find_sword",
    "name": "The Lost Sword",
    "description": "Find the legendary sword in the ruins",
    "objectives": [
      "Enter the ruins",
      "Defeat the guardian",
      "Retrieve the sword"
    ],
    "rewards": {
      "gold": 100,
      "experience": 50,
      "items": ["magic_ring"]
    },
    "giver": "old_wizard",
    "required_level": 1
  }
]
```

#### Quest Types

1. **Fetch Quests** - Retrieve items
2. **Combat Quests** - Defeat enemies
3. **Exploration Quests** - Discover locations
4. **Dialogue Quests** - Talk to NPCs
5. **Puzzle Quests** - Solve riddles

### Environmental Effects

Add atmosphere and challenge:

- **Weather** - Rain, snow, fog (affects visibility)
- **Lighting** - Dark rooms (need torch)
- **Temperature** - Heat/cold (need protection)
- **Hazards** - Poison gas, lava, traps
- **Time** - Day/night cycle

Configure in Room properties:
- Light level: 0 (dark) to 10 (bright)
- Temperature: -50 to 50 (Celsius)
- Hazard type: none, poison, fire, ice, trap

---

## Playing Adventures

### Starting a Game

**From IDE**:
1. Open adventure in IDE
2. Go to **Play** tab
3. Click **Start/Resume Adventure**

**Launch the IDE from terminal**:
```bash
python -m src.acs.ui.ide
# Select adventure from the launcher menu
```

> Legacy note: the standalone command-line engine has been retired. Use the IDE play tab for testing and gameplay.

### Game Interface

```
=== THE DARK TOWER ===
by Honey Badger

You stand in a torch-lit hallway...

Exits: north, east
Items: torch, key
NPCs: guard

> look at guard
A stern guard in chainmail armor. He watches you suspiciously.

> get key
You take the rusty key.

> go north
```

### Saving and Loading

**Save Game**:
- Type `save` during gameplay
- Saves to `saves/[adventure_name]_save.json`
- Preserves all progress, inventory, stats

**Load Game**:
- Type `load` during gameplay
- Restores last save
- Continue where you left off

**Multiple Saves** (advanced):
```bash
# Manual save naming
save my_save_slot1

# Load specific save
load my_save_slot1
```

### Tips for Players

1. **Explore Thoroughly**
   - `look` in every room
   - `search` objects and furniture
   - `examine` everything

2. **Talk to Everyone**
   - NPCs give hints and quests
   - Some have unique dialogue
   - Friendliness affects responses

3. **Manage Inventory**
   - Check weight limits
   - Drop unnecessary items
   - Organize before combat

4. **Combat Strategy**
   - `ready` your best weapon
   - `wear` armor before fights
   - `defend` against strong enemies
   - `flee` if overwhelmed

5. **Use the Journal**
   - Type `journal` to see quests
   - Review objectives
   - Track progress

6. **Save Often**
   - Before dangerous areas
   - After major progress
   - Before experimenting

---

## Customization

### IDE Customization

#### Themes

**Available Themes**:
1. **Dark** - Black background, white text
2. **Light** - White background, black text
3. **Dracula** - Purple, pink, cyan highlights
4. **Nord** - Cool blues and grays
5. **Monokai** - Warm browns and oranges

**Change Theme**:
- View → Theme → [Select Theme]
- Changes apply immediately
- Saved to preferences

#### Fonts

**UI Font** (menus, buttons):
- View → Font → Family
- View → Font → Size
- Recommended: Sans-serif, 9-11pt

**Editor Font** (text areas):
- View → Editor Font → Family
- View → Editor Font → Size
- Recommended: Monospace, 10-12pt

**Reset to Defaults**:
- View → Reset View Settings

### Adventure Customization

#### Configuration Files

Adventures are stored as JSON:

```json
{
  "title": "My Adventure",
  "author": "Your Name",
  "version": "1.0",
  "difficulty": "medium",
  "settings": {
    "combat_enabled": true,
    "permadeath": false,
    "time_limit": null,
    "starting_gold": 100
  },
  "rooms": {...},
  "items": {...},
  "npcs": {...}
}
```

Edit directly or use IDE.

#### Plugin System

Add custom features via plugins:

1. **Browse Plugins**:
   - Tools → Plugin Manager
   - View available plugins

2. **Install Plugin**:
   - Select plugin
   - Click Install
   - Restart IDE

3. **Create Plugin** (advanced):
   - See `docs/PLUGIN_GUIDE.md`
   - Python programming required

---

## Troubleshooting

### Common Issues

#### IDE Won't Launch

**Problem**: `python -m src.acs.ui.ide` fails

**Solutions**:
1. Check Python version: `python --version` (need 3.10+)
2. Install Tkinter (Linux): `sudo apt-get install python3-tk`
3. Launch via quickstart: `./quickstart.sh` → **Launch IDE**
4. Ensure virtual environment is activated if you created one

#### Adventure Won't Load

**Problem**: "Error loading adventure file"

**Solutions**:
1. Check JSON syntax (use validator: jsonlint.com)
2. Ensure all required fields present
3. Check file permissions
4. Try opening sample adventure first

#### Commands Not Working

**Problem**: "I don't understand that command"

**Solutions**:
1. Type `help` for command list
2. Try synonyms (e.g., `get` vs `take`)
3. Check spelling
4. Use natural language ("what am I carrying?")
5. Review Command Reference section

#### Game Crashes

**Problem**: Unexpected error during gameplay

**Solutions**:
1. Check console for error messages
2. Try loading last save
3. Validate adventure: Tools → Validate Adventure
4. Report bug with error details

#### Performance Issues

**Problem**: Slow or laggy IDE

**Solutions**:
1. Close unused tabs
2. Reduce font sizes
3. Disable animations (in preferences)
4. Save and restart IDE
5. Check system resources

### Getting Help

**Documentation**:
- User Manual (this file)
- Technical Reference (`docs/TECHNICAL_REFERENCE.md`)
- Command Reference (`docs/COMMANDS.md`)

**Community**:
- GitHub Issues: Report bugs
- Discord: Join community (link in README)
- Forums: Ask questions

**Contact**:
- Email: support@honeybadgeruniverse.com
- GitHub: github.com/James-HoneyBadger/SagaCraft

---

## Advanced Features

### Achievement System

Track player accomplishments:

**View Achievements**:
- Type `achievements` in-game
- Shows unlocked and locked

**Create Custom Achievements** (IDE):
1. Tools → Achievement Editor
2. Add achievement
3. Set trigger conditions
4. Define rewards

### Journal System

Automatic quest tracking:

**Features**:
- Quest log with objectives
- Location notes
- NPC relationships
- Item catalog
- Combat history

**Usage**:
- Type `journal` to view
- Automatically updates
- Searchable entries

### Context-Aware NPCs

NPCs remember interactions:

**NPC Memory**:
- Conversations affect relationship
- Past actions influence behavior
- Quests change dialogue
- Gifts improve friendliness

**Example**:
```
> talk to guard
Guard: "State your business!"

> give gold to guard
Guard: "Thank you, friend. You may pass."
[Guard friendliness increased]

> talk to guard
Guard: "Hello again, friend."
```

### Dynamic Environment

Living, changing world:

**Features**:
- Day/night cycle
- Weather changes
- NPC schedules
- Item respawning
- Random events

**Configuration**:
- Edit adventure JSON
- Set update intervals
- Define event triggers

### Modding Support

Extend adventures with mods:

**Mod Types**:
1. **Content Mods** - New items, NPCs, rooms
2. **Mechanic Mods** - Custom game rules
3. **Visual Mods** - Themes and graphics
4. **Audio Mods** - Sound effects, music

**Install Mods**:
1. Download mod file
2. Place in `mods/` directory
3. Enable in IDE: Tools → Mod Manager
4. Restart adventure

### Scripting System

Add custom logic:

**Event Scripts**:
```python
# On room enter
def on_enter_room(room_id):
    if room_id == "throne_room" and not has_item("crown"):
        spawn_npc("king")
        show_message("The king awaits...")
```

**Trigger Types**:
- Room entry/exit
- Item pickup/use
- NPC interaction
- Combat events
- Time-based

**Scripting Guide**: See `docs/SCRIPTING_GUIDE.md`

---

## Appendices

### Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Adventure |
| Ctrl+O | Open Adventure |
| Ctrl+S | Save Adventure |
| Ctrl+Q | Quit IDE |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+F | Find |
| Ctrl+H | Replace |
| F1 | Help |
| F5 | Validate Adventure |

### Appendix B: File Formats

**Adventure File** (`.json`):
- JSON format
- UTF-8 encoding
- Gzip compression optional

**Save File** (`.json`):
- JSON format
- Includes game state
- Compatible across versions

**Config File** (`.yaml`):
- YAML format
- User preferences
- Plugin settings

### Appendix C: Glossary

- **NPC** - Non-Player Character
- **HP** - Hit Points (health)
- **XP** - Experience Points
- **AI** - Artificial Intelligence (NPC behavior)
- **JSON** - JavaScript Object Notation (file format)
- **IDE** - Integrated Development Environment

### Appendix D: Credits

**Adventure Creation System**:
- Developed by Honey Badger Universe (2025)
- Licensed under MIT License
- Built with Python and Tkinter

**Special Thanks**:
- Interactive fiction community for inspiration
- Beta testers and contributors
- Open source community

---

## License

This software is licensed under the MIT License.

Copyright © 2025 Honey Badger Universe

See LICENSE file for full text.

---

**End of User Manual**

For technical documentation, see `docs/TECHNICAL_REFERENCE.md`  
For development guide, see `docs/CONTRIBUTING.md`  
For quick reference, see `docs/QUICKSTART.md`
