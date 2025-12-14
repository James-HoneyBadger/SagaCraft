import json
import os
import pytest

from sagacraft.core.engine import AdventureGame


def test_invalid_file_path_raises(tmp_path):
    bad_path = tmp_path / "missing.json"
    eng = AdventureGame(str(bad_path))
    with pytest.raises(FileNotFoundError):
        eng.load_adventure()


def test_invalid_json_raises(tmp_path):
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not json}", encoding="utf-8")
    eng = AdventureGame(str(bad_path))
    with pytest.raises(ValueError):
        eng.load_adventure()


def test_missing_room_graceful_outputs(tmp_path, capsys):
    data = {
        "title": "Broken Adventure",
        "intro": "",
        "start_room": 999,
        "rooms": [],
        "items": [],
        "monsters": [],
    }
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()

    eng.look()
    out = capsys.readouterr().out
    assert "void" in out.lower()

    eng.attack("anything")
    out = capsys.readouterr().out
    assert "nothing to attack" in out.lower()

    eng.get_item("anything")
    out = capsys.readouterr().out
    assert "nothing to pick up" in out.lower()

    eng.drop_item("anything")
    out = capsys.readouterr().out
    assert "can't drop" in out.lower() or "don't have" in out.lower()
