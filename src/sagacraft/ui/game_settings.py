#!/usr/bin/env python3
"""SagaCraft - Game Settings & Quality of Life System

Manages user preferences, auto-save, and enhanced UI settings.
"""

from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


class SaveFrequency(Enum):
    """Auto-save frequency options"""
    DISABLED = "disabled"
    AFTER_COMMAND = "after_command"
    EVERY_5_COMMANDS = "every_5"
    EVERY_10_COMMANDS = "every_10"
    EVERY_MINUTE = "every_minute"


class TextSize(Enum):
    """Text size options"""
    SMALL = "small"
    NORMAL = "normal"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


@dataclass
class GameSettings:
    """Comprehensive game settings"""
    
    # Display settings
    enable_colors: bool = True
    enable_emoji: bool = True
    text_size: TextSize = TextSize.NORMAL
    enable_ascii_art: bool = True
    wrap_at_width: int = 80
    
    # Quality of life
    auto_save_enabled: bool = True
    auto_save_frequency: SaveFrequency = SaveFrequency.AFTER_COMMAND
    quick_save_slot: int = -1  # Slot for quicksave (-1 = disabled)
    show_compass: bool = True
    show_health_bars: bool = True
    show_status_effects: bool = True
    
    # Gameplay
    difficulty_level: str = "normal"  # easy, normal, hard
    enable_tutorials: bool = True
    enable_hints: bool = True
    confirm_dangerous_actions: bool = True
    
    # Accessibility
    screen_reader_mode: bool = False
    high_contrast_mode: bool = False
    dyslexia_friendly_font: bool = False
    verbose_descriptions: bool = False
    
    # Performance
    reduce_animations: bool = False
    limit_fps: int = 0  # 0 = unlimited
    
    # Metadata
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["text_size"] = self.text_size.value
        data["auto_save_frequency"] = self.auto_save_frequency.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameSettings":
        """Create from dictionary"""
        # Convert enum values
        if "text_size" in data and isinstance(data["text_size"], str):
            data["text_size"] = TextSize(data["text_size"])
        if "auto_save_frequency" in data and isinstance(data["auto_save_frequency"], str):
            data["auto_save_frequency"] = SaveFrequency(data["auto_save_frequency"])
        
        # Remove unknown fields
        valid_fields = set(f.name for f in cls.__dataclass_fields__.values())
        data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**data)


class SettingsManager:
    """Manages game settings persistence and access"""
    
    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialize settings manager
        
        Args:
            settings_path: Path to settings file (defaults to config/game_settings.json)
        """
        self.settings_path = settings_path or (
            Path(__file__).resolve().parents[3] / "config" / "game_settings.json"
        )
        self.settings = self._load_settings()
    
    def _load_settings(self) -> GameSettings:
        """Load settings from file or create defaults"""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r") as f:
                    data = json.load(f)
                return GameSettings.from_dict(data)
            except (json.JSONDecodeError, ValueError, TypeError):
                print(f"Warning: Could not load settings from {self.settings_path}, using defaults")
                return GameSettings()
        else:
            return GameSettings()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, "w") as f:
                json.dump(self.settings.to_dict(), f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        if hasattr(self.settings, key):
            return getattr(self.settings, key)
        return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set setting value and save"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.settings.last_updated = datetime.now().isoformat()
            return self.save_settings()
        return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = GameSettings()
        return self.save_settings()


class QuickSaveManager:
    """Manages quick-save slots"""
    
    def __init__(self, saves_dir: Optional[Path] = None):
        """
        Initialize quick-save manager
        
        Args:
            saves_dir: Directory for save files
        """
        self.saves_dir = saves_dir or (Path(__file__).resolve().parents[3] / "saves")
        self.saves_dir.mkdir(parents=True, exist_ok=True)
    
    def get_quicksave_path(self, slot: int = 0) -> Path:
        """Get path for quicksave slot"""
        return self.saves_dir / f"quicksave_{slot}.json"
    
    def has_quicksave(self, slot: int = 0) -> bool:
        """Check if quicksave exists"""
        return self.get_quicksave_path(slot).exists()
    
    def delete_quicksave(self, slot: int = 0) -> bool:
        """Delete a quicksave"""
        path = self.get_quicksave_path(slot)
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False
    
    def get_quicksave_info(self, slot: int = 0) -> Optional[Dict[str, Any]]:
        """Get metadata about a quicksave"""
        path = self.get_quicksave_path(slot)
        if not path.exists():
            return None
        
        try:
            stat = path.stat()
            return {
                "slot": slot,
                "exists": True,
                "size_bytes": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        except (OSError, ValueError):
            return None


class CommandHistory:
    """Manages command history for quick recall"""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize command history
        
        Args:
            max_history: Maximum commands to keep in history
        """
        self.history: list[str] = []
        self.max_history = max_history
        self.current_index = -1
    
    def add(self, command: str) -> None:
        """Add command to history"""
        if command.strip():
            self.history.append(command)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self.current_index = -1  # Reset position
    
    def previous(self) -> Optional[str]:
        """Get previous command"""
        if not self.history:
            return None
        
        if self.current_index == -1:
            self.current_index = len(self.history) - 1
        elif self.current_index > 0:
            self.current_index -= 1
        
        return self.history[self.current_index] if 0 <= self.current_index < len(self.history) else None
    
    def next(self) -> Optional[str]:
        """Get next command"""
        if not self.history or self.current_index == -1:
            return None
        
        self.current_index += 1
        if self.current_index >= len(self.history):
            self.current_index = -1
            return None
        
        return self.history[self.current_index]
    
    def search(self, prefix: str) -> list[str]:
        """Search history for commands starting with prefix"""
        return [cmd for cmd in self.history if cmd.lower().startswith(prefix.lower())]
    
    def clear(self) -> None:
        """Clear history"""
        self.history.clear()
        self.current_index = -1
    
    def get_recent(self, count: int = 10) -> list[str]:
        """Get most recent commands"""
        return self.history[-count:] if self.history else []


__all__ = [
    "GameSettings",
    "SaveFrequency",
    "TextSize",
    "SettingsManager",
    "QuickSaveManager",
    "CommandHistory",
]
