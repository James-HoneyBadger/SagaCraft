#!/usr/bin/env python3
"""SagaCraft - Rich Text Formatting System

Provides text formatting, coloring, ASCII art support, and dynamic text wrapping
for immersive text output.
"""

from enum import Enum
from typing import Optional, List, Dict, Tuple
import textwrap
import re


class TextColor(Enum):
    """ANSI color codes for terminal output"""
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Reset
    RESET = "\033[0m"


class TextCategory(Enum):
    """Categories of game text"""
    
    DESCRIPTION = "description"  # Room/object descriptions
    ACTION = "action"              # Player actions and results
    DIALOGUE = "dialogue"          # NPC dialogue
    SYSTEM = "system"              # System messages
    WARNING = "warning"            # Warnings and important info
    SUCCESS = "success"            # Success messages
    ERROR = "error"                # Error messages
    STAT = "stat"                  # Stat displays


class RichTextFormatter:
    """Handles rich text formatting with colors and styles"""
    
    def __init__(self, enabled: bool = True):
        """
        Initialize formatter
        
        Args:
            enabled: Whether to apply ANSI codes (disable for plain text)
        """
        self.enabled = enabled
        self.color_map: Dict[TextCategory, TextColor] = {
            TextCategory.DESCRIPTION: TextColor.CYAN,
            TextCategory.ACTION: TextColor.GREEN,
            TextCategory.DIALOGUE: TextColor.MAGENTA,
            TextCategory.SYSTEM: TextColor.YELLOW,
            TextCategory.WARNING: TextColor.BRIGHT_RED,
            TextCategory.SUCCESS: TextColor.BRIGHT_GREEN,
            TextCategory.ERROR: TextColor.RED,
            TextCategory.STAT: TextColor.BRIGHT_BLUE,
        }
    
    def colorize(
        self,
        text: str,
        category: TextCategory,
        bold: bool = False,
        underline: bool = False
    ) -> str:
        """
        Apply color to text based on category
        
        Args:
            text: Text to colorize
            category: TextCategory for color selection
            bold: Whether to make text bold
            underline: Whether to underline text
            
        Returns:
            Colored text (or original if disabled)
        """
        if not self.enabled or not text:
            return text
        
        codes = [self.color_map[category].value]
        
        if bold:
            codes.append(TextColor.BOLD.value)
        if underline:
            codes.append(TextColor.UNDERLINE.value)
        
        return "".join(codes) + text + TextColor.RESET.value
    
    def format_status_line(self, label: str, value: str, color: TextColor = TextColor.BRIGHT_BLUE) -> str:
        """Format a status line with label and value"""
        if not self.enabled:
            return f"{label}: {value}"
        
        return f"{color.value}{label}:{TextColor.RESET.value} {value}"
    
    def format_header(self, text: str, color: TextColor = TextColor.BRIGHT_CYAN) -> str:
        """Format a header with bold and color"""
        return self.colorize(text, TextCategory.SYSTEM, bold=True)
    
    def wrap_text(self, text: str, width: int = 80, indent: int = 0) -> str:
        """
        Wrap text to specified width while preserving ANSI codes
        
        Args:
            text: Text to wrap (may contain ANSI codes)
            width: Maximum line width
            indent: Number of spaces to indent each line
            
        Returns:
            Wrapped text
        """
        # Remove ANSI codes for length calculation
        clean_text = self._remove_ansi(text)
        
        # Wrap clean text
        lines = textwrap.wrap(clean_text, width=width - indent)
        
        # Add indentation
        if indent > 0:
            lines = [" " * indent + line for line in lines]
        
        return "\n".join(lines)
    
    @staticmethod
    def _remove_ansi(text: str) -> str:
        """Remove ANSI color codes from text"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    @staticmethod
    def strip_colors(text: str) -> str:
        """Remove all color codes (alias for _remove_ansi)"""
        return RichTextFormatter._remove_ansi(text)


class HealthBar:
    """Creates visual health bar representations"""
    
    @staticmethod
    def create_bar(
        current: int,
        maximum: int,
        width: int = 20,
        full_char: str = "█",
        empty_char: str = "░"
    ) -> str:
        """
        Create a health bar string
        
        Args:
            current: Current health
            maximum: Maximum health
            width: Bar width in characters
            full_char: Character for filled portion
            empty_char: Character for empty portion
            
        Returns:
            Health bar string
        """
        if maximum <= 0:
            percentage = 0
        else:
            percentage = current / maximum
        
        filled = int(width * percentage)
        empty = width - filled
        
        bar = full_char * filled + empty_char * empty
        
        # Color based on health percentage
        if percentage >= 0.75:
            color = TextColor.BRIGHT_GREEN.value
        elif percentage >= 0.5:
            color = TextColor.BRIGHT_YELLOW.value
        elif percentage >= 0.25:
            color = TextColor.BRIGHT_RED.value
        else:
            color = TextColor.RED.value
        
        return f"{color}[{bar}]{TextColor.RESET.value} {current}/{maximum}"


class CompassRose:
    """Creates ASCII compass for navigation"""
    
    @staticmethod
    def simple_compass(exits: List[str]) -> str:
        """
        Create a simple compass showing available exits
        
        Args:
            exits: List of available exit directions
            
        Returns:
            Formatted compass rose
        """
        compass = {
            "north": "↑ N",
            "south": "↓ S",
            "east": "→ E",
            "west": "← W",
            "northeast": "↗ NE",
            "northwest": "↖ NW",
            "southeast": "↘ SE",
            "southwest": "↙ SW",
            "up": "⬆ Up",
            "down": "⬇ Down",
        }
        
        available = []
        for exit_dir in exits:
            if exit_dir.lower() in compass:
                available.append(compass[exit_dir.lower()])
        
        if not available:
            return "(No visible exits)"
        
        return "   Exits: " + " | ".join(available)
    
    @staticmethod
    def detailed_compass(exits: Dict[str, int]) -> str:
        """
        Create a detailed compass with room destinations
        
        Args:
            exits: Dict mapping directions to room IDs
            
        Returns:
            Formatted compass with connections
        """
        directions = {
            "north": "↑ N",
            "south": "↓ S",
            "east": "→ E",
            "west": "← W",
            "northeast": "↗ NE",
            "northwest": "↖ NW",
            "southeast": "↘ SE",
            "southwest": "↙ SW",
            "up": "⬆ Up",
            "down": "⬇ Down",
        }
        
        lines = ["Available exits:"]
        for direction, room_id in exits.items():
            if direction.lower() in directions:
                symbol = directions[direction.lower()]
                lines.append(f"  {symbol} → Room {room_id}")
        
        return "\n".join(lines)


class ASCIIArt:
    """Handles ASCII art and box drawing"""
    
    @staticmethod
    def box(content: str, width: int = 40, title: Optional[str] = None) -> str:
        """
        Create a box around content
        
        Args:
            content: Text to box
            width: Box width
            title: Optional title for top of box
            
        Returns:
            Boxed text
        """
        lines = [
            "┌" + "─" * (width - 2) + "┐",
        ]
        
        if title:
            title_text = f" {title} "
            padding = (width - 2 - len(title_text)) // 2
            lines[0] = "┌" + "─" * padding + title_text + "─" * (width - 2 - padding - len(title_text)) + "┐"
        
        wrapped = textwrap.wrap(content, width=width - 4)
        for line in wrapped:
            lines.append("│ " + line.ljust(width - 3) + "│")
        
        lines.append("└" + "─" * (width - 2) + "┘")
        
        return "\n".join(lines)
    
    @staticmethod
    def horizontal_rule(width: int = 80, char: str = "─") -> str:
        """Create a horizontal rule"""
        return char * width
    
    @staticmethod
    def separator(width: int = 80) -> str:
        """Create a decorative separator"""
        return "═" * width


def format_game_text(
    text: str,
    category: TextCategory = TextCategory.DESCRIPTION,
    color_enabled: bool = True
) -> str:
    """
    Convenience function to format text
    
    Args:
        text: Text to format
        category: Text category
        color_enabled: Whether to enable colors
        
    Returns:
        Formatted text
    """
    formatter = RichTextFormatter(enabled=color_enabled)
    return formatter.colorize(text, category)


# Export common colors for direct use
__all__ = [
    "TextColor",
    "TextCategory",
    "RichTextFormatter",
    "HealthBar",
    "CompassRose",
    "ASCIIArt",
    "format_game_text",
]
