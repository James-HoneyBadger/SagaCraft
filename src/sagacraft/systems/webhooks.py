"""Discord & Webhook Integration System - connect SagaCraft to external platforms."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Callable
import json
import time


class WebhookEventType(Enum):
    """Types of events that trigger webhooks."""
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    QUEST_COMPLETED = "quest_completed"
    PLAYER_LEVELED_UP = "player_leveled_up"
    BOSS_DEFEATED = "boss_defeated"
    PVP_VICTORY = "pvp_victory"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    LEADERBOARD_REACHED = "leaderboard_reached"
    ADVENTURE_COMPLETED = "adventure_completed"
    CUSTOM = "custom"


@dataclass
class WebhookConfig:
    """Configuration for a webhook."""
    webhook_id: str
    webhook_url: str  # e.g., https://discord.com/api/webhooks/...
    event_types: List[WebhookEventType] = field(default_factory=list)
    active: bool = True
    created_time: int = 0
    last_triggered: Optional[int] = None


@dataclass
class DiscordCommand:
    """A Discord command that interacts with SagaCraft."""
    command_name: str
    description: str
    handler: Optional[Callable] = None  # Function to handle the command


@dataclass
class WebhookPayload:
    """Payload sent to a webhook."""
    event_type: WebhookEventType
    timestamp: int
    data: Dict = field(default_factory=dict)
    player_id: Optional[str] = None


@dataclass
class IntegrationConfig:
    """Configuration for external integrations."""
    platform: str  # "discord", "twitch", "custom"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    connected: bool = False


class DiscordIntegration:
    """Discord integration for SagaCraft."""

    def __init__(self):
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.commands: Dict[str, DiscordCommand] = {}
        self.integration_config: Optional[IntegrationConfig] = None
        self.next_webhook_id = 0

        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register default Discord commands."""
        commands = [
            DiscordCommand(
                "sagacraft-check",
                "Check your SagaCraft character status"
            ),
            DiscordCommand(
                "sagacraft-stats",
                "View your gameplay statistics"
            ),
            DiscordCommand(
                "sagacraft-leaderboard",
                "View the SagaCraft leaderboard"
            ),
            DiscordCommand(
                "sagacraft-quests",
                "View available quests"
            ),
        ]

        for cmd in commands:
            self.commands[cmd.command_name] = cmd

    def register_webhook(
        self,
        webhook_url: str,
        event_types: List[WebhookEventType]
    ) -> WebhookConfig:
        """Register a new webhook."""
        webhook_id = f"webhook_{self.next_webhook_id}"
        self.next_webhook_id += 1

        config = WebhookConfig(
            webhook_id=webhook_id,
            webhook_url=webhook_url,
            event_types=event_types,
            created_time=int(time.time())
        )

        self.webhooks[webhook_id] = config
        return config

    def unregister_webhook(self, webhook_id: str) -> Tuple[bool, str]:
        """Unregister a webhook."""
        if webhook_id not in self.webhooks:
            return False, "Webhook not found"

        del self.webhooks[webhook_id]
        return True, f"Webhook {webhook_id} removed"

    def trigger_event(
        self,
        event_type: WebhookEventType,
        data: Dict,
        player_id: Optional[str] = None
    ) -> List[str]:
        """Trigger webhooks for an event."""
        triggered = []
        payload = WebhookPayload(
            event_type=event_type,
            timestamp=int(time.time()),
            data=data,
            player_id=player_id
        )

        for webhook_id, config in self.webhooks.items():
            if not config.active:
                continue

            if event_type in config.event_types:
                success = self._send_webhook(config, payload)
                if success:
                    config.last_triggered = int(time.time())
                    triggered.append(webhook_id)

        return triggered

    def _send_webhook(self, config: WebhookConfig, payload: WebhookPayload) -> bool:
        """Send webhook payload (simulated - in production would use requests)."""
        # In a real implementation, this would use the requests library
        # to send an actual HTTP POST request to the webhook URL
        # For now, we'll simulate success
        return True

    def format_discord_embed(
        self,
        title: str,
        description: str,
        fields: Optional[Dict[str, str]] = None,
        color: int = 0x7289DA  # Discord blurple
    ) -> Dict:
        """Format a Discord embed message."""
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": time.time(),
            "fields": []
        }

        if fields:
            for field_name, field_value in fields.items():
                embed["fields"].append({
                    "name": field_name,
                    "value": field_value,
                    "inline": True
                })

        return embed

    def create_achievement_embed(
        self,
        player_name: str,
        achievement_name: str,
        achievement_desc: str
    ) -> Dict:
        """Create a Discord embed for achievement unlock."""
        return self.format_discord_embed(
            title="🏆 Achievement Unlocked!",
            description=f"{player_name} earned a new achievement!",
            fields={
                "Achievement": achievement_name,
                "Description": achievement_desc,
            },
            color=0xFFD700  # Gold
        )

    def create_quest_embed(
        self,
        player_name: str,
        quest_name: str,
        reward: str
    ) -> Dict:
        """Create a Discord embed for quest completion."""
        return self.format_discord_embed(
            title="✅ Quest Completed!",
            description=f"{player_name} completed a quest!",
            fields={
                "Quest": quest_name,
                "Reward": reward,
            },
            color=0x43B581  # Green
        )

    def create_pvp_embed(
        self,
        winner_name: str,
        loser_name: str,
        rating_change: int
    ) -> Dict:
        """Create a Discord embed for PvP victory."""
        return self.format_discord_embed(
            title="⚔️ PvP Victory!",
            description=f"{winner_name} defeated {loser_name}!",
            fields={
                "Winner": winner_name,
                "Loser": loser_name,
                "Rating Change": f"+{rating_change}" if rating_change > 0 else str(rating_change),
            },
            color=0xFF0000  # Red
        )


class TwitchIntegration:
    """Twitch integration for SagaCraft."""

    def __init__(self):
        self.channel_id: Optional[str] = None
        self.overlay_data: Dict = {}
        self.connected = False

    def connect(self, channel_name: str) -> Tuple[bool, str]:
        """Connect to a Twitch channel."""
        self.channel_id = channel_name
        self.connected = True
        return True, f"Connected to {channel_name}"

    def update_overlay(self, key: str, value: str) -> None:
        """Update overlay data for Twitch extension."""
        self.overlay_data[key] = {
            "value": value,
            "updated_at": int(time.time())
        }

    def get_overlay_data(self) -> Dict:
        """Get current overlay data."""
        return self.overlay_data.copy()


class WebhookSystem:
    """Central system for managing all webhook integrations."""

    def __init__(self):
        self.discord = DiscordIntegration()
        self.twitch = TwitchIntegration()
        self.custom_webhooks: List[WebhookConfig] = []
        self.integration_history: List[Dict] = []

    def register_custom_webhook(
        self,
        webhook_url: str,
        event_types: List[WebhookEventType]
    ) -> WebhookConfig:
        """Register a custom webhook (non-Discord, non-Twitch)."""
        config = WebhookConfig(
            webhook_id=f"custom_webhook_{len(self.custom_webhooks)}",
            webhook_url=webhook_url,
            event_types=event_types,
            created_time=int(time.time())
        )
        self.custom_webhooks.append(config)
        return config

    def trigger_achievement_webhook(
        self,
        player_id: str,
        player_name: str,
        achievement_name: str,
        achievement_desc: str
    ) -> List[str]:
        """Trigger achievement webhooks."""
        triggered = []

        # Discord webhook
        embed = self.discord.create_achievement_embed(
            player_name,
            achievement_name,
            achievement_desc
        )
        discord_triggered = self.discord.trigger_event(
            WebhookEventType.ACHIEVEMENT_UNLOCKED,
            {
                "achievement_name": achievement_name,
                "embed": embed
            },
            player_id
        )
        triggered.extend(discord_triggered)

        # Custom webhooks
        for webhook in self.custom_webhooks:
            if WebhookEventType.ACHIEVEMENT_UNLOCKED in webhook.event_types:
                triggered.append(webhook.webhook_id)

        self.integration_history.append({
            "event": "achievement_unlock",
            "player_id": player_id,
            "timestamp": int(time.time())
        })

        return triggered

    def trigger_pvp_webhook(
        self,
        winner_id: str,
        winner_name: str,
        loser_id: str,
        loser_name: str,
        rating_change: int
    ) -> List[str]:
        """Trigger PvP victory webhooks."""
        triggered = []

        # Discord webhook
        embed = self.discord.create_pvp_embed(winner_name, loser_name, rating_change)
        discord_triggered = self.discord.trigger_event(
            WebhookEventType.PVP_VICTORY,
            {
                "winner_name": winner_name,
                "loser_name": loser_name,
                "embed": embed
            },
            winner_id
        )
        triggered.extend(discord_triggered)

        self.integration_history.append({
            "event": "pvp_victory",
            "winner_id": winner_id,
            "loser_id": loser_id,
            "timestamp": int(time.time())
        })

        return triggered

    def trigger_quest_webhook(
        self,
        player_id: str,
        player_name: str,
        quest_name: str,
        reward: str
    ) -> List[str]:
        """Trigger quest completion webhooks."""
        triggered = []

        # Discord webhook
        embed = self.discord.create_quest_embed(player_name, quest_name, reward)
        discord_triggered = self.discord.trigger_event(
            WebhookEventType.QUEST_COMPLETED,
            {
                "quest_name": quest_name,
                "reward": reward,
                "embed": embed
            },
            player_id
        )
        triggered.extend(discord_triggered)

        self.integration_history.append({
            "event": "quest_completed",
            "player_id": player_id,
            "timestamp": int(time.time())
        })

        return triggered

    def get_integration_status(self) -> Dict:
        """Get status of all integrations."""
        return {
            "discord": {
                "connected": True,
                "webhooks_registered": len(self.discord.webhooks),
                "commands_available": len(self.discord.commands)
            },
            "twitch": {
                "connected": self.twitch.connected,
                "channel": self.twitch.channel_id
            },
            "custom_webhooks": len(self.custom_webhooks),
            "total_events_triggered": len(self.integration_history)
        }

    def export_history(self) -> List[Dict]:
        """Export integration history."""
        return self.integration_history.copy()
