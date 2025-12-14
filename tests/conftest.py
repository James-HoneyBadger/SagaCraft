import json
import pytest

from sagacraft.core.engine import AdventureGame


def make_base_adventure(start_room=1):
    return {
        "title": "Test Adventure",
        "intro": "Testing grounds.",
        "start_room": start_room,
        "rooms": [
            {
                "id": 1,
                "name": "Room One",
                "description": "The first room.",
                "exits": {"north": 2},
            },
            {
                "id": 2,
                "name": "Room Two",
                "description": "The second room.",
                "exits": {"south": 1},
            },
        ],
        "items": [
            {
                "id": 1,
                "name": "test item",
                "description": "A simple item.",
                "type": "normal",
                "weight": 1,
                "value": 0,
                "location": 1,
            }
        ],
        "monsters": [
            {
                "id": 1,
                "name": "Test Goblin",
                "description": "Small and cranky.",
                "room_id": 2,
                "hardiness": 5,
                "agility": 5,
                "friendliness": "neutral",
                "courage": 10,
            }
        ],
    }


@pytest.fixture()
def adventure_path(tmp_path):
    """Create a minimal adventure file on disk and return its path."""
    data = make_base_adventure()
    path = tmp_path / "adventure.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture()
def engine(adventure_path):
    eng = AdventureGame(str(adventure_path))
    eng.load_adventure()
    return eng
