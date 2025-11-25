# Colossal StoryWorks - Game Library

## 🎉 Featured Adventures Available

Colossal StoryWorks now ships with two curated sample adventures: one that exercises every narrative and systems feature, and a compact visual builder demo that spotlights the new point-and-click workflow.

### **Visual Builder Sample Adventure**
- **File**: `adventures/visual_builder_sample.json`
- **Setting**: A compact three-room studio tour that highlights how visual scenes map to classic parser commands
- **Scope**: 3 rooms, 2 items, 9 hotspots, and fully authored grid presets for each scene
- **Systems Spotlighted**:
	- Visual Builder workflow with per-scene grid visibility and cell sizing
	- Hotspot command sequences (`look workbench; get lab keycard`) feeding into the standard parser
	- Lightweight data model ideal for experimentation or tutorials
- **Ideal For**: Designers new to visual adventures who want a minimal, readable example that pairs Tkinter scenes with adventure data.

### **Colossal StoryWorks Showcase Adventure**
- **File**: `adventures/colossal_storyworks_showcase.json`
- **Setting**: A living creative campus that fuses retro arcades, neon skylines, and wizard towers
- **Scope**: 22 interconnected rooms, 24 items, 8 unique NPCs, 5 bespoke puzzles, 3 multi-stage quests, and a reality-bending boss encounter
- **Systems Spotlighted**:
	- Trading and inventory management via Quartermaster Dex
	- Branching dialogue with quest unlocks and item rewards
	- Locked-door, combination, riddle, sequence, and hidden-object puzzles
	- Friendly companions, aggressive foes, and an adaptive end boss
	- Dynamic lighting, hidden items, traps, environmental effects, and dark-room navigation using light sources
- **Ideal For**: New authors exploring the IDE, experienced designers looking for reference patterns, and anyone who wants a single adventure that exercises every major feature.

> Tip: Load the adventure in the IDE (`python -m src.acs.ui.ide`), open the **Adventure Browser**, and select “Colossal StoryWorks Showcase Adventure” to explore or extend it.

---

## ✅ Verification Summary

- JSON validated with `python -m json.tool`
- Required entities present (rooms, items, monsters, puzzles, quests, dialogues)
- Puzzle gating tested (keycard door, combination vault, riddle bridge, hidden latch, temporal sequence)
- Combat, trading, and dialogue systems exercised start-to-finish
- Works with both the IDE launcher and `acs_engine_enhanced.py`

---

## 🛠️ Creating Your Own Adventures

- Duplicate the showcase file and tailor rooms, NPCs, and quests to your theme
- Use the IDE’s validators to catch disconnected rooms or missing quest targets
- Keep utility items (keys, quest objects) clearly labeled—future you will thank you
- Document unique mechanics directly in the adventure JSON or alongside your design notes in `docs/user-guides/`

---

## 🧩 Suggested Experiments

- Swap the Temporal Nexus puzzle type to `custom` and script bespoke logic
- Add plugins (e.g., achievements) and tag drops in the Prototype Vault
- Layer accessibility settings by toggling options in `config/engine.json`

The showcase adventure is a starting line, not a finish line. Fork it, remix it, and keep building!


You now have a comprehensive library spanning the entire history of interactive fiction, from the earliest games to modern interpretations. Each adventure is a fully playable tribute to the classics that defined the genre.

**Have fun exploring!** 🚀
