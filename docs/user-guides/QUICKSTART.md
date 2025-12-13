# Quick Start Guide

**Get up and running in 5 minutes!**

Copyright © 2025 Honey Badger Universe  
License: MIT

---

## Installation (30 seconds)

```bash
# Requirements: Python 3.10+
cd SagaCraft
python -m src.acs.ui.ide
```

- SagaCraft ships with batteries included—no mandatory dependencies.
- Optional: run `./quickstart.sh` for a menu of launch shortcuts.

---

## Your First Adventure (5 minutes)

### Step 1: Launch the IDE

```bash
python -m src.acs.ui.ide
```

### Step 2: Create a New Adventure
1. Click **File → New Adventure**
2. Title: `My First Quest`
3. Author: your name
4. Click **OK**

### Step 3: Add the Starting Room
1. Open the **Rooms** tab
2. Click **Add Room**
3. Name: `entrance`
4. Description: `You stand in a small cave with rough stone walls.`
5. Click **Save**

### Step 4: Add an Item
1. Switch to the **Items** tab
2. Click **Add Item**
3. Name: `torch`
4. Description: `A wooden torch that provides light`
5. Weight: `1`
6. Value: `5`
7. Tick **Takeable**
8. Click **Save**

### Step 5: Add an NPC
1. Open the **NPCs** tab
2. Click **Add NPC**
3. Name: `wizard`
4. Description: `An old wizard with a long white beard`
5. Friendliness: `75`
6. Health: `50`
7. Click **Save**

### Step 6: Place Items & NPCs
1. Return to the **Rooms** tab
2. Select the `entrance` room
3. Add `torch` under **Items**
4. Add `wizard` under **NPCs**
5. Click **Update**

### Step 7: Playtest
1. Open the **Play** tab
2. Click **Start/Resume Adventure**
3. Try these commands:

```
> look
> get torch
> talk to wizard
```

### Step 8: Save Your Work
1. Click **File → Save Adventure**
2. Save as `my_first_quest.json`
3. The IDE stores it in the `adventures/` folder

---

## Essential Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `look` | Describe current room | `look` |
| `go [dir]` | Move in a direction | `go north` |
| `get [item]` | Pick up an item | `get torch` |
| `inventory` | Show carried items | `inventory` |
| `talk to [npc]` | Talk to a character | `talk to wizard` |
| `help` | List all commands | `help` |

**Shortcuts**: `n`=north, `s`=south, `e`=east, `w`=west, `i`=inventory, `l`=look

---

## Next Steps

- **Play bundled adventures:** launch the IDE and choose from the adventure selector.
  ```bash
  python -m src.acs.ui.ide
  ```
- **Learn more commands:** read the [Command Reference](../reference/COMMANDS.md).
- **Dive deeper:** work through the [User Manual](USER_MANUAL.md) and [IDE Guide](IDE_GUIDE.md).
- **Customize the IDE:** adjust themes and fonts from the **View** menu.

---

## Tips

- ✅ Save often via **File → Save Adventure**
- ✅ Playtest while building to catch logic gaps early
- ✅ Use natural language—`what am I carrying?` works!
- ✅ Mirror exits so every route has a return path
- ✅ Type `journal` in-game to review active quests

---

## Troubleshooting

**IDE will not start**

```bash
# Verify interpreter version (need Python 3.10+)
python --version

# Relaunch with the default interpreter
python -m src.acs.ui.ide
```

Still stuck? Run `./quickstart.sh` and choose **Reset Cache**.

**Command not recognised**
- Type `help` for the full verb list
- Try synonyms such as `take`, `get`, or `grab`
- Keep phrasing natural: "pick up the torch" is valid

**Adventure will not load**
- Validate the JSON via [jsonlint.com](https://jsonlint.com/)
- Confirm every exit has a matching room
- Load the bundled showcase adventure (see `adventures/colossal_storyworks_showcase.json`) to compare structure

---

## Sample Adventure Snippet

Preview of a minimal adventure payload:

```json
{
  "title": "Sample Quest",
  "author": "Honey Badger",
  "settings": {"starting_room": "entrance"},
  "rooms": {
    "entrance": {
      "description": "A small cave entrance...",
      "exits": {"north": "hall"},
      "items": ["torch"],
      "npcs": []
    }
  },
  "items": {
    "torch": {
      "description": "A wooden torch",
      "weight": 1,
      "value": 5,
      "takeable": true
    }
  }
}
```

Open any file under `adventures/` for a full example.

---

## Need Help?

- **User Manual:** complete walkthrough for creators and players
- **GitHub Issues:** report bugs or request features
- **Discord:** join the community (link in `README.md`)
- **Email:** support@honeybadgeruniverse.com

---

**Adventure awaits—happy building!** 🎮
