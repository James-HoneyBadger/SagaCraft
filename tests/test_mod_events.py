import json
import pytest

from sagacraft.core.engine import AdventureGame


def base_adventure():
    return {
        "title": "Mods Adventure",
        "intro": "Mods testing.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "Start", "description": "Start room.", "exits": {"east": 2}},
            {"id": 2, "name": "Next", "description": "Next room.", "exits": {"west": 1}},
        ],
        "items": [
            {"id": 1, "name": "coin", "description": "A coin.", "type": "normal", "weight": 1, "value": 1, "location": 1},
        ],
        "monsters": [],
    }


@pytest.fixture()
def mod_engine(tmp_path):
    path = tmp_path / "mods_adventure.json"
    path.write_text(json.dumps(base_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    return eng


def test_fire_mod_event_safe_without_mod_system(mod_engine):
    # With no modding system available, firing events should no-op gracefully.
    payload = {"room_id": 1, "cancel": False}
    out_payload, echo = mod_engine._fire_mod_event(event=None, payload=payload)
    assert out_payload == payload
    assert echo == []


def test_standard_actions_do_not_crash_without_mods(mod_engine):
    mod_engine.get_item("coin")
    mod_engine.drop_item("coin")
    mod_engine.move("east")
    mod_engine.look()
