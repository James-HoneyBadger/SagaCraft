#!/usr/bin/env python3
"""SagaCraft - Auto-Save System

Handles automatic game saving at specified intervals.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from threading import Timer


class AutoSaveSystem:
    """Manages automatic game saving"""
    
    def __init__(self, saves_dir: Optional[Path] = None):
        """
        Initialize auto-save system
        
        Args:
            saves_dir: Directory for save files
        """
        self.saves_dir = saves_dir or (Path(__file__).resolve().parents[3] / "saves")
        self.saves_dir.mkdir(parents=True, exist_ok=True)
        
        self.auto_save_enabled = False
        self.auto_save_interval = 300  # 5 minutes in seconds
        self.save_timer: Optional[Timer] = None
        self.command_count = 0
        self.command_threshold = 10
        self.last_save_time: Optional[datetime] = None
    
    def get_auto_save_path(self) -> Path:
        """Get path for auto-save file"""
        return self.saves_dir / "autosave.json"
    
    def enable_auto_save(
        self,
        enabled: bool = True,
        interval: Optional[int] = None,
        command_threshold: Optional[int] = None
    ) -> None:
        """
        Enable or disable auto-save
        
        Args:
            enabled: Whether to enable auto-save
            interval: Interval in seconds (if timed)
            command_threshold: Save every N commands
        """
        self.auto_save_enabled = enabled
        
        if interval is not None:
            self.auto_save_interval = interval
        
        if command_threshold is not None:
            self.command_threshold = command_threshold
        
        if enabled:
            self._start_timer()
    
    def _start_timer(self) -> None:
        """Start the auto-save timer"""
        if self.save_timer:
            self.save_timer.cancel()
        
        self.save_timer = Timer(
            self.auto_save_interval,
            self._on_timer
        )
        self.save_timer.daemon = True
        self.save_timer.start()
    
    def _on_timer(self) -> None:
        """Called when timer expires"""
        if self.auto_save_enabled:
            self._start_timer()  # Restart timer
    
    def on_command_executed(self) -> bool:
        """
        Called when a command is executed
        
        Returns:
            True if a save was performed
        """
        if not self.auto_save_enabled:
            return False
        
        self.command_count += 1
        
        if self.command_count >= self.command_threshold:
            self.command_count = 0
            return True  # Caller should save
        
        return False
    
    def save_game_state(self, game_state: Dict[str, Any]) -> bool:
        """
        Save game state to auto-save file
        
        Args:
            game_state: Game state dictionary
            
        Returns:
            True if successful
        """
        try:
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "game_state": game_state,
            }
            
            path = self.get_auto_save_path()
            with open(path, "w") as f:
                json.dump(save_data, f, indent=2, default=str)
            
            self.last_save_time = datetime.now()
            return True
        except (IOError, OSError, TypeError) as e:
            print(f"Auto-save failed: {e}")
            return False
    
    def load_auto_save(self) -> Optional[Dict[str, Any]]:
        """
        Load auto-saved game state
        
        Returns:
            Game state dictionary or None if no save exists
        """
        path = self.get_auto_save_path()
        
        if not path.exists():
            return None
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return data.get("game_state")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Failed to load auto-save: {e}")
            return None
    
    def has_auto_save(self) -> bool:
        """Check if auto-save exists"""
        return self.get_auto_save_path().exists()
    
    def clear_auto_save(self) -> bool:
        """Clear auto-save file"""
        path = self.get_auto_save_path()
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return True
    
    def shutdown(self) -> None:
        """Clean up resources"""
        if self.save_timer:
            self.save_timer.cancel()


__all__ = ["AutoSaveSystem"]
