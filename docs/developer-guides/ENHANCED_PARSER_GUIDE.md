# Enhanced Parser & Party System - Quick Reference

## Natural Language Understanding

The Adventure Construction Set now includes an enhanced parser that understands natural language commands!

### Examples of Natural Language:

**Movement:**
- "go north" or "walk north" or "head north" or just "north"
- "go into the cave" → enter
- "leave the room" → exit

**Looking/Examining:**
- "look at the painting" → examines painting
- "inspect the chest" → examines chest
- "what's here?" → look around
- "search the room" → search for hidden items

**Inventory:**
- "pick up the sword" or "get sword" or "take the rusty blade"
- "put the gem in my backpack" → store in container
- "what am I carrying?" → inventory
- "drop the torch" or "put down the torch"

**Combat:**
- "attack the goblin" or "fight goblin" or "kill the orc"
- "run away" or "flee" → escape combat

**Interaction:**
- "talk to the wizard" or "speak with wizard"
- "ask the mayor about the quest"
- "give the key to the guard"
- "trade with the merchant"

**Questions:**
- "Where am I?" → look
- "Who is here?" → list NPCs
- "What am I carrying?" → inventory
- "Can I go north?" → checks exits

## Party/Companion System

### Recruiting Companions

You can now recruit friendly NPCs to join your party!

**Commands:**
- `recruit <npc name>` - Ask an NPC to join
- `invite <npc name>` - Same as recruit
- `party` - View your current party
- `dismiss <name>` - Remove someone from party

**Examples:**
```
> recruit Marcus the merchant
Marcus the merchant joins your party as a fighter!

> party
YOUR PARTY
==================================================
Marcus the merchant - fighter (ALIVE)
  HP: 20/20
  Loyalty: 50/100
==================================================
```

### Party Mechanics

**Party Limits:**
- Maximum 3 companions at once
- Only friendly NPCs can be recruited
- NPCs must be in the same room

**Companion Roles:**
- **Fighter** - High attack, good health
- **Mage** - Magic abilities, lower health
- **Healer** - Can heal party members
- **Rogue** - High agility, can pick locks

**Loyalty System:**
- Companions have loyalty (0-100)
- Low loyalty (<30) = companion may leave
- Improve loyalty: sharing loot, successful quests
- Decrease loyalty: letting them take damage, being mean

**Combat with Companions:**
- Companions fight alongside you automatically
- They can take damage for you
- If they die, they may be lost forever
- Some quests require specific party members

### Advanced Party Commands

```
> order Marcus to attack the orc
Marcus attacks the orc!

> give health potion to Marcus
You give the health potion to Marcus.
Marcus: "Thank you!"

> ask Marcus about his background
Marcus tells you his story...
```

## Synonym Support

The parser understands MANY ways to say things:

**Movement:** go, move, walk, run, travel, head, proceed, enter, leave
**Looking:** look, examine, inspect, check, view, observe, study, peer at
**Taking:** get, take, grab, pick up, acquire, obtain, collect, gather
**Dropping:** drop, put down, leave, discard, release
**Combat:** attack, fight, hit, strike, kill, slay, battle, assault
**Talking:** talk, speak, chat, converse, say, tell, ask

## Tips for Natural Commands

✅ **DO:**
- Use natural sentences: "Can I pick up the sword?"
- Ask questions: "What's in the chest?"
- Be descriptive: "attack the angry goblin"
- Use prepositions: "put sword in backpack"

❌ **DON'T:**
- Need to remember exact syntax
- Type cryptic abbreviations (unless you want to!)
- Worry about article words (the, a, an)

## Combining Features

**Natural Language + Party:**
```
> tell Marcus to guard the door
> ask the wizard to join our quest
> have Sarah heal Marcus
```

**Complex Commands:**
```
> put all my gold in the chest
> give the magic sword to Marcus
> ask the innkeeper about rumors
> search the desk for hidden items
```

## Testing the New Features

Try loading one of the showcase adventures and experiment:

```bash
python acs_engine_enhanced.py adventures/enchanted_forest.json
```

Then try commands like:
- "Can I talk to the pixie queen?"
- "I want to recruit the unicorn"
- "What's in my backpack?"
- "Tell me about this place"
- "Pick up everything valuable"

## For Adventure Creators

To make NPCs recruitable in your adventures:

```json
{
  "id": 1,
  "name": "Marcus the Warrior",
  "friendliness": "friendly",
  "hardiness": 20,
  "agility": 12,
  "can_join_party": true,
  "role": "fighter",
  "recruitment_dialog": "I'll join you, but only if you're brave enough!"
}
```

## Backward Compatibility

All original commands still work!
- "n" still means north
- "i" still shows inventory
- Simple commands work exactly as before

The enhanced parser is OPTIONAL - games work fine without it.

---

**Have fun creating natural conversations with your adventures!**
