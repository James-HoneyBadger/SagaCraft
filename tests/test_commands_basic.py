import io
import json
import sys

import pytest

from sagacraft.core.engine import AdventureGame


def make_cmd_adventure():
    return {
        "title": "Cmd Adventure",
        "intro": "Cmd testing.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "Start", "description": "Start room.", "exits": {"north": 2}},
            {"id": 2, "name": "North", "description": "North room.", "exits": {"south": 1}},
        ],
        "items": [
            {"id": 1, "name": "apple", "description": "A tasty apple.", "type": "edible", "weight": 1, "value": 1, "location": 1},
            {"id": 2, "name": "stone", "description": "Just a stone.", "type": "normal", "weight": 1, "value": 0, "location": 1},
        ],
        "monsters": [
            {"id": 1, "name": "Rat", "description": "A small rat.", "room_id": 2, "hardiness": 2, "agility": 2, "friendliness": "neutral", "courage": 5}
        ],
    }


@pytest.fixture()
def cmd_engine(tmp_path):
    path = tmp_path / "cmd_adventure.json"
    path.write_text(json.dumps(make_cmd_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    return eng


def capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        func(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_process_command_look(cmd_engine):
    out = capture_output(cmd_engine.process_command, "look")
    assert "start" in out.lower()
    assert "obvious exits" in out.lower()


def test_process_command_move_and_look(cmd_engine):
    cmd_engine.process_command("move north")
    assert cmd_engine.player.current_room == 2
    out = capture_output(cmd_engine.process_command, "look")
    assert "north" in out.lower()


def test_process_command_get_drop_inventory(cmd_engine):
    # get apple
    cmd_engine.process_command("get apple")
    assert 1 in cmd_engine.player.inventory
    out = capture_output(cmd_engine.process_command, "inventory")
    assert "carrying" in out.lower()
    # drop stone by command
    cmd_engine.process_command("drop stone")
    assert 2 not in cmd_engine.player.inventory


def test_process_command_attack_handles_missing_target(cmd_engine):
    out = capture_output(cmd_engine.process_command, "attack dragon")
    assert "don't see" in out.lower()


def test_process_command_status(cmd_engine):
    out = capture_output(cmd_engine.process_command, "status")
    assert "health" in out.lower()
    assert cmd_engine.player.current_health is not None


def test_process_command_examine_and_search_without_env(cmd_engine):
    out_ex = capture_output(cmd_engine.process_command, "examine stone")
    assert "examine" in out_ex.lower() or "don't see" in out_ex.lower()
    out_search = capture_output(cmd_engine.process_command, "search")
    assert "search" in out_search.lower()
