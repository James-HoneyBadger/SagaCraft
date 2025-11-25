# Example Gameplay Session

This walkthrough captures a condensed play session inside the Colossal StoryWorks Showcase adventure. It illustrates how exploration, quest pickup, and NPC conversations flow with the enhanced systems.

## Starting the Game

Launch the IDE with `python -m src.acs.ui.ide`, switch to the **Play** tab, load the showcase adventure, and press **▶ Start Game**. The transcript below mirrors the experience inside the play console.

## Sample Gameplay

*Output below is abridged for readability while staying faithful to the bundled adventure.*

```
============================================================
            Colossal StoryWorks Showcase Adventure
============================================================

Grand Concourse
---------------
A vaulted atrium filled with holographic banners that celebrate legendary adventures. Interactive kiosks line the walls, while portals lead deeper into the complex.
Ambient: A warm synth melody hums through hidden speakers.
Obvious exits: north, east, west, up

> quests
No active quests yet. Talk with the campus staff to pick one up.

> north
Idea Fountain
-------------
A tranquil garden where inspiration literally flows. Wisps of text swirl above a luminous pool, forming snippets of future storylines.
Obvious exits: south, north, east

> search fountain
You trace the glowing runes around the basin. A hidden panel slides open and reveals a vault keycard!

> get keycard
Taken: vault keycard.

> south
Grand Concourse
---------------
A vaulted atrium filled with holographic banners that celebrate legendary adventures.
Obvious exits: north, east, west, up

> west
Library of Echoes
-----------------
Shelves spiral upward into darkness, packed with design journals and glowing codices. Archivist Lyra looks up from her catalog.
Obvious exits: east, west

> talk lyra
Archivist Lyra says: Ah, a fresh face! Welcome to the Library of Echoes. Every tale ever told whispers here.

> ask lyra about quest
Archivist Lyra says: If you're willing, recover the data crystal and arcane coil. They power the new narrative analytics wing.
Quest added: Reboot the Archive.

> quests
Active Quests:
1. Reboot the Archive — Recover the Arcane Coil from the Puzzle Gallery and the Data Crystal from the Archive Terminal.

> east
Grand Concourse
---------------
Ambient: A warm synth melody hums through hidden speakers.
Obvious exits: north, east, west, up

> east
Workshop Row
------------
Benches overflow with clockwork contraptions, spell matrices, and plush dice. Quartermaster Dex stands ready to outfit any creator.
Obvious exits: west, east, south

> talk dex
Quartermaster Dex says: Dex here! Need gear? Inspiration? Sparkling water? I'm your quartermaster.

> trade dex
Quartermaster Dex says: I've got shield emitters, pulse pistols, and nano tonics. Bring me rare drops and I'll stock something special.

> inventory
You are carrying:
  - vault keycard
Gold: 0  |  Weight: 1
```

### Highlights

- Discovered a hidden item with the environment-aware `search` command.
- Accepted the “Reboot the Archive” quest from Archivist Lyra, demonstrating quest activation.
- Consulted Quartermaster Dex for trading options while keeping an eye on inventory updates.
