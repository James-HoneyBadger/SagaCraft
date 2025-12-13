# Enhanced Adventure System - Quick Start Guide

## Overview

SagaCraft includes powerful features for creating rich interactive fiction experiences.

## What's New?

### 🧩 Puzzles
- Locked doors requiring keys
- Riddles to solve
- Combination locks
- Hidden objects to find
- Multi-step puzzle chains

### 💬 Dialogue System
- Talk to NPCs with branching conversations
- Multiple dialogue topics
- Quest-giving NPCs
- Reputation system
- Dynamic responses

### 📜 Quest System
- Main and side quests
- Multiple objectives per quest
- Quest tracking
- Rewards (gold, XP, items)
- Quest chains

### 🎒 Enhanced Inventory
- Container items (backpacks, chests)
- Equipment slots (weapon, armor, accessories)
- Item durability
- Special item abilities
- Quest items

### ⚔️ Improved Combat
- Equipment bonuses
- Special abilities
- Better AI behavior
- Item drops from monsters

### 🌟 Character Progression
- Experience points and leveling
- Stat improvements
- Equipment system
- Spell learning

### 💾 Save/Load System
- Multiple save slots
- Save anywhere (if enabled)
- Auto-save support

## Playing Enhanced Adventures

### New Commands

**Dialogue:**
- `talk <npc>` - Start conversation with NPC
- `talk to <npc>` - Alternative syntax
- `ask <npc> about <topic>` - Ask about specific topic

**Inventory:**
- `examine <item>` - Detailed item examination
- `use <item>` - Use an item (unlock doors, read books, drink potions)
- `equip <item>` - Equip weapon/armor
- `unequip <item>` - Remove equipped item

**Puzzles:**
- `solve <answer>` - Answer riddles
- `unlock <direction>` - Try to unlock doors
- `search` - Search room for hidden items

**Quests:**
- `quests` - Show active quests
- `quest <number>` - Show details of specific quest

**Save/Load:**
- `save` or `save <slot>` - Save game
- `load <slot>` - Load saved game

### Original Commands Still Work!
All standard adventure commands work as expected:
- Movement: n, s, e, w, u, d
- Actions: look, get, drop, attack
- Info: inventory, status, help

## Creating Enhanced Adventures

### Basic Structure

```json
{
  "title": "My Adventure",
  "author": "Your Name",
  "intro": "Welcome text",
  "start_room": 1,
  "rooms": [...],
  "items": [...],
  "monsters": [...]
}
```

**This still works perfectly!** No changes needed for original adventures.

### Enhanced Structure (Optional Additions)

```json
{
  "title": "My Enhanced Adventure",
  "author": "Your Name",
  "intro": "Welcome text",
  "start_room": 1,
  
  "settings": {
    "allow_save": true,
    "enable_puzzles": true,
    "enable_magic": true
  },
  
  "rooms": [...],
  "items": [...],
  "monsters": [...],
  
  "puzzles": [...],      // Optional
  "dialogues": [...],    // Optional
  "quests": [...]        // Optional
}
```

## Enhanced Item Example

### Simple (Original - Still Works)
```json
{
  "id": 1,
  "name": "sword",
  "description": "A sharp blade",
  "type": "weapon",
  "weight": 5,
  "value": 50,
  "is_weapon": true,
  "location": 1
}
```

### Enhanced (Optional Additions)
```json
{
  "id": 1,
  "name": "magic sword",
  "description": "A glowing blade of power",
  "type": "weapon",
  "weight": 5,
  "value": 500,
  "is_weapon": true,
  "location": 1,
  
  "can_be_equipped": true,
  "equipment_slot": "weapon",
  "magical_bonus": 3,
  "special_abilities": ["light_source", "fire_damage"],
  "durability": 100
}
```

## Adding a Puzzle

```json
{
  "id": 1,
  "type": "locked_door",
  "room_id": 5,
  "description": "A locked iron door",
  "exit_direction": "north",
  "required_item": 12,
  "success_message": "The door unlocks!",
  "failure_message": "You need a key."
}
```

**Puzzle Types:**
- `locked_door` - Requires a key item
- `riddle` - Answer a riddle
- `combination` - Enter combination
- `hidden_object` - Find hidden item

## Adding NPC Dialogue

```json
{
  "npc_id": 3,
  "greeting": "Hello, traveler!",
  "topics": [
    {
      "keyword": "quest",
      "response": "I need help finding my lost ring...",
      "unlocks_quest": 1
    },
    {
      "keyword": "directions",
      "response": "The dungeon lies to the north.",
      "changes_reaction": 5
    }
  ],
  "farewell": "Safe travels!"
}
```

## Adding a Quest

```json
{
  "id": 1,
  "title": "Find the Lost Ring",
  "description": "Help the merchant find his lost ring",
  "giver_npc": 3,
  "objectives": [
    {
      "type": "collect_item",
      "target_id": 25,
      "quantity": 1,
      "description": "Find the lost ring"
    }
  ],
  "rewards_gold": 100,
  "rewards_experience": 50,
  "status": "not_started"
}
```

## Using the Enhanced IDE

### New IDE Features (Coming Soon)
- Puzzles Tab - Visual puzzle creator
- Quests Tab - Quest chain designer
- Dialogues Tab - Conversation tree builder
- Enhanced Items Tab - Set special abilities
- Enhanced Monsters Tab - Configure AI and dialogue

### Current IDE Still Works!
The existing IDE fully supports creating enhanced adventures. Just edit the JSON to add new fields.

## Backward Compatibility

### Original Adventures
✅ Work exactly as before
✅ No changes needed
✅ All commands work the same
✅ Same gameplay experience

### DSK Imports
✅ Import Apple II disk images as before
✅ Converted adventures are playable
✅ Can enhance converted adventures manually
✅ Original game mechanics preserved

### Mixing Old and New
✅ Add enhanced features gradually
✅ Start with original, add puzzles/quests later
✅ Enhanced and original content work together
✅ Players can use original OR enhanced commands

## Example Enhanced Adventure

See `adventures/colossal_storyworks_showcase.json` for a complete example featuring:
- Multiple districts with varied light levels and environmental effects
- NPCs offering dialogue, trading, and quest hooks
- Multi-step questlines with optional objectives
- Puzzle variety including locks, riddles, and sequencing logic
- Enhanced items with durability, special abilities, and equipment slots
- Container items and environmental storytelling objects
- Integrated achievement tracking and journal entries

## Testing Enhanced Features

### In the IDE
1. Load `colossal_storyworks_showcase.json`
2. Go to Play Adventure tab
3. Click "▶ Start Game"
4. Try these commands:
   - `talk master eldrin`
   - `ask eldrin about quest`
   - `get key`
   - `unlock north`
   - `quests`
   - `search` (in storage room)

### Creating Your Own
1. Start with a simple original adventure
2. Add one feature at a time:
   - Add a puzzle first
   - Then try adding dialogue
   - Then add a quest
   - Finally add enhanced items
3. Test after each addition
4. Build complexity gradually

## Tips for Adventure Creators

### Start Simple
- Begin with standard adventure format
- Add one enhanced feature at a time
- Test thoroughly before adding more
- Keep backup copies

### Use Enhanced Features Sparingly
- Not every adventure needs all features
- A few good puzzles > many mediocre ones
- Quality dialogue > quantity
- Simple can be better

### Maintain Balance
- Don't make puzzles too hard
- Give hints in descriptions
- Test with fresh eyes
- Get feedback from players

### Think About Story
- Enhanced features support storytelling
- Use quests to guide players
- Use dialogue to build characters
- Use puzzles to create memorable moments

## Common Patterns

### Simple Lock and Key
```json
// Add key item
{"id": 10, "name": "brass key", "is_key": true, "location": 5}

// Add puzzle
{"id": 1, "type": "locked_door", "room_id": 3, 
 "exit_direction": "north", "required_item": 10}
```

### Quest-Giving NPC
```json
// Monster with dialogue
{"id": 1, "name": "mayor", "friendliness": "friendly", 
 "dialogue_id": 1, "gives_quests": [1]}

// Dialogue
{"npc_id": 1, "topics": [
  {"keyword": "quest", "unlocks_quest": 1}
]}

// Quest
{"id": 1, "title": "Help the Town", 
 "giver_npc": 1, "objectives": [...]}
```

### Container with Treasure
```json
{
  "id": 20,
  "name": "treasure chest",
  "is_container": true,
  "container_capacity": 100,
  "contains_items": [21, 22, 23],
  "location": 10
}
```

## Performance Considerations

### File Size
- Enhanced adventures are slightly larger
- Typical: 20-50 KB (vs 10-20 KB original)
- Still very reasonable
- Loads instantly

### Complexity
- Game engine handles 100+ rooms easily
- 50+ items work fine
- 20+ NPCs with dialogue okay
- Performance is excellent

## Future Enhancements

Coming soon:
- Enhanced IDE with visual editors
- More puzzle types
- Magic spell system
- Crafting system
- More special abilities
- Sound effects support
- ASCII art support

## Getting Help

### Documentation
- `ENHANCEMENT_PLAN.md` - Full feature roadmap
- `README.md` - Basic system info
- `IDE_GUIDE.md` - IDE usage
- This file - Enhanced features

### Examples
- `colossal_storyworks_showcase.json` - Comprehensive enhanced example
- Compare against your own legacy adventures to see differences

### Community
- Share your enhanced adventures!
- Report bugs or issues
- Suggest new features
- Help other creators

## Quick Reference

### Enhanced Item Fields
- `magical_bonus` - Bonus to combat/stats
- `special_abilities` - List of abilities
- `can_be_equipped` - Can equip item
- `equipment_slot` - Where it equips
- `is_container` - Holds other items
- `contains_items` - IDs of contained items
- `durability` - Current durability
- `on_use_effect` - What happens when used

### Enhanced Monster Fields
- `dialogue_id` - Link to dialogue
- `can_trade` - Can trade with player
- `gives_quests` - Quest IDs NPC gives
- `reaction_level` - How friendly (-100 to 100)
- `special_abilities` - Special powers
- `ai_behavior` - How monster acts
- `drops_items_on_death` - Item drops

### Enhanced Room Fields
- `light_level` - bright/normal/dim/dark
- `requires_light_source` - Need torch/light
- `has_trap` - Room has a trap
- `hidden_items` - Items revealed by search
- `is_safe_zone` - No combat allowed
- `alternate_description` - Conditional desc

---

**Ready to enhance?** Start with the example adventure, then create your own enhanced content!

**Remember:** All standard adventure features still work perfectly. Enhanced features are completely optional!
