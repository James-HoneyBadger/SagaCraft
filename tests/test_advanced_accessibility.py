"""Tests for Advanced Accessibility system."""

import unittest
from sagacraft.systems.advanced_accessibility import (
    AccessibilityManager,
    AccessibilityFeature,
    ColorblindMode,
    DyslexiaFontConverter,
    TextToSpeechManager,
    ColorblindModeConverter,
    ScreenReaderOptimizer,
)


class TestAccessibilityManager(unittest.TestCase):
    """Test the accessibility manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = AccessibilityManager()
        self.user_id = "test_user"

    def test_create_profile(self):
        """Test creating accessibility profile."""
        profile = self.manager.create_profile(self.user_id)

        self.assertEqual(profile.user_id, self.user_id)
        self.assertEqual(len(profile.enabled_features), 0)
        self.assertEqual(profile.text_size, 100)
        self.assertEqual(profile.game_speed, 1.0)

    def test_enable_feature(self):
        """Test enabling accessibility feature."""
        success, msg = self.manager.enable_feature(
            self.user_id,
            AccessibilityFeature.DYSLEXIA_FRIENDLY
        )

        self.assertTrue(success)
        profile = self.manager.get_profile(self.user_id)
        self.assertIn(AccessibilityFeature.DYSLEXIA_FRIENDLY, profile.enabled_features)
        self.assertTrue(profile.dyslexia_font)

    def test_disable_feature(self):
        """Test disabling accessibility feature."""
        self.manager.enable_feature(self.user_id, AccessibilityFeature.HIGH_CONTRAST)
        success, msg = self.manager.disable_feature(
            self.user_id,
            AccessibilityFeature.HIGH_CONTRAST
        )

        self.assertTrue(success)
        profile = self.manager.get_profile(self.user_id)
        self.assertNotIn(AccessibilityFeature.HIGH_CONTRAST, profile.enabled_features)

    def test_set_text_size(self):
        """Test setting text size."""
        success, msg = self.manager.set_text_size(self.user_id, 150)

        self.assertTrue(success)
        profile = self.manager.get_profile(self.user_id)
        self.assertEqual(profile.text_size, 150)

    def test_text_size_boundaries(self):
        """Test text size boundary validation."""
        # Too small
        success, msg = self.manager.set_text_size(self.user_id, 30)
        self.assertFalse(success)

        # Too large
        success, msg = self.manager.set_text_size(self.user_id, 250)
        self.assertFalse(success)

        # Valid
        success, msg = self.manager.set_text_size(self.user_id, 100)
        self.assertTrue(success)

    def test_set_game_speed(self):
        """Test setting game speed."""
        success, msg = self.manager.set_game_speed(self.user_id, 1.5)

        self.assertTrue(success)
        profile = self.manager.get_profile(self.user_id)
        self.assertEqual(profile.game_speed, 1.5)

    def test_game_speed_boundaries(self):
        """Test game speed boundary validation."""
        # Too slow
        success, msg = self.manager.set_game_speed(self.user_id, 0.2)
        self.assertFalse(success)

        # Too fast
        success, msg = self.manager.set_game_speed(self.user_id, 3.0)
        self.assertFalse(success)

        # Valid
        success, msg = self.manager.set_game_speed(self.user_id, 0.75)
        self.assertTrue(success)

    def test_set_colorblind_mode(self):
        """Test setting colorblind mode."""
        success, msg = self.manager.set_colorblind_mode(
            self.user_id,
            ColorblindMode.DEUTERANOPIA
        )

        self.assertTrue(success)
        profile = self.manager.get_profile(self.user_id)
        self.assertEqual(profile.colorblind_mode, ColorblindMode.DEUTERANOPIA)

    def test_process_text_with_accessibility(self):
        """Test text processing with accessibility settings."""
        profile = self.manager.get_profile(self.user_id)
        profile.dyslexia_font = True

        text = "Hello world"
        processed = self.manager.process_text_with_accessibility(self.user_id, text)

        self.assertNotEqual(text, processed)

    def test_accessibility_report(self):
        """Test accessibility report generation."""
        self.manager.enable_feature(self.user_id, AccessibilityFeature.DYSLEXIA_FRIENDLY)
        self.manager.set_text_size(self.user_id, 150)

        report = self.manager.get_accessibility_report(self.user_id)

        self.assertIn("features_enabled", report)
        self.assertEqual(report["text_size"], "150%")
        self.assertEqual(report["dyslexia_friendly"], True)


class TestColorblindModeConverter(unittest.TestCase):
    """Test colorblind mode conversion."""

    def test_protanopia_conversion(self):
        """Test protanopia (red-blind) color conversion."""
        color = ColorblindModeConverter.convert_color("red", ColorblindMode.PROTANOPIA)
        self.assertEqual(color, "#0173B2")  # Converts to blue

    def test_deuteranopia_conversion(self):
        """Test deuteranopia (green-blind) color conversion."""
        color = ColorblindModeConverter.convert_color("green", ColorblindMode.DEUTERANOPIA)
        self.assertEqual(color, "#CC78BC")  # Converts to purple

    def test_high_contrast_palette(self):
        """Test high contrast palette generation."""
        palette = ColorblindModeConverter.get_high_contrast_palette()

        self.assertIn("background", palette)
        self.assertIn("foreground", palette)
        self.assertEqual(palette["background"], "#000000")
        self.assertEqual(palette["foreground"], "#FFFFFF")

    def test_high_contrast_with_colorblind(self):
        """Test high contrast palette with colorblind mode."""
        palette = ColorblindModeConverter.get_high_contrast_palette(ColorblindMode.PROTANOPIA)

        self.assertIn("accent1", palette)
        # Palette should be created successfully
        self.assertIsNotNone(palette["accent1"])


class TestDyslexiaFontConverter(unittest.TestCase):
    """Test dyslexia font conversion."""

    def test_dyslexia_conversion(self):
        """Test dyslexia-friendly text conversion."""
        text = "hello"
        converted = DyslexiaFontConverter.convert(text)

        # Should be different from original
        self.assertNotEqual(text, converted)
        # Should contain some modified characters
        self.assertIn(" ", converted)  # Should have extra spacing


class TestTextToSpeechManager(unittest.TestCase):
    """Test text-to-speech manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.tts = TextToSpeechManager()

    def test_synthesize_text(self):
        """Test text synthesis."""
        success, msg = self.tts.synthesize_text("Hello world")
        self.assertTrue(success)

    def test_invalid_voice_profile(self):
        """Test invalid voice profile."""
        success, msg = self.tts.synthesize_text(
            "Hello",
            voice_profile="invalid_voice"
        )
        self.assertFalse(success)

    def test_invalid_speed(self):
        """Test invalid TTS speed."""
        success, msg = self.tts.synthesize_text(
            "Hello",
            speed=3.0
        )
        self.assertFalse(success)

    def test_playback_history(self):
        """Test TTS playback history tracking."""
        user_id = "test_user"
        self.tts.add_to_playback_history(user_id, "Hello")
        self.tts.add_to_playback_history(user_id, "World")

        history = self.tts.playback_history[user_id]
        self.assertEqual(len(history), 2)


class TestScreenReaderOptimizer(unittest.TestCase):
    """Test screen reader optimization."""

    def test_aria_labels(self):
        """Test ARIA label creation."""
        content = {"type": "button", "description": "Close menu", "id": "close_btn"}
        labels = ScreenReaderOptimizer.create_aria_labels(content)

        self.assertIn("aria-label", labels)
        self.assertEqual(labels["aria-label"], "Close menu")
        self.assertEqual(labels["role"], "button")

    def test_semantic_structure(self):
        """Test semantic structure creation."""
        text = "Main Content:\nItem 1\nItem 2"
        structured = ScreenReaderOptimizer.create_semantic_structure(text)

        self.assertIn("[SECTION:", structured)


if __name__ == "__main__":
    unittest.main()
