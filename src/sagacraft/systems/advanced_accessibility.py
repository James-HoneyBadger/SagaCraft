"""Advanced Accessibility System - text-to-speech, dyslexia support, speed controls, etc."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import re


class AccessibilityFeature(Enum):
    """Supported accessibility features."""
    TEXT_TO_SPEECH = "text_to_speech"
    DYSLEXIA_FRIENDLY = "dyslexia_friendly"
    HIGH_CONTRAST = "high_contrast"
    SCREEN_READER = "screen_reader"
    COLORBLIND_MODE = "colorblind_mode"
    REDUCED_MOTION = "reduced_motion"
    ADJUSTABLE_SPEED = "adjustable_speed"
    LARGE_TEXT = "large_text"
    SIMPLIFIED_LANGUAGE = "simplified_language"


class ColorblindMode(Enum):
    """Types of colorblindness to support."""
    PROTANOPIA = "protanopia"  # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"  # Blue-yellow blind
    ACHROMATOPSIA = "achromatopsia"  # Total colorblindness


@dataclass
class AccessibilityProfile:
    """User accessibility preferences."""
    user_id: str
    enabled_features: List[AccessibilityFeature] = field(default_factory=list)
    text_size: int = 100  # 50-200%
    game_speed: float = 1.0  # 0.5x - 2.0x
    colorblind_mode: Optional[ColorblindMode] = None
    dyslexia_font: bool = False
    high_contrast: bool = False
    reduce_motion: bool = False
    text_to_speech_voice: str = "default"
    text_to_speech_speed: float = 1.0  # 0.5x - 2.0x
    text_to_speech_enabled: bool = False
    screen_reader_enabled: bool = False
    auto_read_descriptions: bool = False
    simplified_language: bool = False


@dataclass
class AccessibilityStatistic:
    """Statistics about accessibility feature usage."""
    user_id: str
    features_enabled: int = 0
    total_play_time_hours: float = 0.0
    feedback_provided: int = 0
    accessibility_score: int = 0  # 0-100 (higher = more accessible)


class DyslexiaFontConverter:
    """Converts text to dyslexia-friendly format."""

    # Common dyslexia-friendly substitutions (based on OpenDyslexic principles)
    DYSLEXIA_MAPPINGS = {
        # Make similar letters distinct
        'l': 'ł',  # lowercase L with stroke
        'b': 'ḃ',  # better distinction
        'd': 'ḋ',  # better distinction
        'p': 'ṗ',  # better distinction
        'q': 'q̃',  # better distinction
    }

    @staticmethod
    def convert(text: str) -> str:
        """Convert text to dyslexia-friendly font."""
        result = text
        # Add extra letter spacing
        result = ' '.join(result)
        # Add visual weight bottom
        result = result.replace('a', 'a̲').replace('o', 'o̲')
        return result


class TextToSpeechManager:
    """Manages text-to-speech for accessibility."""

    VOICE_PROFILES = {
        "default": {"gender": "neutral", "speed": 1.0},
        "female": {"gender": "female", "speed": 1.0},
        "male": {"gender": "male", "speed": 1.0},
        "robotic": {"gender": "neutral", "speed": 1.2},
        "slow": {"gender": "neutral", "speed": 0.75},
        "fast": {"gender": "neutral", "speed": 1.5},
    }

    def __init__(self):
        self.playback_history: Dict[str, List[str]] = {}

    def synthesize_text(
        self,
        text: str,
        voice_profile: str = "default",
        speed: float = 1.0
    ) -> Tuple[bool, str]:
        """
        Convert text to speech (simulated).
        In production, would use actual TTS service like Azure Speech Services.
        """
        if voice_profile not in self.VOICE_PROFILES:
            return False, "Invalid voice profile"

        if not (0.5 <= speed <= 2.0):
            return False, "Speed must be between 0.5 and 2.0"

        # In real implementation, would generate audio file
        # For now, return success
        return True, f"Speech synthesis queued: {len(text)} characters"

    def add_to_playback_history(self, user_id: str, text: str) -> None:
        """Track TTS history for user."""
        if user_id not in self.playback_history:
            self.playback_history[user_id] = []
        self.playback_history[user_id].append(text)


class ColorblindModeConverter:
    """Adapts color schemes for colorblind users."""

    # Common game colors and their colorblind-safe alternatives
    COLOR_PALETTE = {
        "protanopia": {
            "red": "#0173B2",    # Blue instead of red
            "green": "#029E73",  # Teal instead of green
            "blue": "#D55E00",   # Orange instead of blue
        },
        "deuteranopia": {
            "red": "#0173B2",    # Blue instead of red
            "green": "#CC78BC",  # Purple instead of green
            "blue": "#D55E00",   # Orange instead of blue
        },
        "tritanopia": {
            "red": "#0173B2",    # Keep red as blue
            "green": "#E69F00",  # Yellow instead of green
            "blue": "#D55E00",   # Orange instead of blue
        },
        "achromatopsia": {
            "red": "#000000",
            "green": "#CCCCCC",
            "blue": "#FFFFFF",
        }
    }

    @staticmethod
    def convert_color(
        color: str,
        colorblind_mode: ColorblindMode
    ) -> str:
        """Convert a color to colorblind-friendly alternative."""
        mode_name = colorblind_mode.value
        palette = ColorblindModeConverter.COLOR_PALETTE.get(mode_name, {})

        # Simple lookup
        for key, value in palette.items():
            if key in color.lower():
                return value

        return color

    @staticmethod
    def get_high_contrast_palette(colorblind_mode: Optional[ColorblindMode] = None) -> Dict:
        """Get high contrast color palette."""
        base_palette = {
            "background": "#000000",
            "foreground": "#FFFFFF",
            "accent1": "#FFFF00",
            "accent2": "#00FFFF",
            "accent3": "#FF00FF",
        }

        if colorblind_mode:
            # Apply colorblind conversion to accent colors
            base_palette["accent1"] = ColorblindModeConverter.convert_color(
                "#FFFF00", colorblind_mode
            )

        return base_palette


class ScreenReaderOptimizer:
    """Optimizes content for screen readers."""

    @staticmethod
    def create_aria_labels(content: Dict) -> Dict:
        """Create ARIA labels for screen reader compatibility."""
        return {
            "role": content.get("type", "generic"),
            "aria-label": content.get("description", ""),
            "aria-describedby": f"desc_{content.get('id', 'unknown')}",
            "aria-live": "polite" if content.get("important") else "off",
        }

    @staticmethod
    def create_semantic_structure(text: str) -> str:
        """Create semantically structured text for screen readers."""
        # Add section markers
        result = text
        result = re.sub(r'^(.*?):$', r'[SECTION: \1]', result, flags=re.MULTILINE)
        result = re.sub(r'^(-|•|→)', r'[LIST ITEM]', result, flags=re.MULTILINE)
        return result


class AccessibilityManager:
    """Central manager for all accessibility features."""

    def __init__(self):
        self.profiles: Dict[str, AccessibilityProfile] = {}
        self.statistics: Dict[str, AccessibilityStatistic] = {}
        self.tts_manager = TextToSpeechManager()
        self.screen_reader = ScreenReaderOptimizer()

    def create_profile(self, user_id: str) -> AccessibilityProfile:
        """Create accessibility profile for user."""
        profile = AccessibilityProfile(user_id=user_id)
        self.profiles[user_id] = profile
        self.statistics[user_id] = AccessibilityStatistic(user_id=user_id)
        return profile

    def get_profile(self, user_id: str) -> AccessibilityProfile:
        """Get user's accessibility profile."""
        if user_id not in self.profiles:
            return self.create_profile(user_id)
        return self.profiles[user_id]

    def enable_feature(self, user_id: str, feature: AccessibilityFeature) -> Tuple[bool, str]:
        """Enable an accessibility feature."""
        profile = self.get_profile(user_id)

        if feature not in profile.enabled_features:
            profile.enabled_features.append(feature)

            # Apply feature-specific settings
            if feature == AccessibilityFeature.DYSLEXIA_FRIENDLY:
                profile.dyslexia_font = True
            elif feature == AccessibilityFeature.HIGH_CONTRAST:
                profile.high_contrast = True
            elif feature == AccessibilityFeature.TEXT_TO_SPEECH:
                profile.text_to_speech_enabled = True
            elif feature == AccessibilityFeature.SCREEN_READER:
                profile.screen_reader_enabled = True
            elif feature == AccessibilityFeature.REDUCED_MOTION:
                profile.reduce_motion = True

            return True, f"Enabled {feature.value}"

        return False, f"{feature.value} already enabled"

    def disable_feature(self, user_id: str, feature: AccessibilityFeature) -> Tuple[bool, str]:
        """Disable an accessibility feature."""
        profile = self.get_profile(user_id)

        if feature in profile.enabled_features:
            profile.enabled_features.remove(feature)
            return True, f"Disabled {feature.value}"

        return False, f"{feature.value} not enabled"

    def set_text_size(self, user_id: str, size: int) -> Tuple[bool, str]:
        """Set text size percentage."""
        if not (50 <= size <= 200):
            return False, "Text size must be between 50% and 200%"

        profile = self.get_profile(user_id)
        profile.text_size = size
        return True, f"Text size set to {size}%"

    def set_game_speed(self, user_id: str, speed: float) -> Tuple[bool, str]:
        """Set game speed multiplier."""
        if not (0.5 <= speed <= 2.0):
            return False, "Game speed must be between 0.5x and 2.0x"

        profile = self.get_profile(user_id)
        profile.game_speed = speed
        return True, f"Game speed set to {speed}x"

    def set_colorblind_mode(
        self,
        user_id: str,
        mode: Optional[ColorblindMode]
    ) -> Tuple[bool, str]:
        """Set colorblind mode."""
        profile = self.get_profile(user_id)
        profile.colorblind_mode = mode
        return True, f"Colorblind mode set to {mode.value if mode else 'off'}"

    def process_text_with_accessibility(
        self,
        user_id: str,
        text: str
    ) -> str:
        """Process text according to user's accessibility settings."""
        profile = self.get_profile(user_id)
        result = text

        # Apply dyslexia font
        if profile.dyslexia_font:
            result = DyslexiaFontConverter.convert(result)

        # Apply simplified language
        if profile.simplified_language:
            result = self._simplify_language(result)

        return result

    def _simplify_language(self, text: str) -> str:
        """Simplify complex language."""
        simplifications = {
            "magnificent": "great",
            "peculiar": "strange",
            "embark": "start",
            "traverse": "walk",
            "summon": "call",
            "encounter": "meet",
            "behold": "see",
        }

        result = text
        for complex_word, simple_word in simplifications.items():
            result = re.sub(
                f'\\b{complex_word}\\b',
                simple_word,
                result,
                flags=re.IGNORECASE
            )
        return result

    def get_accessibility_report(self, user_id: str) -> Dict:
        """Generate accessibility feature usage report."""
        profile = self.get_profile(user_id)
        stats = self.statistics.get(user_id)

        return {
            "user_id": user_id,
            "features_enabled": len(profile.enabled_features),
            "feature_list": [f.value for f in profile.enabled_features],
            "text_size": f"{profile.text_size}%",
            "game_speed": f"{profile.game_speed}x",
            "colorblind_mode": profile.colorblind_mode.value if profile.colorblind_mode else "off",
            "dyslexia_friendly": profile.dyslexia_font,
            "high_contrast": profile.high_contrast,
            "tts_enabled": profile.text_to_speech_enabled,
            "screen_reader_enabled": profile.screen_reader_enabled,
            "total_play_time": f"{stats.total_play_time_hours:.1f} hours" if stats else "N/A",
        }
