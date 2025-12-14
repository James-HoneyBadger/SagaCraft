import json
import pytest

from sagacraft.core.engine import AdventureGame


def aj_adventure():
    return {
        "title": "AJ Adventure",
        "intro": "AJ testing.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "One", "description": "First.", "exits": {"north": 2}},
            {"id": 2, "name": "Two", "description": "Second.", "exits": {"south": 1}},
        ],
        "items": [],
        "monsters": [],
    }


@pytest.fixture()
def aj_engine(tmp_path):
    path = tmp_path / "aj_adventure.json"
    path.write_text(json.dumps(aj_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    return eng


def test_achievements_journal_no_crash(aj_engine):
    # Whether subsystems are present or not, moving should work and not crash.
    aj_engine.move("north")
    assert aj_engine.player.current_room == 2
    # If achievements/journal exist, moving should increment stats and optionally log.
    ach = getattr(aj_engine, "achievements", None)
    if ach:
        # stats may have incremented; at minimum the object exists.
        assert hasattr(ach, "statistics")
    journal = getattr(aj_engine, "journal", None)
    if journal:
        assert hasattr(journal, "log_event")
