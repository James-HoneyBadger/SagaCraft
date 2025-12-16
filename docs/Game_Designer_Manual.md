# SagaCraft Game Designer Manual

## Designing an adventure
An adventure is a single JSON file (see examples in `adventures/`).

Minimal top-level fields used across the IDE/engine:
- `title` (string)
- `author` (string)
- `intro` (string)
- `start_room` (int room id)
- `rooms` (array)
- `items` (array)
- `monsters` (array)
- `effects` (array, optional)

Optional extended top-level fields (supported by the extended engine):
- `settings` (object)
- `puzzles` (array)
- `dialogues` (array)
- `quests` (array)

## Rooms
Each room typically has:
- `id` (int)
- `name` (string)
- `description` (string)
- `exits` (object mapping directions to room ids)

Extended room fields you can use (examples exist in `adventures/infinite_archive.json`):
- `light_level` (e.g. `bright`, `normal`, `dim`, `dark`)
- `requires_light_source` (bool)
- `is_safe_zone` (bool)
- `has_trap` / `trap_damage` (bool/int)
- `environmental_effects` (array of strings)
- `hidden_items` (array of item ids) and `items_revealed` (bool)
- `alternate_description` + `condition_for_alternate` (strings)
- `ambient_sound` (string)

## Items
Core item fields:
- `id`, `name`, `description`
- `type` (string; maps to engine `ItemType` like `weapon`, `armor`, `edible`, `container`, `normal`)
- `weight`, `value`
- `location` (0 = player inventory, -1 = worn, or a room id)

Common combat/equipment fields:
- `is_weapon`, `weapon_type`, `weapon_dice`, `weapon_sides`
- `is_armor`, `armor_value`

Extended item fields (optional):
- `durability`, `max_durability`, `magical_bonus`, `special_abilities`
- `can_be_equipped`, `equipment_slot`
- Container support: `is_container`, `container_capacity`, `contains_items`
- Keys/quests: `is_key`, `unlocks_puzzle`, `is_quest_item`, `quest_id`
- `on_use_effect` (string hook for scripted/engine effects)

## Monsters / NPCs
Core monster fields:
- `id`, `name`, `description`, `room_id`
- `hardiness`, `agility`, `friendliness` (e.g. `friendly`, `neutral`, `hostile`)

Extended monster fields (optional):
- Dialogue/quests: `dialogue_id`, `gives_quests`
- Trading: `can_trade`, `inventory`
- AI tuning: `reaction_level`, `ai_behavior`, `special_abilities`

## Settings
Optional `settings` object supports at least:
- `allow_save` (bool) — if false, saving is disabled

## Using the IDE effectively
- Use `./Saga.sh` to create/edit adventures.
- Keep ids stable (rooms/items/monsters) to avoid broken references.
- Validate via play-testing from inside the IDE or via the headless loader.

## Validation without tests
Basic checks that catch most structural mistakes:
- Engine load: `PYTHONPATH=src python -m sagacraft.ui.player --check`
- Load + start room description: `PYTHONPATH=src python -m sagacraft.ui.player --load <your.json>`
- Run a small script of commands: `PYTHONPATH=src python -m sagacraft.ui.player --load <your.json> --cmds <file>`
