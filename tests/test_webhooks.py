"""Tests for the Webhook Integration system."""

import unittest
from sagacraft.systems.webhooks import (
    WebhookSystem,
    WebhookEventType,
    DiscordIntegration,
    TwitchIntegration,
)


class TestDiscordIntegration(unittest.TestCase):
    """Test Discord integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.discord = DiscordIntegration()

    def test_register_webhook(self):
        """Test webhook registration."""
        config = self.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.ACHIEVEMENT_UNLOCKED]
        )

        self.assertIsNotNone(config.webhook_id)
        self.assertEqual(config.webhook_url, "https://discord.com/api/webhooks/test")
        self.assertIn(WebhookEventType.ACHIEVEMENT_UNLOCKED, config.event_types)

    def test_unregister_webhook(self):
        """Test webhook removal."""
        config = self.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.ACHIEVEMENT_UNLOCKED]
        )

        success, msg = self.discord.unregister_webhook(config.webhook_id)
        self.assertTrue(success)
        self.assertNotIn(config.webhook_id, self.discord.webhooks)

    def test_discord_commands_registered(self):
        """Test default Discord commands registration."""
        self.assertGreater(len(self.discord.commands), 0)
        self.assertIn("sagacraft-check", self.discord.commands)
        self.assertIn("sagacraft-stats", self.discord.commands)

    def test_achievement_embed_format(self):
        """Test achievement embed formatting."""
        embed = self.discord.create_achievement_embed(
            "TestPlayer",
            "First Quest",
            "Complete your first quest"
        )

        self.assertEqual(embed["title"], "🏆 Achievement Unlocked!")
        self.assertIn("TestPlayer", embed["description"])
        self.assertGreater(len(embed["fields"]), 0)

    def test_quest_embed_format(self):
        """Test quest completion embed."""
        embed = self.discord.create_quest_embed(
            "TestPlayer",
            "Rescue the Princess",
            "1000 gold"
        )

        self.assertEqual(embed["title"], "✅ Quest Completed!")
        self.assertIn("TestPlayer", embed["description"])

    def test_pvp_embed_format(self):
        """Test PvP victory embed."""
        embed = self.discord.create_pvp_embed(
            "Winner",
            "Loser",
            +25
        )

        self.assertEqual(embed["title"], "⚔️ PvP Victory!")
        self.assertIn("Winner", embed["description"])

    def test_trigger_event(self):
        """Test event triggering."""
        self.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.ACHIEVEMENT_UNLOCKED]
        )

        triggered = self.discord.trigger_event(
            WebhookEventType.ACHIEVEMENT_UNLOCKED,
            {"achievement": "test"}
        )

        self.assertGreater(len(triggered), 0)


class TestTwitchIntegration(unittest.TestCase):
    """Test Twitch integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.twitch = TwitchIntegration()

    def test_connect_to_channel(self):
        """Test Twitch channel connection."""
        success, msg = self.twitch.connect("test_channel")

        self.assertTrue(success)
        self.assertEqual(self.twitch.channel_id, "test_channel")
        self.assertTrue(self.twitch.connected)

    def test_update_overlay(self):
        """Test overlay data updates."""
        self.twitch.update_overlay("player_level", "10")
        self.twitch.update_overlay("player_health", "100/100")

        overlay = self.twitch.get_overlay_data()
        self.assertEqual(overlay["player_level"]["value"], "10")
        self.assertEqual(overlay["player_health"]["value"], "100/100")

    def test_overlay_timestamp(self):
        """Test overlay includes timestamps."""
        self.twitch.update_overlay("test", "value")
        overlay = self.twitch.get_overlay_data()

        self.assertIn("updated_at", overlay["test"])
        self.assertIsInstance(overlay["test"]["updated_at"], int)


class TestWebhookSystem(unittest.TestCase):
    """Test the central webhook system."""

    def setUp(self):
        """Set up test fixtures."""
        self.webhook_system = WebhookSystem()

    def test_register_custom_webhook(self):
        """Test custom webhook registration."""
        config = self.webhook_system.register_custom_webhook(
            "https://custom.webhook.com/events",
            [WebhookEventType.CUSTOM]
        )

        self.assertIsNotNone(config.webhook_id)
        self.assertEqual(len(self.webhook_system.custom_webhooks), 1)

    def test_trigger_achievement_webhook(self):
        """Test achievement webhook triggering."""
        self.webhook_system.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.ACHIEVEMENT_UNLOCKED]
        )

        triggered = self.webhook_system.trigger_achievement_webhook(
            "player_1",
            "TestPlayer",
            "First Steps",
            "Complete tutorial"
        )

        self.assertGreater(len(triggered), 0)

    def test_trigger_pvp_webhook(self):
        """Test PvP webhook triggering."""
        self.webhook_system.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.PVP_VICTORY]
        )

        triggered = self.webhook_system.trigger_pvp_webhook(
            "player_1",
            "Champion",
            "player_2",
            "Challenger",
            +25
        )

        self.assertGreater(len(triggered), 0)

    def test_trigger_quest_webhook(self):
        """Test quest webhook triggering."""
        self.webhook_system.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.QUEST_COMPLETED]
        )

        triggered = self.webhook_system.trigger_quest_webhook(
            "player_1",
            "Adventurer",
            "Explore the Forest",
            "100 gold + sword"
        )

        self.assertGreater(len(triggered), 0)

    def test_integration_status(self):
        """Test getting integration status."""
        status = self.webhook_system.get_integration_status()

        self.assertIn("discord", status)
        self.assertIn("twitch", status)
        self.assertIn("custom_webhooks", status)

    def test_history_tracking(self):
        """Test integration event history."""
        self.webhook_system.discord.register_webhook(
            "https://discord.com/api/webhooks/test",
            [WebhookEventType.ACHIEVEMENT_UNLOCKED]
        )

        self.webhook_system.trigger_achievement_webhook(
            "player_1",
            "Test",
            "Achievement",
            "Desc"
        )

        history = self.webhook_system.export_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["event"], "achievement_unlock")

    def test_format_embed(self):
        """Test Discord embed formatting."""
        embed = self.webhook_system.discord.format_discord_embed(
            "Test Title",
            "Test Description",
            {"Field 1": "Value 1", "Field 2": "Value 2"}
        )

        self.assertEqual(embed["title"], "Test Title")
        self.assertEqual(embed["description"], "Test Description")
        self.assertEqual(len(embed["fields"]), 2)


if __name__ == "__main__":
    unittest.main()
