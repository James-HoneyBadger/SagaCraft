#!/usr/bin/env python3
"""Integration tests for Phase I enhanced systems"""

import sys
from pathlib import Path
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parents[2]))

from sagacraft.ui.enhanced_game_ui import (
    EnhancedGameDisplay,
    EnhancedGameSession,
)
from sagacraft.ui.game_settings import GameSettings
from sagacraft.ui.auto_save import AutoSaveSystem


def test_enhanced_display():
    """Test enhanced game display system"""
    print("\n=== Testing Enhanced Game Display ===")
    
    settings = GameSettings(enable_colors=True, wrap_at_width=60)
    display = EnhancedGameDisplay(settings)
    
    # Test room display
    room_output = display.display_room(
        "Throne Room",
        "A grand chamber with towering pillars and golden decorations.",
        {"north": 2, "south": 3, "east": 4},
        show_compass=True
    )
    assert "Throne Room" in room_output, "Should include room name"
    assert "↑" in room_output or "Exits" in room_output, "Should show exits"
    print(f"✓ Room display works\n{room_output[:100]}...")
    
    # Test status display
    status_output = display.display_status(
        "Hero",
        level=5,
        health=45,
        max_health=100,
        additional_stats={"Gold": 250, "Experience": 1500}
    )
    assert "Hero" in status_output, "Should include character name"
    assert "45/100" in status_output, "Should show health"
    assert "250" in status_output, "Should show additional stats"
    print(f"✓ Status display works\n{status_output[:100]}...")
    
    # Test colored messages
    success_msg = display.display_success("Quest completed!")
    assert "Quest completed!" in success_msg, "Should include message"
    print(f"✓ Success message works")
    
    error_msg = display.display_error("Not enough mana!")
    assert "Not enough mana!" in error_msg, "Should include message"
    print(f"✓ Error message works")
    
    # Test dialogue
    dialog = display.display_dialog("Wizard", "Greetings, adventurer! I have a quest for you.")
    assert "Wizard:" in dialog, "Should include NPC name"
    assert "quest" in dialog.lower(), "Should include dialogue"
    print(f"✓ Dialogue display works\n{dialog[:100]}...")
    
    return True


def test_auto_save_system(tmp_path):
    """Test auto-save system"""
    print("\n=== Testing Auto-Save System ===")
    
    auto_save = AutoSaveSystem(tmp_path)
    
    # Test enable/disable
    auto_save.enable_auto_save(True, command_threshold=5)
    assert auto_save.auto_save_enabled, "Should be enabled"
    print("✓ Auto-save enabled")
    
    # Test command counting
    for i in range(4):
        result = auto_save.on_command_executed()
        assert not result, f"Should not trigger save at command {i+1}"
    
    result = auto_save.on_command_executed()
    assert result, "Should trigger save on 5th command"
    print("✓ Command threshold works")
    
    # Test save/load
    test_state = {
        "player": {"name": "Hero", "health": 50},
        "room": 1,
        "inventory": ["sword", "shield"]
    }
    
    saved = auto_save.save_game_state(test_state)
    assert saved, "Should save successfully"
    assert auto_save.has_auto_save(), "Should detect save"
    print("✓ Game state saved")
    
    loaded_state = auto_save.load_auto_save()
    assert loaded_state == test_state, "Loaded state should match saved"
    print("✓ Game state loaded correctly")
    
    # Test clear
    cleared = auto_save.clear_auto_save()
    assert cleared, "Should clear auto-save"
    assert not auto_save.has_auto_save(), "Should be gone after clear"
    print("✓ Auto-save cleared")
    
    return True


def test_enhanced_session(tmp_path):
    """Test enhanced game session"""
    print("\n=== Testing Enhanced Game Session ===")
    
    session = EnhancedGameSession(tmp_path)
    
    # Test command recording
    session.record_command("look")
    session.record_command("inventory")
    session.record_command("go north")
    
    recent = session.get_recent_commands(2)
    assert "go north" in recent, "Should have recent commands"
    print(f"✓ Command recording works: {recent}")
    
    # Test history search
    session.record_command("attack goblin")
    session.record_command("attack orc")
    results = session.search_history("attack")
    assert len(results) == 2, "Should find attack commands"
    print(f"✓ History search works: {results}")
    
    # Test settings update
    original_colors = session.display.formatter.enabled
    success = session.update_setting("enable_colors", not original_colors)
    assert success, "Should update setting"
    assert session.display.formatter.enabled == (not original_colors), "Setting should change"
    print("✓ Settings update works")
    
    # Test auto-save configuration
    assert session.auto_save.auto_save_enabled, "Should have auto-save enabled"
    print("✓ Auto-save configured")
    
    return True


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("SAGACRAFT PHASE I: INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Enhanced Display", test_enhanced_display),
        ("Auto-Save System", lambda: test_auto_save_system(Path(tempfile.mkdtemp()))),
        ("Enhanced Session", lambda: test_enhanced_session(Path(tempfile.mkdtemp()))),
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
    success = run_integration_tests()
    sys.exit(0 if success else 1)
