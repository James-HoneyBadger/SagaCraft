# 🎮 Game Creation Guide

**Adventure Construction Set - Complete Creator's Guide**

Learn how to create your own text adventures from scratch using the ACS toolset.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding the JSON Format](#understanding-the-json-format)
3. [Creating Your First Adventure](#creating-your-first-adventure)
4. [Designing Rooms](#designing-rooms)
5. [Adding Items](#adding-items)
6. [Creating NPCs](#creating-npcs)
7. [Implementing Quests](#implementing-quests)
8. [Advanced Features](#advanced-features)
9. [Testing Your Game](#testing-your-game)
10. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### Method 1: Using the Graphical IDE (Recommended)

```bash
python -m src.acs.ui.ide
```

The IDE provides a visual interface for creating adventures without writing JSON manually.

### Method 2: Manual JSON Creation

1. Copy an existing adventure as a template
2. Edit the JSON file in your favorite text editor
3. Test your adventure with `python -m src.acs.ui.ide`

---

## 📖 Understanding the JSON Format

Every adventure is a single JSON file with this structure:

```json
{
  "metadata": { /* Game info */ },
  "rooms": [ /* All locations */ ],
  "items": [ /* All objects */ ],
  "npcs": [ /* All characters */ ],
  "quests": [ /* All objectives */ ]
}
```

### Minimum Required Structure

```json
{
  "metadata": {
    "title": "Your Adventure Title",
    "author": "Your Name",
    "description": "A brief description",
    "version": "1.0"
  },
  "rooms": [
    {
      "id": 1,
      "name": "Starting Room",
      "description": "Your first room description.",
      "exits": {}
    }
  ],
  "items": [],
  "npcs": [],
  "quests": []
}
```

---

## 🎬 Creating Your First Adventure

### Step 1: Set Up the Metadata

```json
{
  "metadata": {
    "title": "Mystery of the Ancient Temple",
    "author": "Your Name",
    "description": "Explore an ancient temple filled with puzzles and treasures.",
    "version": "1.0",
    "start_room": 1,
    "intro_text": "You stand before the entrance of an ancient temple...",
    "max_weight": 100,
    "start_gold": 50
  }
}
```

**Metadata Fields:**
- `title` - Name of your adventure (required)
- `author` - Your name (required)
- `description` - Brief summary (required)
- `version` - Version number (recommended)
- `start_room` - Room ID where players begin (default: 1)
- `intro_text` - Opening message (optional)
- `max_weight` - Maximum carry weight (default: 100)
- `start_gold` - Starting gold amount (default: 100)

### Step 2: Create Your First Room

```json
{
  "rooms": [
    {
      "id": 1,
      "name": "Temple Entrance",
      "description": "Massive stone pillars frame the entrance to an ancient temple. Vines crawl up the weathered walls, and the air smells of age and mystery.",
      "exits": {
        "north": 2,
        "east": 3
      },
      "items": [1, 2],
      "npcs": [],
      "visited": false
    }
  ]
}
```

**Room Fields:**
- `id` - Unique number (required, start at 1)
- `name` - Short room title (required)
- `description` - Full description (required)
- `exits` - Dictionary of direction: room_id (required)
- `items` - List of item IDs in this room (default: [])
- `npcs` - List of NPC IDs in this room (default: [])
- `visited` - Has player been here? (default: false)
- `light_level` - 0-10, 0 is pitch black (default: 10)
- `safe_room` - No combat allowed (default: false)

**Valid Exit Directions:**
- `north`, `south`, `east`, `west`
- `up`, `down`
- `northeast`, `northwest`, `southeast`, `southwest`
- `in`, `out`

---

## 🗺️ Designing Rooms

### Room Design Principles

1. **Write Vivid Descriptions**
   - Use sensory details (sight, sound, smell)
   - Create atmosphere and mood
   - Keep descriptions 2-4 sentences

2. **Connect Logically**
   - Map out your rooms on paper first
   - Make exits make sense geographically
   - Use opposite exits (if north goes to room 2, room 2's south should return)

3. **Vary Room Types**
   - Safe rooms for resting
   - Dark rooms requiring light sources
   - Puzzle rooms
   - Combat areas
   - Treasure rooms

### Example: Multi-Room Area

```json
{
  "rooms": [
    {
      "id": 1,
      "name": "Temple Courtyard",
      "description": "An open courtyard with a cracked fountain in the center.",
      "exits": {"north": 2, "east": 3, "west": 4},
      "safe_room": true
    },
    {
      "id": 2,
      "name": "Main Hall",
      "description": "A grand hall with ancient murals on the walls.",
      "exits": {"south": 1, "up": 5}
    },
    {
      "id": 3,
      "name": "East Wing",
      "description": "A narrow corridor leading to small chambers.",
      "exits": {"west": 1},
      "light_level": 3
    },
    {
      "id": 4,
      "name": "West Wing",
      "description": "Collapsed rubble blocks further progress.",
      "exits": {"east": 1}
    },
    {
      "id": 5,
      "name": "Upper Gallery",
      "description": "A balcony overlooking the main hall.",
      "exits": {"down": 2}
    }
  ]
}
```

### Special Room Types

**Dark Rooms:**
```json
{
  "id": 10,
  "name": "Dark Cavern",
  "description": "Complete darkness surrounds you.",
  "light_level": 0,
  "exits": {"west": 9}
}
```

**Safe Rooms (No Combat):**
```json
{
  "id": 1,
  "name": "Sanctuary",
  "description": "A peaceful shrine radiating protective magic.",
  "safe_room": true,
  "exits": {"out": 2}
}
```

---

## 🎒 Adding Items

### Basic Item Structure

```json
{
  "id": 1,
  "name": "rusty sword",
  "description": "An old iron sword, still serviceable despite the rust.",
  "type": "weapon",
  "weight": 5,
  "value": 10,
  "takeable": true,
  "damage": 5
}
```

### Item Types

**Weapons:**
```json
{
  "id": 1,
  "name": "steel longsword",
  "description": "A well-crafted blade with excellent balance.",
  "type": "weapon",
  "weight": 8,
  "value": 100,
  "takeable": true,
  "damage": 10,
  "hands": 1
}
```

**Armor:**
```json
{
  "id": 2,
  "name": "leather armor",
  "description": "Supple leather armor that doesn't restrict movement.",
  "type": "armor",
  "weight": 10,
  "value": 50,
  "takeable": true,
  "armor_value": 5
}
```

**Light Sources:**
```json
{
  "id": 3,
  "name": "torch",
  "description": "A wooden torch wrapped in oil-soaked cloth.",
  "type": "light",
  "weight": 2,
  "value": 5,
  "takeable": true,
  "light_radius": 5,
  "fuel": 100
}
```

**Quest Items:**
```json
{
  "id": 4,
  "name": "ancient key",
  "description": "An ornate key covered in strange runes.",
  "type": "key",
  "weight": 1,
  "value": 0,
  "takeable": true,
  "quest_item": true,
  "unlocks": [5]
}
```

**Containers:**
```json
{
  "id": 5,
  "name": "wooden chest",
  "description": "A sturdy oak chest with iron bands.",
  "type": "container",
  "weight": 20,
  "value": 25,
  "takeable": false,
  "container": true,
  "locked": true,
  "contents": [6, 7, 8]
}
```

**Food/Healing:**
```json
{
  "id": 6,
  "name": "healing potion",
  "description": "A vial of glowing red liquid.",
  "type": "consumable",
  "weight": 1,
  "value": 30,
  "takeable": true,
  "healing": 20,
  "consumable": true
}
```

### Item Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `id` | int | Unique identifier | Required |
| `name` | string | Item name | Required |
| `description` | string | Full description | Required |
| `type` | string | Item category | "generic" |
| `weight` | int | Weight in pounds | 1 |
| `value` | int | Gold value | 0 |
| `takeable` | bool | Can be picked up | true |
| `visible` | bool | Can be seen | true |
| `damage` | int | Weapon damage | 0 |
| `armor_value` | int | Armor protection | 0 |
| `healing` | int | HP restored | 0 |
| `consumable` | bool | Single use item | false |
| `container` | bool | Can hold items | false |
| `locked` | bool | Requires key | false |
| `quest_item` | bool | Needed for quest | false |

---

## 👥 Creating NPCs

### Basic NPC Structure

```json
{
  "id": 1,
  "name": "Old Hermit",
  "description": "A weathered old man with kind eyes.",
  "friendliness": "friendly",
  "health": 50,
  "damage": 0,
  "armor": 0,
  "conversation": [
    "Welcome, traveler. This temple holds many secrets.",
    "Beware the guardian in the upper chambers.",
    "The ancient key lies hidden in the eastern wing."
  ],
  "inventory": [10],
  "gives_quest": 1
}
```

### NPC Friendliness Levels

**Friendly NPCs:**
```json
{
  "id": 1,
  "name": "Merchant",
  "description": "A jovial trader with a cart full of goods.",
  "friendliness": "friendly",
  "health": 30,
  "conversation": [
    "Welcome! Care to see my wares?",
    "I have the finest goods in the realm!"
  ],
  "trades": true,
  "inventory": [5, 6, 7]
}
```

**Neutral NPCs:**
```json
{
  "id": 2,
  "name": "Temple Guard",
  "description": "A stern-looking guard in ceremonial armor.",
  "friendliness": "neutral",
  "health": 80,
  "damage": 8,
  "armor": 10,
  "conversation": [
    "State your business.",
    "Only the worthy may pass."
  ],
  "blocks_exit": "north",
  "requires_item": 4
}
```

**Hostile NPCs:**
```json
{
  "id": 3,
  "name": "Stone Golem",
  "description": "A massive construct of animated stone.",
  "friendliness": "hostile",
  "health": 150,
  "damage": 15,
  "armor": 20,
  "conversation": [],
  "aggressive": true,
  "drops": [11, 12]
}
```

### NPC Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `id` | int | Unique identifier | Required |
| `name` | string | NPC name | Required |
| `description` | string | Full description | Required |
| `friendliness` | string | "friendly", "neutral", "hostile" | "neutral" |
| `health` | int | Hit points | 50 |
| `damage` | int | Attack damage | 5 |
| `armor` | int | Armor class | 0 |
| `conversation` | list | Dialog lines | [] |
| `inventory` | list | Item IDs carried | [] |
| `trades` | bool | Can trade items | false |
| `gives_quest` | int | Quest ID offered | null |
| `blocks_exit` | string | Blocks direction | null |
| `requires_item` | int | Item needed to pass | null |
| `aggressive` | bool | Attacks on sight | false |
| `drops` | list | Items dropped on death | [] |

### Advanced NPC Examples

**Quest Giver:**
```json
{
  "id": 4,
  "name": "High Priest",
  "description": "An elderly priest in flowing robes.",
  "friendliness": "friendly",
  "health": 40,
  "conversation": [
    "The temple has been defiled by dark forces.",
    "Retrieve the Sacred Amulet and I shall reward you.",
    "May the gods guide your path."
  ],
  "gives_quest": 1,
  "inventory": [20]
}
```

**Blocking NPC:**
```json
{
  "id": 5,
  "name": "Gate Keeper",
  "description": "A massive warrior blocking the gate.",
  "friendliness": "neutral",
  "health": 100,
  "damage": 12,
  "armor": 15,
  "conversation": [
    "None shall pass without the Royal Seal."
  ],
  "blocks_exit": "north",
  "requires_item": 8
}
```

**Companion:**
```json
{
  "id": 6,
  "name": "Elara the Brave",
  "description": "A skilled warrior seeking adventure.",
  "friendliness": "friendly",
  "health": 80,
  "damage": 10,
  "armor": 12,
  "conversation": [
    "I'll join you on your quest!",
    "Together we can defeat any foe!"
  ],
  "can_recruit": true,
  "inventory": [15]
}
```

---

## 🎯 Implementing Quests

### Basic Quest Structure

```json
{
  "id": 1,
  "name": "Retrieve the Sacred Amulet",
  "description": "Find the Sacred Amulet in the temple depths and return it to the High Priest.",
  "type": "fetch",
  "status": "available",
  "required_item": 25,
  "reward_gold": 500,
  "reward_items": [26],
  "completion_text": "You have restored the temple's sacred relic!"
}
```

### Quest Types

**Fetch Quests:**
```json
{
  "id": 1,
  "name": "Lost Heirloom",
  "description": "Recover the merchant's stolen ring.",
  "type": "fetch",
  "required_item": 12,
  "reward_gold": 100
}
```

**Kill Quests:**
```json
{
  "id": 2,
  "name": "Slay the Golem",
  "description": "Defeat the Stone Golem terrorizing the temple.",
  "type": "kill",
  "target_npc": 3,
  "reward_gold": 200,
  "reward_items": [15]
}
```

**Exploration Quests:**
```json
{
  "id": 3,
  "name": "Map the Temple",
  "description": "Explore all chambers of the ancient temple.",
  "type": "explore",
  "required_rooms": [1, 2, 3, 4, 5, 6, 7, 8],
  "reward_gold": 150
}
```

**Delivery Quests:**
```json
{
  "id": 4,
  "name": "Deliver the Message",
  "description": "Take this sealed letter to the guard captain.",
  "type": "delivery",
  "required_item": 18,
  "target_npc": 7,
  "reward_gold": 50
}
```

### Quest Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | int | Unique identifier |
| `name` | string | Quest name |
| `description` | string | Quest objective |
| `type` | string | "fetch", "kill", "explore", "delivery" |
| `status` | string | "available", "active", "completed" |
| `required_item` | int | Item ID to obtain |
| `target_npc` | int | NPC ID to kill/talk to |
| `required_rooms` | list | Room IDs to visit |
| `reward_gold` | int | Gold reward |
| `reward_items` | list | Item rewards |
| `reward_xp` | int | Experience reward |
| `completion_text` | string | Success message |

### Multi-Stage Quest Example

```json
{
  "id": 5,
  "name": "The Temple Mystery",
  "description": "Uncover the secrets of the ancient temple.",
  "type": "multi_stage",
  "stages": [
    {
      "stage": 1,
      "description": "Find the ancient journal",
      "required_item": 30
    },
    {
      "stage": 2,
      "description": "Decode the cryptic message",
      "required_item": 31
    },
    {
      "stage": 3,
      "description": "Confront the temple guardian",
      "target_npc": 10
    }
  ],
  "current_stage": 1,
  "reward_gold": 1000,
  "reward_items": [35]
}
```

---

## ⚡ Advanced Features

### Environmental Effects

**Weather:**
```json
{
  "id": 10,
  "name": "Mountain Peak",
  "description": "Howling winds whip around the exposed peak.",
  "environment": {
    "weather": "stormy",
    "temperature": "cold",
    "damage_per_turn": 2
  }
}
```

**Hazards:**
```json
{
  "id": 11,
  "name": "Toxic Swamp",
  "description": "Poisonous fumes rise from the murky water.",
  "environment": {
    "hazard": "poison",
    "damage_per_turn": 5,
    "requires_protection": 22
  }
}
```

### Locked Doors and Puzzles

**Key-Based Lock:**
```json
{
  "id": 15,
  "name": "Locked Treasury",
  "description": "A heavy iron door bars the way.",
  "exits": {
    "north": {
      "destination": 16,
      "locked": true,
      "requires_item": 8,
      "unlock_message": "The ancient key turns in the lock with a satisfying click."
    }
  }
}
```

**Puzzle Room:**
```json
{
  "id": 20,
  "name": "Riddle Chamber",
  "description": "An inscription reads: 'What walks on four legs in morning, two at noon, three at evening?'",
  "puzzle": {
    "type": "riddle",
    "answer": "man",
    "success_exit": 21,
    "failure_message": "The door remains sealed."
  }
}
```

### Custom Events

**Timed Events:**
```json
{
  "id": 25,
  "name": "Collapsing Tunnel",
  "description": "Cracks spread across the ceiling!",
  "event": {
    "type": "timed",
    "turns_remaining": 5,
    "on_expire": "room_destroyed",
    "warning_message": "Debris begins to fall!"
  }
}
```

**Trigger Events:**
```json
{
  "id": 30,
  "name": "Throne Room",
  "description": "An ornate throne sits on a raised dais.",
  "event": {
    "type": "trigger",
    "trigger_item": 12,
    "trigger_action": "use",
    "result": "spawn_npc",
    "spawn_npc_id": 15,
    "message": "The statue comes to life!"
  }
}
```

### Hidden Items and Secrets

```json
{
  "id": 35,
  "name": "Ancient Library",
  "description": "Dusty bookshelves line the walls.",
  "items": [40],
  "hidden_items": [
    {
      "item_id": 41,
      "hidden": true,
      "reveal_command": "search shelves",
      "reveal_message": "You find a hidden compartment!"
    }
  ]
}
```

---

## 🧪 Testing Your Game

### Pre-Release Checklist

**1. Test All Rooms:**
```bash
# Play through and visit every room
python -m src.acs.ui.ide
```

- [ ] All rooms are accessible
- [ ] All exits work correctly
- [ ] Room descriptions are clear
- [ ] No dead ends (unless intentional)

**2. Test All Items:**
- [ ] All items can be picked up (if takeable)
- [ ] Weapons work in combat
- [ ] Armor provides protection
- [ ] Consumables have effects
- [ ] Quest items trigger properly

**3. Test All NPCs:**
- [ ] Friendly NPCs don't attack
- [ ] Hostile NPCs engage in combat
- [ ] Conversations display correctly
- [ ] Quest givers offer quests
- [ ] Traders accept trades

**4. Test All Quests:**
- [ ] Quests can be accepted
- [ ] Objectives are clear
- [ ] Completion is recognized
- [ ] Rewards are given

**5. Test Edge Cases:**
- [ ] Player can't break sequence
- [ ] No soft-locks possible
- [ ] Weight limits work
- [ ] Gold economy is balanced

### Common Issues and Fixes

**Issue: Room Not Accessible**
```json
// BAD: Missing return exit
{
  "id": 1,
  "exits": {"north": 2}
}
{
  "id": 2,
  "exits": {"east": 3}  // No way back to room 1!
}

// GOOD: Two-way connection
{
  "id": 1,
  "exits": {"north": 2}
}
{
  "id": 2,
  "exits": {"south": 1, "east": 3}
}
```

**Issue: Items Not Appearing**
```json
// Make sure item ID is in room's items list
{
  "id": 1,
  "name": "Entrance Hall",
  "items": [1, 2]  // Items 1 and 2 will be here
}
```

**Issue: Quest Won't Complete**
```json
// Ensure quest requirements match available items/NPCs
{
  "id": 1,
  "required_item": 10  // Make sure item 10 exists!
}
```

---

## ✨ Best Practices

### Writing Engaging Descriptions

**Good Description:**
> "The chamber reeks of decay. Skeletal remains lie scattered across the cracked floor, and ancient tapestries hang in tatters from the walls. A faint draft suggests another passage hidden somewhere in the darkness."

**Poor Description:**
> "A room. There are bones. It's dark."

**Tips:**
- Use sensory details (smell, sound, texture)
- Create atmosphere
- Hint at secrets or dangers
- Keep it concise (2-4 sentences)

### Balancing Difficulty

**Combat Balance:**
```
Early Game:
- Enemy health: 20-50
- Enemy damage: 3-8
- Player weapons: 5-10 damage
- Player armor: 3-8 protection

Mid Game:
- Enemy health: 50-100
- Enemy damage: 8-15
- Player weapons: 10-20 damage
- Player armor: 8-15 protection

Late Game:
- Enemy health: 100-200
- Enemy damage: 15-25
- Player weapons: 20-35 damage
- Player armor: 15-25 protection
```

**Item Values:**
```
Common items: 1-50 gold
Uncommon items: 50-200 gold
Rare items: 200-500 gold
Epic items: 500-1000 gold
Legendary items: 1000+ gold
```

**Quest Rewards:**
```
Simple quests: 50-100 gold
Medium quests: 100-300 gold
Major quests: 300-500 gold
Epic quests: 500-1000 gold
```

### Pacing Your Adventure

**Adventure Length Guidelines:**

**Short Adventure (1-2 hours):**
- 10-15 rooms
- 5-10 items
- 3-5 NPCs
- 2-3 quests

**Medium Adventure (3-5 hours):**
- 20-35 rooms
- 15-25 items
- 8-12 NPCs
- 5-8 quests

**Long Adventure (5+ hours):**
- 35+ rooms
- 30+ items
- 15+ NPCs
- 10+ quests

### Design Patterns

**Tutorial Area:**
```json
{
  "id": 1,
  "name": "Training Grounds",
  "description": "A safe area to learn the basics.",
  "safe_room": true,
  "items": [1, 2],  // Basic weapon and armor
  "npcs": [1],      // Friendly trainer
  "exits": {"north": 2}
}
```

**Hub Area:**
```json
{
  "id": 5,
  "name": "Town Square",
  "description": "The heart of the village.",
  "safe_room": true,
  "exits": {
    "north": 6,   // To adventure area 1
    "east": 10,   // To adventure area 2
    "south": 15,  // To adventure area 3
    "west": 20    // To merchant district
  }
}
```

**Boss Room:**
```json
{
  "id": 50,
  "name": "Throne of the Lich King",
  "description": "A chamber pulsing with dark energy.",
  "npcs": [99],  // Final boss
  "items": [100, 101, 102],  // Epic loot
  "exits": {"south": 49}  // Only one entrance
}
```

---

## 📚 Example: Complete Mini-Adventure

Here's a complete, playable mini-adventure demonstrating all concepts:

```json
{
  "metadata": {
    "title": "The Cursed Crypt",
    "author": "Example Creator",
    "description": "A short adventure exploring a haunted crypt.",
    "version": "1.0",
    "start_room": 1,
    "intro_text": "Local villagers speak of a cursed crypt holding ancient treasure. Few who enter ever return...",
    "max_weight": 100,
    "start_gold": 50
  },
  "rooms": [
    {
      "id": 1,
      "name": "Crypt Entrance",
      "description": "Stone steps descend into darkness. The air grows cold as you approach the entrance.",
      "exits": {"down": 2},
      "items": [1],
      "safe_room": true
    },
    {
      "id": 2,
      "name": "Burial Chamber",
      "description": "Ancient sarcophagi line the walls. Cobwebs hang thick in every corner.",
      "exits": {"up": 1, "north": 3, "east": 4},
      "npcs": [1],
      "light_level": 3
    },
    {
      "id": 3,
      "name": "Treasure Room",
      "description": "Gold and jewels glitter in the dim light.",
      "exits": {"south": 2},
      "items": [2, 3, 4],
      "npcs": [2]
    },
    {
      "id": 4,
      "name": "Secret Chamber",
      "description": "A hidden room containing a mysterious altar.",
      "exits": {"west": 2},
      "items": [5]
    }
  ],
  "items": [
    {
      "id": 1,
      "name": "torch",
      "description": "A wooden torch.",
      "type": "light",
      "weight": 2,
      "value": 5,
      "takeable": true,
      "light_radius": 5,
      "fuel": 100
    },
    {
      "id": 2,
      "name": "silver sword",
      "description": "A blessed blade effective against undead.",
      "type": "weapon",
      "weight": 6,
      "value": 150,
      "takeable": true,
      "damage": 12
    },
    {
      "id": 3,
      "name": "gold coins",
      "description": "A pile of ancient gold coins.",
      "type": "treasure",
      "weight": 3,
      "value": 200,
      "takeable": true
    },
    {
      "id": 4,
      "name": "ruby amulet",
      "description": "A beautiful amulet set with a large ruby.",
      "type": "treasure",
      "weight": 1,
      "value": 500,
      "takeable": true,
      "quest_item": true
    },
    {
      "id": 5,
      "name": "healing potion",
      "description": "A vial of red liquid.",
      "type": "consumable",
      "weight": 1,
      "value": 30,
      "takeable": true,
      "healing": 25,
      "consumable": true
    }
  ],
  "npcs": [
    {
      "id": 1,
      "name": "Restless Skeleton",
      "description": "The bones of an ancient warrior, animated by dark magic.",
      "friendliness": "hostile",
      "health": 40,
      "damage": 6,
      "armor": 2,
      "aggressive": true,
      "drops": [2]
    },
    {
      "id": 2,
      "name": "Lich Lord",
      "description": "A powerful undead sorcerer guarding the treasure.",
      "friendliness": "hostile",
      "health": 80,
      "damage": 12,
      "armor": 5,
      "conversation": [
        "You dare disturb my eternal rest?",
        "Your soul shall join my collection!"
      ],
      "aggressive": true,
      "drops": [4]
    }
  ],
  "quests": [
    {
      "id": 1,
      "name": "Retrieve the Ruby Amulet",
      "description": "The village elder seeks a ruby amulet rumored to be in the crypt.",
      "type": "fetch",
      "status": "available",
      "required_item": 4,
      "reward_gold": 300,
      "completion_text": "The elder thanks you for recovering the sacred amulet!"
    }
  ]
}
```

Save this as `cursed_crypt.json` in the `adventures/` folder and play it!

---

## 🎓 Next Steps

1. **Start Simple** - Create a 3-5 room adventure to learn the basics
2. **Study Examples** - Look at the included adventures for inspiration
3. **Experiment** - Try different room layouts, puzzles, and combat scenarios
4. **Iterate** - Playtest and refine your adventure
5. **Share** - Submit your adventure to the community!

---

## 📖 Additional Resources

- **[User Manual](USER_MANUAL.md)** - Complete player and creator guide
- **[Command Reference](../reference/COMMANDS.md)** - All available commands
- **[Technical Reference](../reference/TECHNICAL_REFERENCE.md)** - JSON schema details
- **[IDE Guide](IDE_GUIDE.md)** - Using the graphical editor

---

## 💡 Quick Tips

- **Map it first** - Draw your room layout on paper
- **Balance is key** - Test combat encounters thoroughly
- **Tell a story** - Give players a reason to explore
- **Reward exploration** - Hide secrets and treasures
- **Playtest often** - Test every change you make
- **Keep backups** - Save versions of your work
- **Start small** - Better to finish a small adventure than abandon a huge one

---

**Happy Creating!** 🎮

Need help? Check the [User Manual](USER_MANUAL.md) or [Contributing Guide](../developer-guides/CONTRIBUTING.md)

Copyright © 2025 Honey Badger Universe | MIT License
