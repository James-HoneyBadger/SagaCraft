#!/usr/bin/env python3
"""Master test runner for all SagaCraft phases"""

import sys
import subprocess
from pathlib import Path

def run_test_file(test_file: Path) -> bool:
    """Run a single test file"""
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def main():
    """Run all phase tests"""
    tests_dir = Path(__file__).parent
    
    test_files = [
        "test_phase_1_ui_ux.py",
        "test_phase_1_integration.py",
        "test_phase_2_progression.py",
        "test_phase_3_combat.py",
        "test_phase_4_dialogue.py",
        "test_phase_5_procedural.py",
        "test_phase_6_persistence.py",
        "test_phase_7_companions.py",
        "test_phase_8_quests.py",
    ]
    
    print("\n" + "="*70)
    print("SAGACRAFT EPIC EVOLUTION - MASTER TEST SUITE")
    print("="*70)
    
    results = {}
    for test_file in test_files:
        test_path = tests_dir / test_file
        if not test_path.exists():
            print(f"\n⚠️  {test_file}: NOT FOUND")
            continue
        
        print(f"\n{'─'*70}")
        print(f"Running: {test_file}")
        print(f"{'─'*70}")
        
        success = run_test_file(test_path)
        results[test_file] = success
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {test_file}")
    
    print(f"\n{'─'*70}")
    print(f"Total: {passed} passed, {failed} failed out of {len(results)}")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
