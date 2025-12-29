"""Advanced Storytelling System - branching timelines, flashbacks, and narrative choices."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import json


class NarrativeType(Enum):
    """Types of narrative content."""
    CHAPTER = "chapter"
    FLASHBACK = "flashback"
    BRANCH = "branch"
    MERGE_POINT = "merge_point"
    CLIMAX = "climax"
    ENDING = "ending"


@dataclass
class NarrativeChoice:
    """A story choice for the player."""
    choice_id: str
    text: str
    leads_to_chapter: str
    requires_conditions: List[str] = field(default_factory=list)
    hidden: bool = False  # Hidden from player initially
    affects_timeline: bool = False
    cosmetic_only: bool = False  # Doesn't affect story


@dataclass
class StoryVariable:
    """A narrative variable tracking story state."""
    var_name: str
    value: str
    affects_dialogue: bool = True
    affects_choices: bool = True
    visible_to_player: bool = True
    group: str = "story"  # "story", "character", "world"


@dataclass
class Timeline:
    """A branching story timeline."""
    timeline_id: str
    name: str
    description: str
    divergence_chapter: str  # Where timeline split from original
    original_timeline: Optional[str] = None  # Parent timeline
    chapters: List[str] = field(default_factory=list)
    ending_id: Optional[str] = None
    deviation_level: int = 0  # How far from canon (0=canon, 5=completely different)
    merge_back_at: Optional[str] = None  # Chapter where timeline rejoins canon


@dataclass
class StoryChapter:
    """A chapter in the story."""
    chapter_id: str
    title: str
    description: str
    narrative_type: NarrativeType
    content: str
    choices: List[NarrativeChoice] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)  # Story flags needed
    sets_variables: Dict[str, str] = field(default_factory=dict)
    next_chapter_default: Optional[str] = None
    is_checkpoint: bool = False  # Can save here
    can_replay: bool = True
    previous_chapters: List[str] = field(default_factory=list)


@dataclass
class Flashback:
    """A flashback sequence revealing past events."""
    flashback_id: str
    title: str
    description: str
    related_chapter: str
    timeline_reference: Optional[str] = None
    content: str = ""
    reveals_character_info: bool = True
    reveals_world_lore: bool = False
    mandatory: bool = False
    trigger_conditions: List[str] = field(default_factory=list)


@dataclass
class StoryEnding:
    """A story ending."""
    ending_id: str
    name: str
    description: str
    requirements: List[str] = field(default_factory=list)  # Story flags needed
    content: str = ""
    epilogue: str = ""
    is_canonical: bool = False
    mood: str = "neutral"  # "happy", "sad", "bittersweet", "tragic", "heroic"
    unlocks_ng_plus: bool = False


@dataclass
class PlayerProgress:
    """Player's story progress across timelines."""
    player_id: str
    current_timeline: str = "canon"
    current_chapter: str = ""
    completed_chapters: List[str] = field(default_factory=list)
    completed_timelines: List[str] = field(default_factory=list)
    completed_endings: List[str] = field(default_factory=list)
    story_variables: Dict[str, str] = field(default_factory=dict)
    unlocked_flashbacks: Set[str] = field(default_factory=set)
    branching_points: Dict[str, str] = field(default_factory=dict)  # chapter_id -> choice_taken
    timeline_history: List[str] = field(default_factory=list)


class StoryEngine:
    """Advanced storytelling engine for branching narratives."""

    def __init__(self):
        self.chapters: Dict[str, StoryChapter] = {}
        self.timelines: Dict[str, Timeline] = {}
        self.flashbacks: Dict[str, Flashback] = {}
        self.endings: Dict[str, StoryEnding] = {}
        self.player_progress: Dict[str, PlayerProgress] = {}

    def register_chapter(self, chapter: StoryChapter) -> None:
        """Register a story chapter."""
        self.chapters[chapter.chapter_id] = chapter

    def register_timeline(self, timeline: Timeline) -> None:
        """Register a branching timeline."""
        self.timelines[timeline.timeline_id] = timeline

    def register_flashback(self, flashback: Flashback) -> None:
        """Register a flashback sequence."""
        self.flashbacks[flashback.flashback_id] = flashback

    def register_ending(self, ending: StoryEnding) -> None:
        """Register a story ending."""
        self.endings[ending.ending_id] = ending

    def get_player_progress(self, player_id: str) -> PlayerProgress:
        """Get or create player progress."""
        if player_id not in self.player_progress:
            self.player_progress[player_id] = PlayerProgress(player_id=player_id)
        return self.player_progress[player_id]

    def get_current_chapter(self, player_id: str) -> Optional[StoryChapter]:
        """Get player's current chapter."""
        progress = self.get_player_progress(player_id)
        if progress.current_chapter:
            return self.chapters.get(progress.current_chapter)
        return None

    def get_available_choices(self, player_id: str) -> List[NarrativeChoice]:
        """Get available story choices for player."""
        chapter = self.get_current_chapter(player_id)
        if not chapter:
            return []

        progress = self.get_player_progress(player_id)
        available = []

        for choice in chapter.choices:
            # Check if choice requirements are met
            if self._check_requirements(progress, choice.requires_conditions):
                if not choice.hidden:
                    available.append(choice)

        return available

    def make_choice(self, player_id: str, choice_id: str) -> Tuple[bool, str]:
        """Player makes a story choice."""
        chapter = self.get_current_chapter(player_id)
        if not chapter:
            return False, "No active chapter"

        # Find the choice
        choice = None
        for c in chapter.choices:
            if c.choice_id == choice_id:
                choice = c
                break

        if not choice:
            return False, "Choice not found"

        progress = self.get_player_progress(player_id)

        # Record the choice
        progress.branching_points[chapter.chapter_id] = choice_id

        # Handle timeline divergence
        if choice.affects_timeline:
            self._handle_timeline_divergence(player_id, chapter.chapter_id)

        # Apply story variable changes
        if choice.requires_conditions:
            for condition in choice.requires_conditions:
                progress.story_variables[condition] = "true"

        # Move to next chapter
        next_chapter = choice.leads_to_chapter
        return self.advance_to_chapter(player_id, next_chapter)

    def _handle_timeline_divergence(self, player_id: str, from_chapter: str) -> None:
        """Create new timeline if choice diverges from canon."""
        progress = self.get_player_progress(player_id)
        if progress.current_timeline == "canon":
            # Create new timeline
            timeline_id = f"alt_timeline_{len(progress.timeline_history)}"
            new_timeline = Timeline(
                timeline_id=timeline_id,
                name=f"Alternative Timeline {len(progress.timeline_history)}",
                description="An alternate path through the story",
                divergence_chapter=from_chapter,
                original_timeline="canon",
                deviation_level=1
            )
            self.timelines[timeline_id] = new_timeline
            progress.current_timeline = timeline_id
            progress.timeline_history.append(timeline_id)

    def advance_to_chapter(self, player_id: str, chapter_id: str) -> Tuple[bool, str]:
        """Advance player to next chapter."""
        chapter = self.chapters.get(chapter_id)
        if not chapter:
            return False, "Chapter not found"

        progress = self.get_player_progress(player_id)

        # Check requirements
        if not self._check_requirements(progress, chapter.requirements):
            return False, "Chapter requirements not met"

        progress.current_chapter = chapter_id
        progress.completed_chapters.append(chapter_id)

        # Apply variable changes
        for var_name, value in chapter.sets_variables.items():
            progress.story_variables[var_name] = value

        # Check for unlocked flashbacks
        self._check_flashback_unlocks(player_id)

        return True, f"Advanced to chapter: {chapter.title}"

    def _check_flashback_unlocks(self, player_id: str) -> None:
        """Check which flashbacks unlock at current chapter."""
        progress = self.get_player_progress(player_id)

        for flashback_id, flashback in self.flashbacks.items():
            if flashback_id in progress.unlocked_flashbacks:
                continue

            # Check if flashback conditions are met
            if self._check_requirements(progress, flashback.trigger_conditions):
                progress.unlocked_flashbacks.add(flashback_id)

    def play_flashback(self, player_id: str, flashback_id: str) -> Tuple[bool, str]:
        """Play a flashback sequence."""
        flashback = self.flashbacks.get(flashback_id)
        if not flashback:
            return False, "Flashback not found"

        progress = self.get_player_progress(player_id)
        if flashback_id not in progress.unlocked_flashbacks:
            return False, "Flashback not yet unlocked"

        return True, f"Flashback: {flashback.title}\n{flashback.content}"

    def check_ending_conditions(self, player_id: str) -> Optional[StoryEnding]:
        """Check if player has met conditions for any ending."""
        progress = self.get_player_progress(player_id)

        for ending_id, ending in self.endings.items():
            if self._check_requirements(progress, ending.requirements):
                return ending

        return None

    def trigger_ending(self, player_id: str, ending_id: str) -> Tuple[bool, str]:
        """Trigger a story ending."""
        ending = self.endings.get(ending_id)
        if not ending:
            return False, "Ending not found"

        progress = self.get_player_progress(player_id)

        if not self._check_requirements(progress, ending.requirements):
            return False, "Ending requirements not met"

        progress.completed_endings.append(ending_id)
        progress.current_timeline = "complete"

        return True, f"Ending: {ending.name}\n{ending.content}\n\nEpilogue:\n{ending.epilogue}"

    def _check_requirements(self, progress: PlayerProgress, requirements: List[str]) -> bool:
        """Check if all story requirements are met."""
        for req in requirements:
            if progress.story_variables.get(req) != "true":
                return False
        return True

    def get_timeline_summary(self, player_id: str) -> Dict:
        """Get summary of player's timeline progress."""
        progress = self.get_player_progress(player_id)

        return {
            "current_timeline": progress.current_timeline,
            "current_chapter": progress.current_chapter,
            "chapters_completed": len(progress.completed_chapters),
            "timelines_explored": len(progress.timeline_history),
            "endings_reached": len(progress.completed_endings),
            "flashbacks_unlocked": len(progress.unlocked_flashbacks),
            "story_variables": progress.story_variables
        }

    def create_story_map(self, player_id: str) -> Dict:
        """Create a visual map of story branching for player."""
        progress = self.get_player_progress(player_id)

        story_map = {
            "timelines": [],
            "branching_points": []
        }

        # Add timelines
        for timeline_id in ["canon"] + progress.timeline_history:
            timeline = self.timelines.get(timeline_id)
            if timeline:
                story_map["timelines"].append({
                    "id": timeline_id,
                    "name": timeline.name,
                    "deviation": timeline.deviation_level
                })

        # Add branching points
        for chapter_id, choice_id in progress.branching_points.items():
            story_map["branching_points"].append({
                "chapter": chapter_id,
                "choice": choice_id
            })

        return story_map
