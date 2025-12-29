"""Tests for the Advanced Storytelling system."""

import unittest
from sagacraft.systems.storytelling import (
    StoryEngine,
    StoryChapter,
    StoryEnding,
    Flashback,
    Timeline,
    NarrativeChoice,
    NarrativeType,
)


class TestStoryEngine(unittest.TestCase):
    """Test the story engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = StoryEngine()
        self.player_id = "test_player"

    def test_create_player_progress(self):
        """Test player progress initialization."""
        progress = self.engine.get_player_progress(self.player_id)

        self.assertEqual(progress.player_id, self.player_id)
        self.assertEqual(progress.current_timeline, "canon")

    def test_register_chapter(self):
        """Test chapter registration."""
        chapter = StoryChapter(
            chapter_id="ch1",
            title="The Beginning",
            description="Where it all starts",
            narrative_type=NarrativeType.CHAPTER,
            content="You awaken in a mysterious forest..."
        )

        self.engine.register_chapter(chapter)
        self.assertIn("ch1", self.engine.chapters)

    def test_advance_to_chapter(self):
        """Test advancing to a chapter."""
        chapter = StoryChapter(
            chapter_id="ch1",
            title="Start",
            description="Beginning",
            narrative_type=NarrativeType.CHAPTER,
            content="You start here"
        )
        self.engine.register_chapter(chapter)

        success, msg = self.engine.advance_to_chapter(self.player_id, "ch1")

        self.assertTrue(success)
        progress = self.engine.get_player_progress(self.player_id)
        self.assertEqual(progress.current_chapter, "ch1")

    def test_chapter_requirements(self):
        """Test chapter requirements checking."""
        chapter = StoryChapter(
            chapter_id="ch2",
            title="Later",
            description="Requires completion",
            narrative_type=NarrativeType.CHAPTER,
            content="You're back",
            requirements=["flag_started"]
        )
        self.engine.register_chapter(chapter)

        # Without requirement
        success, msg = self.engine.advance_to_chapter(self.player_id, "ch2")
        self.assertFalse(success)

        # With requirement met
        progress = self.engine.get_player_progress(self.player_id)
        progress.story_variables["flag_started"] = "true"
        success, msg = self.engine.advance_to_chapter(self.player_id, "ch2")
        self.assertTrue(success)

    def test_story_choices(self):
        """Test story choice system."""
        choice1 = NarrativeChoice(
            choice_id="choice_a",
            text="Go left",
            leads_to_chapter="ch_left"
        )
        choice2 = NarrativeChoice(
            choice_id="choice_b",
            text="Go right",
            leads_to_chapter="ch_right"
        )

        chapter = StoryChapter(
            chapter_id="ch_fork",
            title="Fork",
            description="Choose your path",
            narrative_type=NarrativeType.BRANCH,
            content="Two paths appear",
            choices=[choice1, choice2]
        )

        self.engine.register_chapter(chapter)
        self.engine.advance_to_chapter(self.player_id, "ch_fork")

        available = self.engine.get_available_choices(self.player_id)
        self.assertEqual(len(available), 2)

    def test_make_choice(self):
        """Test making a story choice."""
        # Create two branches
        left_chapter = StoryChapter(
            chapter_id="ch_left",
            title="Left Path",
            description="You went left",
            narrative_type=NarrativeType.CHAPTER,
            content="The left path was dark..."
        )

        choice = NarrativeChoice(
            choice_id="go_left",
            text="Go left",
            leads_to_chapter="ch_left"
        )

        fork_chapter = StoryChapter(
            chapter_id="ch_fork",
            title="Fork",
            description="Choose",
            narrative_type=NarrativeType.BRANCH,
            content="Two paths",
            choices=[choice]
        )

        self.engine.register_chapter(fork_chapter)
        self.engine.register_chapter(left_chapter)
        self.engine.advance_to_chapter(self.player_id, "ch_fork")

        success, msg = self.engine.make_choice(self.player_id, "go_left")

        self.assertTrue(success)
        progress = self.engine.get_player_progress(self.player_id)
        self.assertEqual(progress.current_chapter, "ch_left")

    def test_timeline_divergence(self):
        """Test timeline branching."""
        choice = NarrativeChoice(
            choice_id="split",
            text="Make major choice",
            leads_to_chapter="ch2",
            affects_timeline=True
        )

        chapter = StoryChapter(
            chapter_id="ch1",
            title="Start",
            description="Start",
            narrative_type=NarrativeType.CHAPTER,
            content="Start",
            choices=[choice]
        )

        ch2 = StoryChapter(
            chapter_id="ch2",
            title="After",
            description="After",
            narrative_type=NarrativeType.CHAPTER,
            content="After"
        )

        self.engine.register_chapter(chapter)
        self.engine.register_chapter(ch2)
        self.engine.advance_to_chapter(self.player_id, "ch1")

        progress = self.engine.get_player_progress(self.player_id)
        self.assertEqual(progress.current_timeline, "canon")

        self.engine.make_choice(self.player_id, "split")

        progress = self.engine.get_player_progress(self.player_id)
        self.assertNotEqual(progress.current_timeline, "canon")

    def test_register_flashback(self):
        """Test flashback registration."""
        flashback = Flashback(
            flashback_id="fb1",
            title="The Past",
            description="What happened before",
            related_chapter="ch1",
            content="Long ago...",
            trigger_conditions=[]
        )

        self.engine.register_flashback(flashback)
        self.assertIn("fb1", self.engine.flashbacks)

    def test_flashback_unlock(self):
        """Test flashback unlocking."""
        flashback = Flashback(
            flashback_id="fb1",
            title="Memory",
            description="A memory unlocks",
            related_chapter="ch1",
            content="You remember...",
            trigger_conditions=["saw_clue"]
        )

        self.engine.register_flashback(flashback)

        # Initially locked
        progress = self.engine.get_player_progress(self.player_id)
        self.assertNotIn("fb1", progress.unlocked_flashbacks)

        # Unlock by setting trigger
        progress.story_variables["saw_clue"] = "true"
        self.engine._check_flashback_unlocks(self.player_id)
        self.assertIn("fb1", progress.unlocked_flashbacks)

    def test_play_flashback(self):
        """Test playing a flashback."""
        flashback = Flashback(
            flashback_id="fb1",
            title="Memory",
            description="A memory",
            related_chapter="ch1",
            content="I remember now..."
        )

        self.engine.register_flashback(flashback)
        progress = self.engine.get_player_progress(self.player_id)
        progress.unlocked_flashbacks.add("fb1")

        success, content = self.engine.play_flashback(self.player_id, "fb1")

        self.assertTrue(success)
        self.assertIn("I remember now", content)

    def test_register_ending(self):
        """Test ending registration."""
        ending = StoryEnding(
            ending_id="end_good",
            name="Good Ending",
            description="Happy conclusion",
            content="You saved the day",
            mood="happy"
        )

        self.engine.register_ending(ending)
        self.assertIn("end_good", self.engine.endings)

    def test_check_ending_conditions(self):
        """Test ending condition checking."""
        ending = StoryEnding(
            ending_id="end_hero",
            name="Hero's Ending",
            description="Heroic conclusion",
            requirements=["defeated_boss", "saved_kingdom"],
            content="You became a hero"
        )

        self.engine.register_ending(ending)

        # No ending without requirements
        result = self.engine.check_ending_conditions(self.player_id)
        self.assertIsNone(result)

        # Ending unlocks with requirements
        progress = self.engine.get_player_progress(self.player_id)
        progress.story_variables["defeated_boss"] = "true"
        progress.story_variables["saved_kingdom"] = "true"

        result = self.engine.check_ending_conditions(self.player_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.ending_id, "end_hero")

    def test_trigger_ending(self):
        """Test triggering story ending."""
        ending = StoryEnding(
            ending_id="end_victory",
            name="Victory",
            description="You win",
            content="The End",
            epilogue="And they lived happily..."
        )

        self.engine.register_ending(ending)

        # Set requirements
        progress = self.engine.get_player_progress(self.player_id)
        # No requirements, should work

        success, text = self.engine.trigger_ending(self.player_id, "end_victory")

        self.assertTrue(success)
        self.assertIn("The End", text)
        self.assertIn("lived happily", text)

    def test_timeline_summary(self):
        """Test timeline summary generation."""
        summary = self.engine.get_timeline_summary(self.player_id)

        self.assertIn("current_timeline", summary)
        self.assertIn("chapters_completed", summary)
        self.assertIn("timelines_explored", summary)

    def test_story_map(self):
        """Test story map creation."""
        story_map = self.engine.create_story_map(self.player_id)

        self.assertIn("timelines", story_map)
        self.assertIn("branching_points", story_map)


if __name__ == "__main__":
    unittest.main()
