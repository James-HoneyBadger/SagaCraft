import random

import pytest

from sagacraft.core.engine import AdventureGame, MonsterStatus


def test_load_adventure_initializes_entities(engine):
    assert engine.adventure_title == "Test Adventure"
    assert engine.player.current_room == 1
    assert len(engine.rooms) == 2
    assert len(engine.items) == 1
    assert len(engine.monsters) == 1
    # Item starts in room 1
    item = engine.items[1]
    assert item.location == 1


def test_move_changes_room_and_increments_turns(engine):
    engine.move("north")
    assert engine.player.current_room == 2
    assert engine.turn_count == 1


def test_move_invalid_direction_keeps_position(engine, capsys):
    engine.move("west")
    captured = capsys.readouterr().out
    assert "can't go that way" in captured.lower()
    assert engine.player.current_room == 1


def test_get_and_drop_item_cycles_inventory(engine, capsys):
    engine.get_item("test item")
    item = engine.items[1]
    assert item.location == 0
    assert 1 in engine.player.inventory

    engine.drop_item("test item")
    captured = capsys.readouterr().out
    assert "drop the test item" in captured.lower()
    assert 1 not in engine.player.inventory
    assert item.location == engine.player.current_room


def test_attack_kills_monster_without_counter(engine, monkeypatch):
    # Move to monster room
    engine.player.current_room = 2
    monster = engine.monsters[1]
    monster.current_health = 1
    monster.friendliness = MonsterStatus.HOSTILE

    # Ensure deterministic damage high enough to kill
    monkeypatch.setattr(random, "randint", lambda a, b: 2)

    engine.attack("goblin")

    assert monster.is_dead is True
    assert engine.game_over is False
    assert monster.current_health <= 0


def test_attack_handles_missing_room_gracefully(engine, capsys):
    engine.player.current_room = 999
    engine.rooms.clear()
    engine.attack("anything")
    captured = capsys.readouterr().out
    assert "nothing to attack" in captured.lower()


def test_get_items_in_room_matches_locations(engine):
    items = engine.get_items_in_room(1)
    assert len(items) == 1
    assert items[0].id == 1
