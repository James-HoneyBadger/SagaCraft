#!/usr/bin/env python3
"""Tests for Phase I: UI/UX Enhancements"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from sagacraft.ui.text_formatting import (
    RichTextFormatter,
    TextColor,
    TextCategory,
    HealthBar,
    CompassRose,
    ASCIIArt,
)
from sagacraft.ui.game_settings import (
    GameSettings,
    SettingsManager,
    QuickSaveManager,
    CommandHistory,
    SaveFrequency,
    TextSize,
)


def test_text_formatting():
    """Test text formatting capabilities"""
    print("\n=== Testing Text Formatting ===")
    
    formatter = RichTextFormatter(enabled=True)
    
    # Test colorization
    colored_text = formatter.colorize("Hello", TextCategory.DESCRIPTION)
    assert "\033[" in colored_text, "Color codes should be present"
    print(f"✓ Colorization works: {colored_text}")
    
    # Test disabled colors
    plain_formatter = RichTextFormatter(enabled=False)
    plain_text = plain_formatter.colorize("Hello", TextCategory.DESCRIPTION)
    assert plain_text == "Hello", "Plain formatter should not add codes"
    print("✓ Plain text mode works")
    
    # Test ANSI stripping
    stripped = RichTextFormatter.strip_colors(colored_text)
    assert stripped == "Hello", "Stripping should remove colors"
    print(f"✓ Color stripping works: '{stripped}'")
    
    # Test text wrapping
    long_text = "This is a long piece of text that should be wrapped to a specific width."
    wrapped = formatter.wrap_text(long_text, width=30, indent=2)
    lines = wrapped.split('\n')
    for line in lines:
        assert len(line) <= 30, f"Line too long: {len(line)} > 30"
    print(f"✓ Text wrapping works:\n{wrapped}")
    
    return True


def test_health_bar():
    """Test health bar generation"""
    print("\n=== Testing Health Bar ===")
    
    # Test full health
    bar_full = HealthBar.create_bar(100, 100)
    assert "100/100" in bar_full, "Should show 100/100"
    assert "█" in bar_full, "Should have full bar"
    print(f"✓ Full health bar: {bar_full}")
    
    # Test half health
    bar_half = HealthBar.create_bar(50, 100)
    assert "50/100" in bar_half, "Should show 50/100"
    print(f"✓ Half health bar: {bar_half}")
    
    # Test no health
    bar_empty = HealthBar.create_bar(0, 100)
    assert "0/100" in bar_empty, "Should show 0/100"
    assert "░" in bar_empty, "Should have empty bar"
    print(f"✓ Empty health bar: {bar_empty}")
    
    return True


def test_compass():
    """Test compass rose generation"""
    print("\n=== Testing Compass ===")
    
    # Test simple compass
    exits = ["north", "south", "east"]
    compass = CompassRose.simple_compass(exits)
    assert "↑" in compass, "Should have north arrow"
    assert "↓" in compass, "Should have south arrow"
    assert "→" in compass, "Should have east arrow"
    print(f"✓ Simple compass: {compass}")
    
    # Test detailed compass
    exits_dict = {"north": 2, "east": 3}
    detailed = CompassRose.detailed_compass(exits_dict)
    assert "Room 2" in detailed, "Should show room IDs"
    assert "Room 3" in detailed, "Should show room IDs"
    print(f"✓ Detailed compass:\n{detailed}")
    
    # Test no exits
    empty_compass = CompassRose.simple_compass([])
    assert "No visible exits" in empty_compass, "Should handle no exits"
    print(f"✓ Empty compass: {empty_compass}")
    
    return True


def test_ascii_art():
    """Test ASCII art generation"""
    print("\n=== Testing ASCII Art ===")
    
    # Test box
    content = "This is a test"
    box = ASCIIArt.box(content, width=30)
    assert "┌" in box, "Should have top border"
    assert "└" in box, "Should have bottom border"
    assert "│" in box, "Should have side borders"
    print(f"✓ ASCII box:\n{box}")
    
    # Test box with title
    titled_box = ASCIIArt.box(content, width=30, title="Test")
    assert "Test" in titled_box, "Should include title"
    print(f"✓ Titled box:\n{titled_box}")
    
    # Test separators
    rule = ASCIIArt.horizontal_rule(20)
    assert len(rule) == 20, "Rule should be correct length"
    print(f"✓ Horizontal rule: {rule}")
    
    separator = ASCIIArt.separator(20)
    assert "═" in separator, "Should use separator character"
    print(f"✓ Separator: {separator}")
    
    return True


def test_game_settings():
    """Test game settings"""
    print("\n=== Testing Game Settings ===")
    
    # Test creation
    settings = GameSettings()
    assert settings.auto_save_enabled is True, "Should have auto-save enabled by default"
    assert settings.difficulty_level == "normal", "Should default to normal difficulty"
    print("✓ Settings creation works")
    
    # Test to_dict
    data = settings.to_dict()
    assert "enable_colors" in data, "Should include colors setting"
    assert data["text_size"] == "normal", "Enum should be converted"
    print("✓ Settings serialization works")
    
    # Test from_dict
    settings2 = GameSettings.from_dict(data)
    assert settings2.enable_colors == settings.enable_colors, "Should deserialize correctly"
    print("✓ Settings deserialization works")
    
    return True


def test_settings_manager(tmp_path):
    """Test settings manager"""
    print("\n=== Testing Settings Manager ===")
    
    settings_file = tmp_path / "test_settings.json"
    manager = SettingsManager(settings_file)
    
    # Test default loading
    assert manager.settings.auto_save_enabled is True
    print("✓ Settings manager loads defaults")
    
    # Test setting and saving
    manager.set("difficulty_level", "hard")
    assert manager.get("difficulty_level") == "hard", "Setting should be updated"
    assert settings_file.exists(), "Settings file should be created"
    print("✓ Settings can be set and saved")
    
    # Test reloading
    manager2 = SettingsManager(settings_file)
    assert manager2.get("difficulty_level") == "hard", "Settings should persist"
    print("✓ Settings persist across reload")
    
    # Test reset
    manager.reset_to_defaults()
    assert manager.get("difficulty_level") == "normal", "Should reset to defaults"
    print("✓ Settings reset works")
    
    return True


def test_quick_save_manager(tmp_path):
    """Test quick-save manager"""
    print("\n=== Testing Quick-Save Manager ===")
    
    manager = QuickSaveManager(tmp_path)
    
    # Test path generation
    path = manager.get_quicksave_path(0)
    assert "quicksave_0" in str(path), "Should generate correct path"
    print(f"✓ Quick-save path: {path}")
    
    # Test existence check
    assert not manager.has_quicksave(0), "Should not have quicksave initially"
    print("✓ Quicksave existence check works")
    
    # Test creation
    path.write_text("{}")
    assert manager.has_quicksave(0), "Should detect existing quicksave"
    print("✓ Quicksave creation detected")
    
    # Test info retrieval
    info = manager.get_quicksave_info(0)
    assert info is not None, "Should retrieve info"
    assert info["size_bytes"] == 2, "Should show correct file size"
    print(f"✓ Quicksave info: {info}")
    
    # Test deletion
    assert manager.delete_quicksave(0), "Should delete quicksave"
    assert not manager.has_quicksave(0), "Should be gone after deletion"
    print("✓ Quicksave deletion works")
    
    return True


def test_command_history():
    """Test command history"""
    print("\n=== Testing Command History ===")
    
    history = CommandHistory(max_history=5)
    
    # Test adding commands
    history.add("look")
    history.add("inventory")
    history.add("go north")
    assert len(history.history) == 3, "Should have 3 commands"
    print("✓ Commands added to history")
    
    # Test history overflow
    for i in range(10):
        history.add(f"command_{i}")
    assert len(history.history) == 5, "Should respect max history"
    print("✓ History max limit enforced")
    
    # Test navigation
    assert history.previous() == "command_9", "Should get most recent"
    assert history.previous() == "command_8", "Should go back"
    assert history.next() == "command_9", "Should go forward"
    print("✓ History navigation works")
    
    # Test search
    history.clear()
    history.add("attack goblin")
    history.add("attack orc")
    history.add("look around")
    results = history.search("attack")
    assert len(results) == 2, "Should find matching commands"
    print(f"✓ History search works: {results}")
    
    # Test recent
    recent = history.get_recent(2)
    assert len(recent) == 2, "Should get recent commands"
    assert recent[-1] == "look around", "Should be in order"
    print(f"✓ Recent history: {recent}")
    
    return True


def run_all_tests():
    """Run all Phase I tests"""
    print("\n" + "="*60)
    print("SAGACRAFT PHASE I: UI/UX ENHANCEMENT TESTS")
    print("="*60)
    
    import tempfile
    
    tests = [
        ("Text Formatting", test_text_formatting),
        ("Health Bar", test_health_bar),
        ("Compass Rose", test_compass),
        ("ASCII Art", test_ascii_art),
        ("Game Settings", test_game_settings),
        ("Settings Manager", lambda: test_settings_manager(Path(tempfile.mkdtemp()))),
        ("Quick-Save Manager", lambda: test_quick_save_manager(Path(tempfile.mkdtemp()))),
        ("Command History", test_command_history),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
