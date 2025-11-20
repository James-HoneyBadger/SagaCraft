# Quick Start Guide

**Get up and running in 5 minutes!**

Copyright © 2025 Honey Badger Universe  
License: MIT

---

## Installation (30 seconds)

```bash
# Requirements: Python 3.6+
cd HB_Adventure_Games
python3 -m src.acs.ui.ide
```

That's it! No dependencies to install.

---

## Your First Adventure (5 minutes)

### Step 1: Launch IDE
```bash
python3 -m src.acs.ui.ide
```

### Step 2: Create New Adventure
1. Click **File → New Adventure**
2. Enter title: "My First Quest"
3. Enter author: Your name
4. Click OK

### Step 3: Create Starting Room
1. Go to **Rooms** tab
2. Click **Add Room**
3. Name: `entrance`
4. Description: `You stand in a small cave with rough stone walls.`
5. Click Save

### Step 4: Add an Item
1. Go to **Items** tab
2. Click **Add Item**
3. Name: `torch`
4. Description: `A wooden torch that provides light`
5. Weight: `1`
6. Value: `5`
7. Check ✓ **Takeable**
8. Click Save

### Step 5: Add NPC
1. Go to **NPCs** tab
2. Click **Add NPC**
3. Name: `wizard`
4. Description: `An old wizard with a long white beard`
5. Friendliness: `75` (friendly)
6. Health: `50`
7. Click Save

### Step 6: Place Items/NPCs in Room
1. Back to **Rooms** tab
2. Select `entrance` room
3. Add `torch` to room items
4. Add `wizard` to room NPCs
5. Click Update

### Step 7: Play!
1. Go to **Play** tab
2. Click **Start/Resume Adventure**
3. Try these commands:
   ```
   > look
   > get torch
   > talk to wizard
   ```

### Step 8: Save Your Work
1. Click **File → Save Adventure**
2. Name it `my_first_quest.json`
3. It's saved in `adventures/` directory

---

## Essential Commands

| Command | What It Does | Example |
|---------|--------------|---------|
| `look` | Describe current room | `look` |
| `go [dir]` | Move direction | `go north` |
| `get [item]` | Pick up item | `get torch` |
| `inventory` | Show what you carry | `inventory` |
| `talk to [npc]` | Talk to character | `talk to wizard` |
| `help` | Show all commands | `help` |

**Shortcuts**: `n`=north, `s`=south, `e`=east, `w`=west, `i`=inventory, `l`=look

---

## Next Steps

### Play Sample Adventures
```bash
python3 -m src.acs.ui.ide
# Select from menu
```

### Learn More Commands
See [Command Reference](../reference/COMMANDS.md) for all 30 commands

### Read Full Manual
See [User Manual](USER_MANUAL.md) for everything

### Customize IDE
- **View → Theme** - Try different color schemes
- **View → Font** - Adjust text size

---

## Tips

✅ **Save often** - Click File → Save regularly  
✅ **Test as you build** - Use Play tab to test  
✅ **Use natural language** - "what am I carrying?" works!  
✅ **Define two-way exits** - If north goes to room B, room B should have south back  
✅ **Check the journal** - Type `journal` in-game for quest tracking  

---

## Troubleshooting

**IDE won't start?**
```bash
# Check Python version (need 3.6+)
python3 --version

# Try without '3'
python3 -m src.acs.ui.ide
```

**Command not recognized?**
- Type `help` for command list
- Try synonyms: `get` = `take` = `grab`
- Use natural language: "pick up the sword"

**Adventure won't load?**
- Check JSON syntax (use jsonlint.com)
- Look for missing commas/brackets
- Try loading sample adventure first

---

## Sample Adventure Code

Want to see a complete adventure? Open `adventures/sample_adventure.json`:

```json
{
  "title": "Sample Quest",
  "author": "Honey Badger",
  "settings": {
    "starting_room": "entrance"
  },
  "rooms": {
    "entrance": {
      "description": "A small cave entrance...",
      "exits": {"north": "hall"},
      "items": ["torch"],
      "npcs": []
    },
    "hall": {
      "description": "A long hallway...",
      "exits": {"south": "entrance"},
      "items": [],
      "npcs": ["guard"]
    }
  },
  "items": {
    "torch": {
      "description": "A wooden torch",
      "weight": 1,
      "value": 5,
      "takeable": true
    }
  },
  "npcs": {
    "guard": {
      "display_name": "Castle Guard",
      "description": "A stern guard",
      "health": 50,
      "friendliness": 0
    }
  }
}
```

---

## Get Help

- **User Manual**: Full documentation
- **GitHub Issues**: Report bugs
- **Discord**: Community chat (link in README)
- **Email**: support@honeybadgeruniverse.com

---

**Ready to create amazing adventures!** 🎮

For detailed information, see [User Manual](USER_MANUAL.md)
