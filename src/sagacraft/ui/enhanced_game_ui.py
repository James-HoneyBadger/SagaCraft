#!/usr/bin/env python3
"""SagaCraft - Enhanced Player UI Integration

Integrates all Phase I improvements into the game player.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json

from sagacraft.ui.text_formatting import (
    RichTextFormatter,
    TextCategory,
    HealthBar,
    CompassRose,
    ASCIIArt,
    TextColor,
)
from sagacraft.ui.game_settings import (
    SettingsManager,
    GameSettings,
    CommandHistory,
)
from sagacraft.ui.auto_save import AutoSaveSystem


class EnhancedGameDisplay:
    """Enhanced display system for game output"""
    
    def __init__(self, settings: Optional[GameSettings] = None):
        """
        Initialize enhanced display
        
        Args:
            settings: Game settings (uses defaults if None)
        """
        self.settings = settings or GameSettings()
        self.formatter = RichTextFormatter(enabled=self.settings.enable_colors)
        self.screen_width = self.settings.wrap_at_width
    
    def display_room(
        self,
        room_name: str,
        description: str,
        exits: Dict[str, int],
        show_compass: bool = True
    ) -> str:
        """
        Display a room with enhanced formatting
        
        Args:
            room_name: Room name
            description: Room description
            exits: Dictionary of exits
            show_compass: Whether to show compass
            
        Returns:
            Formatted room display
        """
        lines = []
        
        # Room name header
        header = self.formatter.colorize(
            f"\n{'='*self.screen_width}\n{room_name}\n{'='*self.screen_width}",
            TextCategory.SYSTEM,
            bold=True
        )
        lines.append(header)
        
        # Room description
        wrapped_desc = self.formatter.wrap_text(description, width=self.screen_width)
        lines.append(wrapped_desc)
        
        # Compass
        if show_compass and exits:
            lines.append("")
            compass = CompassRose.simple_compass(list(exits.keys()))
            lines.append(self.formatter.colorize(compass, TextCategory.SYSTEM))
        
        return "\n".join(lines)
    
    def display_status(
        self,
        name: str,
        level: int,
        health: int,
        max_health: int,
        additional_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Display player status with health bar
        
        Args:
            name: Character name
            level: Character level
            health: Current health
            max_health: Maximum health
            additional_stats: Additional stats to display
            
        Returns:
            Formatted status display
        """
        lines = []
        
        # Header
        header = self.formatter.colorize(
            f"\n{'─'*self.screen_width}",
            TextCategory.SYSTEM
        )
        lines.append(header)
        
        # Name and level
        char_line = self.formatter.format_status_line(
            "Character",
            f"{name} (Level {level})",
            TextColor.BRIGHT_CYAN
        )
        lines.append(char_line)
        
        # Health bar
        health_bar = HealthBar.create_bar(health, max_health, width=30)
        health_display = self.formatter.format_status_line(
            "Health",
            health_bar,
            TextColor.BRIGHT_RED
        )
        lines.append(health_display)
        
        # Additional stats
        if additional_stats:
            for stat_name, stat_value in additional_stats.items():
                stat_display = self.formatter.format_status_line(
                    stat_name.title(),
                    str(stat_value),
                    TextColor.BRIGHT_YELLOW
                )
                lines.append(stat_display)
        
        lines.append(self.formatter.colorize(
            f"{'─'*self.screen_width}",
            TextCategory.SYSTEM
        ))
        
        return "\n".join(lines)
    
    def display_message(
        self,
        message: str,
        category: TextCategory = TextCategory.ACTION
    ) -> str:
        """
        Display a colored message
        
        Args:
            message: Message text
            category: Text category for coloring
            
        Returns:
            Formatted message
        """
        return self.formatter.colorize(message, category)
    
    def display_success(self, message: str) -> str:
        """Display success message"""
        return self.formatter.colorize(message, TextCategory.SUCCESS, bold=True)
    
    def display_error(self, message: str) -> str:
        """Display error message"""
        return self.formatter.colorize(message, TextCategory.ERROR, bold=True)
    
    def display_warning(self, message: str) -> str:
        """Display warning message"""
        return self.formatter.colorize(message, TextCategory.WARNING, bold=True)
    
    def display_dialog(self, npc_name: str, dialog_text: str) -> str:
        """
        Display NPC dialogue
        
        Args:
            npc_name: Name of NPC
            dialog_text: Dialogue text
            
        Returns:
            Formatted dialogue
        """
        lines = []
        npc_header = self.formatter.colorize(
            f"{npc_name}:",
            TextCategory.DIALOGUE,
            bold=True
        )
        lines.append(npc_header)
        
        wrapped_dialog = self.formatter.wrap_text(
            dialog_text,
            width=self.screen_width - 4,
            indent=2
        )
        lines.append(wrapped_dialog)
        
        return "\n".join(lines)


class EnhancedGameSession:
    """Main enhanced game session manager"""
    
    def __init__(self, saves_dir: Optional[Path] = None):
        """
        Initialize enhanced game session
        
        Args:
            saves_dir: Directory for saves
        """
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        self.command_history = CommandHistory(max_history=100)
        self.auto_save = AutoSaveSystem(saves_dir)
        self.display = EnhancedGameDisplay(self.settings)
        
        # Configure auto-save
        if self.settings.auto_save_enabled:
            self._configure_auto_save()
    
    def _configure_auto_save(self) -> None:
        """Configure auto-save based on settings"""
        from sagacraft.ui.game_settings import SaveFrequency
        
        freq = self.settings.auto_save_frequency
        
        if freq == SaveFrequency.DISABLED:
            self.auto_save.enable_auto_save(False)
        elif freq == SaveFrequency.AFTER_COMMAND:
            self.auto_save.enable_auto_save(True, command_threshold=1)
        elif freq == SaveFrequency.EVERY_5_COMMANDS:
            self.auto_save.enable_auto_save(True, command_threshold=5)
        elif freq == SaveFrequency.EVERY_10_COMMANDS:
            self.auto_save.enable_auto_save(True, command_threshold=10)
        elif freq == SaveFrequency.EVERY_MINUTE:
            self.auto_save.enable_auto_save(True, interval=60)
    
    def record_command(self, command: str) -> None:
        """Record command in history"""
        self.command_history.add(command)
        
        # Check if we should auto-save
        if self.auto_save.on_command_executed():
            # Auto-save would happen here with game state
            pass
    
    def get_recent_commands(self, count: int = 5) -> list[str]:
        """Get recent commands"""
        return self.command_history.get_recent(count)
    
    def search_history(self, prefix: str) -> list[str]:
        """Search command history"""
        return self.command_history.search(prefix)
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a setting and refresh display"""
        if self.settings_manager.set(key, value):
            # Refresh affected components
            if key == "enable_colors":
                self.display.formatter.enabled = value
            elif key == "wrap_at_width":
                self.display.screen_width = value
            return True
        return False
    
    def shutdown(self) -> None:
        """Clean up resources"""
        self.auto_save.shutdown()


__all__ = [
    "EnhancedGameDisplay",
    "EnhancedGameSession",
]
