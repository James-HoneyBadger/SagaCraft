"""Guild/Clan System - create groups with shared treasury, guild halls, and challenges."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class GuildRank(Enum):
    """Guild member ranks."""
    LEADER = "leader"
    OFFICER = "officer"
    MEMBER = "member"
    RECRUIT = "recruit"


class GuildTier(Enum):
    """Guild progression tiers."""
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4
    DIAMOND = 5


@dataclass
class GuildMember:
    """A member in a guild."""
    player_id: str
    rank: GuildRank
    join_date: int  # Unix timestamp
    contribution_points: int = 0


@dataclass
class GuildChallenge:
    """A weekly guild challenge."""
    id: str
    name: str
    description: str
    objective: str
    duration_days: int = 7
    reward_currency: int = 0
    reward_items: List[str] = field(default_factory=list)
    difficulty: str = "normal"  # easy, normal, hard, extreme
    participation_count: int = 0
    completion_count: int = 0


@dataclass
class Guild:
    """A guild/clan."""
    id: str
    name: str
    leader_id: str
    description: str
    created_date: int  # Unix timestamp
    tier: GuildTier = GuildTier.BRONZE
    level: int = 1
    members: Dict[str, GuildMember] = field(default_factory=dict)
    treasury: int = 0  # Guild currency
    perks: Set[str] = field(default_factory=set)  # Unlocked guild perks
    hall_level: int = 1  # Guild hall progression (1-5)
    active_challenges: List[GuildChallenge] = field(default_factory=list)
    members_online: int = 0
    max_members: int = 50


class GuildSystem:
    """Manages guilds and guild interactions."""

    def __init__(self):
        self.guilds: Dict[str, Guild] = {}
        self.player_guilds: Dict[str, str] = {}  # player_id -> guild_id
        self.guild_invitations: Dict[str, List[str]] = {}  # guild_id -> [player_ids]

    def create_guild(
        self, guild_id: str, name: str, leader_id: str, description: str, created_date: int
    ) -> Guild:
        """Create a new guild."""
        guild = Guild(
            id=guild_id,
            name=name,
            leader_id=leader_id,
            description=description,
            created_date=created_date,
        )

        # Add leader as member
        guild.members[leader_id] = GuildMember(
            player_id=leader_id, rank=GuildRank.LEADER, join_date=created_date
        )

        self.guilds[guild_id] = guild
        self.player_guilds[leader_id] = guild_id
        return guild

    def get_guild(self, guild_id: str) -> Optional[Guild]:
        """Get a guild by ID."""
        return self.guilds.get(guild_id)

    def get_player_guild(self, player_id: str) -> Optional[Guild]:
        """Get the guild a player belongs to."""
        guild_id = self.player_guilds.get(player_id)
        if guild_id:
            return self.guilds.get(guild_id)
        return None

    def invite_player(self, guild_id: str, player_id: str) -> Tuple[bool, str]:
        """Invite a player to join the guild."""
        guild = self.get_guild(guild_id)
        if not guild:
            return False, "Guild not found"

        if len(guild.members) >= guild.max_members:
            return False, "Guild is full"

        if player_id in guild.members:
            return False, "Player already in guild"

        # Add to invitations
        if guild_id not in self.guild_invitations:
            self.guild_invitations[guild_id] = []
        if player_id not in self.guild_invitations[guild_id]:
            self.guild_invitations[guild_id].append(player_id)

        return True, f"Invited {player_id} to {guild.name}"

    def join_guild(self, guild_id: str, player_id: str) -> Tuple[bool, str]:
        """Accept guild invitation and join."""
        guild = self.get_guild(guild_id)
        if not guild:
            return False, "Guild not found"

        if player_id not in self.guild_invitations.get(guild_id, []):
            return False, "No invitation to join this guild"

        # Join guild
        guild.members[player_id] = GuildMember(
            player_id=player_id, rank=GuildRank.RECRUIT, join_date=int(__import__("time").time())
        )
        self.player_guilds[player_id] = guild_id

        # Remove invitation
        self.guild_invitations[guild_id].remove(player_id)

        return True, f"Joined {guild.name}"

    def leave_guild(self, guild_id: str, player_id: str) -> Tuple[bool, str]:
        """Leave a guild."""
        guild = self.get_guild(guild_id)
        if not guild or player_id not in guild.members:
            return False, "Not in guild"

        if guild.members[player_id].rank == GuildRank.LEADER:
            return False, "Leader cannot leave. Transfer leadership first."

        del guild.members[player_id]
        if player_id in self.player_guilds:
            del self.player_guilds[player_id]

        return True, f"Left {guild.name}"

    def contribute_to_treasury(self, guild_id: str, player_id: str, amount: int) -> Tuple[bool, str]:
        """Contribute currency to guild treasury."""
        guild = self.get_guild(guild_id)
        if not guild or player_id not in guild.members:
            return False, "Not in guild"

        guild.treasury += amount
        member = guild.members[player_id]
        member.contribution_points += amount

        return True, f"Contributed {amount} to guild treasury"

    def add_guild_challenge(self, guild_id: str, challenge: GuildChallenge) -> Tuple[bool, str]:
        """Add a new guild challenge."""
        guild = self.get_guild(guild_id)
        if not guild:
            return False, "Guild not found"

        guild.active_challenges.append(challenge)
        return True, f"Challenge '{challenge.name}' started"

    def complete_guild_challenge(self, guild_id: str, challenge_id: str) -> Tuple[bool, str]:
        """Mark a guild challenge as completed."""
        guild = self.get_guild(guild_id)
        if not guild:
            return False, "Guild not found"

        for challenge in guild.active_challenges:
            if challenge.id == challenge_id:
                challenge.completion_count += 1
                guild.treasury += challenge.reward_currency
                return True, f"Challenge completed! Guild earned {challenge.reward_currency} currency"

        return False, "Challenge not found"

    def upgrade_guild_hall(self, guild_id: str) -> Tuple[bool, str]:
        """Upgrade the guild hall."""
        guild = self.get_guild(guild_id)
        if not guild:
            return False, "Guild not found"

        if guild.hall_level >= 5:
            return False, "Guild hall already at max level"

        # Cost increases with level
        upgrade_cost = guild.hall_level * 5000
        if guild.treasury < upgrade_cost:
            return False, f"Need {upgrade_cost} currency (have {guild.treasury})"

        guild.treasury -= upgrade_cost
        guild.hall_level += 1

        return True, f"Guild hall upgraded to level {guild.hall_level}"

    def promote_member(self, guild_id: str, player_id: str, rank: GuildRank) -> Tuple[bool, str]:
        """Promote a guild member."""
        guild = self.get_guild(guild_id)
        if not guild or player_id not in guild.members:
            return False, "Member not in guild"

        guild.members[player_id].rank = rank
        return True, f"Promoted {player_id} to {rank.value}"

    def get_guild_members(self, guild_id: str) -> List[Dict]:
        """Get all members of a guild."""
        guild = self.get_guild(guild_id)
        if not guild:
            return []

        members = []
        for player_id, member in guild.members.items():
            members.append({
                "player_id": player_id,
                "rank": member.rank.value,
                "contribution": member.contribution_points,
            })
        return members

    def get_guild_info(self, guild_id: str) -> Optional[Dict]:
        """Get detailed guild information."""
        guild = self.get_guild(guild_id)
        if not guild:
            return None

        return {
            "name": guild.name,
            "leader": guild.leader_id,
            "level": guild.level,
            "tier": guild.tier.name,
            "members": len(guild.members),
            "max_members": guild.max_members,
            "treasury": guild.treasury,
            "hall_level": guild.hall_level,
            "description": guild.description,
        }


from typing import Tuple
