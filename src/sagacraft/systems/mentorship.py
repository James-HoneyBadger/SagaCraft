"""Mentor System - experienced players guide newbies for mutual rewards."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class MentorshipStatus(Enum):
    """Mentorship relationship status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MentorshipTier(Enum):
    """Mentor experience tiers."""
    NOVICE_MENTOR = 1
    EXPERIENCED_MENTOR = 2
    EXPERT_MENTOR = 3
    LEGENDARY_MENTOR = 4


@dataclass
class MentorshipMilestone:
    """A milestone in a mentorship relationship."""
    name: str
    description: str
    requirement: str
    xp_reward: int
    gold_reward: int
    completed: bool = False


@dataclass
class MentorshipPair:
    """A mentor-mentee relationship."""
    pair_id: str
    mentor_id: str
    mentee_id: str
    created_date: int  # Unix timestamp
    status: MentorshipStatus
    duration_days: int = 30
    mentee_level_start: int = 1
    mentee_level_current: int = 1
    mentee_level_goal: int = 20
    milestones_completed: List[str] = field(default_factory=list)
    lessons_conducted: int = 0
    quests_completed_together: int = 0
    mentee_playtime_hours: float = 0.0
    mentor_playtime_hours: float = 0.0
    mentor_satisfaction: float = 0.0  # 0-100
    mentee_satisfaction: float = 0.0  # 0-100


@dataclass
class MentorProfile:
    """A player's mentor profile."""
    player_id: str
    mentor_tier: MentorshipTier
    active_mentees: int = 0
    max_mentees: int = 2  # Tier dependent
    total_mentees_trained: int = 0
    total_rewards_earned: int = 0
    average_mentee_satisfaction: float = 0.0
    completion_rate: float = 0.0  # % of successful mentorships


class MentorSystem:
    """Manages mentor-mentee relationships and progression."""

    def __init__(self):
        self.mentorships: Dict[str, MentorshipPair] = {}
        self.mentor_profiles: Dict[str, MentorProfile] = {}
        self.player_mentorships: Dict[str, List[str]] = {}  # player_id -> pair_ids
        self.next_pair_id = 0
        self._init_milestones()

    def _init_milestones(self) -> None:
        """Initialize mentorship milestones."""
        self.milestones = {
            "first_lesson": MentorshipMilestone(
                name="First Lesson",
                description="Conduct first lesson",
                requirement="lessons_conducted >= 1",
                xp_reward=100,
                gold_reward=500,
            ),
            "reach_level_10": MentorshipMilestone(
                name="Student Reaches Level 10",
                description="Mentee reaches level 10",
                requirement="mentee_level >= 10",
                xp_reward=200,
                gold_reward=1000,
            ),
            "reach_level_20": MentorshipMilestone(
                name="Student Reaches Level 20",
                description="Mentee reaches level 20",
                requirement="mentee_level >= 20",
                xp_reward=500,
                gold_reward=2500,
            ),
            "complete_5_quests": MentorshipMilestone(
                name="5 Quests Together",
                description="Complete 5 quests together",
                requirement="quests_completed >= 5",
                xp_reward=300,
                gold_reward=1500,
            ),
            "high_satisfaction": MentorshipMilestone(
                name="Outstanding Mentor",
                description="Mentee gives 90+ satisfaction",
                requirement="mentee_satisfaction >= 90",
                xp_reward=400,
                gold_reward=2000,
            ),
        }

    def create_mentor_profile(self, player_id: str) -> MentorProfile:
        """Create a mentor profile."""
        profile = MentorProfile(player_id=player_id, mentor_tier=MentorshipTier.NOVICE_MENTOR)
        self.mentor_profiles[player_id] = profile
        return profile

    def request_mentor(self, mentee_id: str, mentor_id: str) -> Tuple[bool, str]:
        """Request a mentor for a mentee."""
        if mentor_id not in self.mentor_profiles:
            return False, "Mentor not found"

        mentor_profile = self.mentor_profiles[mentor_id]
        if mentor_profile.active_mentees >= mentor_profile.max_mentees:
            return False, "Mentor is at max capacity"

        # Create mentorship
        pair_id = f"mentorship_{self.next_pair_id}"
        self.next_pair_id += 1

        pair = MentorshipPair(
            pair_id=pair_id,
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            created_date=int(__import__("time").time()),
            status=MentorshipStatus.PENDING,
        )

        self.mentorships[pair_id] = pair

        if mentee_id not in self.player_mentorships:
            self.player_mentorships[mentee_id] = []
        self.player_mentorships[mentee_id].append(pair_id)

        if mentor_id not in self.player_mentorships:
            self.player_mentorships[mentor_id] = []
        self.player_mentorships[mentor_id].append(pair_id)

        return True, f"Mentorship request sent to {mentor_id}"

    def accept_mentorship(self, mentor_id: str, pair_id: str) -> Tuple[bool, str]:
        """Accept a mentorship request."""
        pair = self.mentorships.get(pair_id)
        if not pair or pair.mentor_id != mentor_id:
            return False, "Invalid mentorship"

        pair.status = MentorshipStatus.ACTIVE
        mentor_profile = self.mentor_profiles[mentor_id]
        mentor_profile.active_mentees += 1

        return True, f"Mentorship with {pair.mentee_id} activated"

    def reject_mentorship(self, mentor_id: str, pair_id: str) -> Tuple[bool, str]:
        """Reject a mentorship request."""
        pair = self.mentorships.get(pair_id)
        if not pair or pair.mentor_id != mentor_id:
            return False, "Invalid mentorship"

        pair.status = MentorshipStatus.CANCELLED
        return True, "Mentorship cancelled"

    def record_lesson(self, pair_id: str) -> Tuple[bool, str]:
        """Record that a lesson was conducted."""
        pair = self.mentorships.get(pair_id)
        if not pair or pair.status != MentorshipStatus.ACTIVE:
            return False, "Mentorship not active"

        pair.lessons_conducted += 1
        self._check_milestones(pair_id)

        return True, f"Lesson recorded (Total: {pair.lessons_conducted})"

    def record_quest_completion(self, pair_id: str) -> Tuple[bool, str]:
        """Record a quest completed together."""
        pair = self.mentorships.get(pair_id)
        if not pair or pair.status != MentorshipStatus.ACTIVE:
            return False, "Mentorship not active"

        pair.quests_completed_together += 1
        self._check_milestones(pair_id)

        return True, f"Quest recorded ({pair.quests_completed_together} total)"

    def update_mentee_level(self, pair_id: str, new_level: int) -> None:
        """Update mentee's current level."""
        pair = self.mentorships.get(pair_id)
        if pair:
            pair.mentee_level_current = new_level
            self._check_milestones(pair_id)

    def _check_milestones(self, pair_id: str) -> None:
        """Check and unlock milestones."""
        pair = self.mentorships.get(pair_id)
        if not pair:
            return

        for milestone_id, milestone in self.milestones.items():
            if milestone_id in pair.milestones_completed:
                continue

            # Check if milestone is complete
            if milestone_id == "first_lesson" and pair.lessons_conducted >= 1:
                pair.milestones_completed.append(milestone_id)
            elif milestone_id == "reach_level_10" and pair.mentee_level_current >= 10:
                pair.milestones_completed.append(milestone_id)
            elif milestone_id == "reach_level_20" and pair.mentee_level_current >= 20:
                pair.milestones_completed.append(milestone_id)
            elif milestone_id == "complete_5_quests" and pair.quests_completed_together >= 5:
                pair.milestones_completed.append(milestone_id)
            elif milestone_id == "high_satisfaction" and pair.mentee_satisfaction >= 90:
                pair.milestones_completed.append(milestone_id)

    def rate_mentorship(self, pair_id: str, rater_id: str, satisfaction: float) -> Tuple[bool, str]:
        """Rate mentorship experience."""
        pair = self.mentorships.get(pair_id)
        if not pair:
            return False, "Mentorship not found"

        satisfaction = max(0, min(100, satisfaction))  # Clamp 0-100

        if rater_id == pair.mentor_id:
            pair.mentee_satisfaction = satisfaction
        elif rater_id == pair.mentee_id:
            pair.mentor_satisfaction = satisfaction
        else:
            return False, "Not part of this mentorship"

        return True, f"Rating recorded: {satisfaction}/100"

    def complete_mentorship(self, pair_id: str) -> Tuple[bool, Dict]:
        """Complete a mentorship and award rewards."""
        pair = self.mentorships.get(pair_id)
        if not pair:
            return False, {}

        pair.status = MentorshipStatus.COMPLETED

        # Calculate rewards
        mentor_xp = 500 + (len(pair.milestones_completed) * 100)
        mentee_xp = 300 + (len(pair.milestones_completed) * 75)

        # Update mentor profile
        mentor_profile = self.mentor_profiles[pair.mentor_id]
        mentor_profile.active_mentees -= 1
        mentor_profile.total_mentees_trained += 1
        mentor_profile.total_rewards_earned += mentor_xp

        return True, {
            "mentor_xp": mentor_xp,
            "mentee_xp": mentee_xp,
            "milestones": len(pair.milestones_completed),
        }

    def get_mentor_candidates(self) -> List[Dict]:
        """Get available mentors for a new player."""
        mentors = []
        for player_id, profile in self.mentor_profiles.items():
            if profile.active_mentees < profile.max_mentees:
                mentors.append({
                    "player_id": player_id,
                    "tier": profile.mentor_tier.name,
                    "trainees": profile.total_mentees_trained,
                    "satisfaction": profile.average_mentee_satisfaction,
                })
        return mentors

    def get_mentorship_details(self, pair_id: str) -> Optional[Dict]:
        """Get detailed information about a mentorship."""
        pair = self.mentorships.get(pair_id)
        if not pair:
            return None

        return {
            "mentor": pair.mentor_id,
            "mentee": pair.mentee_id,
            "status": pair.status.value,
            "level_progress": f"{pair.mentee_level_current}/{pair.mentee_level_goal}",
            "lessons": pair.lessons_conducted,
            "quests": pair.quests_completed_together,
            "milestones": len(pair.milestones_completed),
        }
