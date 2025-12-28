"""
Phase X: Polish, Performance & Launch - Test Suite

Tests for multiplayer, adventure sharing, community hub, and performance monitoring.
30+ tests covering all final phase features.

Tests:
    Multiplayer Sessions
    Adventure Sharing & Community
    Replay Recording
    Performance Monitoring
    Content Filtering
    UI Themes
"""

import sys
sys.path.insert(0, '/home/james/SagaCraft/src')

from sagacraft.systems.multiplayer import (
    ReplayRecorder, ReplayEvent, ReplayEventType, PartyMember, MultiplayerSession,
    SharedAdventure, ShareScope, AdventureRating, CommunityHub, PerformanceMonitor,
    UIThemeManager, ContentFilter
)
import time


# ============================================================================
# REPLAY RECORDING TESTS
# ============================================================================

def test_replay_recorder_creation():
    """Test replay recorder creation."""
    recorder = ReplayRecorder(session_id="session1")
    assert recorder.session_id == "session1"
    assert recorder.is_recording
    assert recorder.get_event_count() == 0
    print("✓ Replay recorder creation")


def test_replay_recorder_event():
    """Test recording replay event."""
    recorder = ReplayRecorder(session_id="session1")
    event = ReplayEvent(
        event_type=ReplayEventType.COMBAT,
        timestamp=1000.0,
        player_id="p1",
        description="Defeated goblin"
    )
    recorder.record_event(event)
    assert recorder.get_event_count() == 1
    print("✓ Replay recorder event")


def test_replay_recorder_stop():
    """Test stopping replay recording."""
    recorder = ReplayRecorder(session_id="session1")
    recorder.record_event(ReplayEvent(
        ReplayEventType.COMBAT, 1000.0, "p1", "Combat"
    ))
    assert recorder.is_recording
    count = recorder.stop_recording()
    assert not recorder.is_recording
    assert count == 1
    print("✓ Replay recorder stop")


def test_replay_recorder_duration():
    """Test replay duration calculation."""
    recorder = ReplayRecorder(session_id="session1")
    recorder.events = [
        ReplayEvent(ReplayEventType.COMBAT, 0.0, "p1", "Start"),
        ReplayEvent(ReplayEventType.COMBAT, 3600.0, "p1", "End")  # 3600 seconds = 60 minutes
    ]
    duration = recorder.get_duration()
    assert duration == 60.0  # Should be exactly 60 minutes
    print("✓ Replay recorder duration")


# ============================================================================
# PARTY MEMBER TESTS
# ============================================================================

def test_party_member_creation():
    """Test party member creation."""
    member = PartyMember(
        player_id="p1",
        username="Hero",
        character_class="Warrior",
        level=5
    )
    assert member.player_id == "p1"
    assert member.username == "Hero"
    assert not member.is_ready
    print("✓ Party member creation")


def test_party_member_ready():
    """Test setting party member ready."""
    member = PartyMember("p1", "Hero", "Warrior", 5)
    member.set_ready(True)
    assert member.is_ready
    print("✓ Party member ready")


# ============================================================================
# MULTIPLAYER SESSION TESTS
# ============================================================================

def test_multiplayer_session_creation():
    """Test multiplayer session creation."""
    session = MultiplayerSession(
        session_id="session1",
        host_player_id="p1"
    )
    assert session.session_id == "session1"
    assert session.host_player_id == "p1"
    assert session.is_active
    print("✓ Multiplayer session creation")


def test_multiplayer_session_add_member():
    """Test adding party member."""
    session = MultiplayerSession("session1", "p1")
    member = PartyMember("p1", "Host", "Warrior", 5)
    assert session.add_member(member)
    assert session.get_member_count() == 1
    print("✓ Multiplayer session add member")


def test_multiplayer_session_remove_member():
    """Test removing party member."""
    session = MultiplayerSession("session1", "p1")
    member = PartyMember("p1", "Host", "Warrior", 5)
    session.add_member(member)
    assert session.remove_member("p1")
    assert session.get_member_count() == 0
    print("✓ Multiplayer session remove member")


def test_multiplayer_session_party_full():
    """Test party size limit."""
    session = MultiplayerSession("session1", "p1", max_party_size=2)
    session.add_member(PartyMember("p1", "Host", "Warrior", 5))
    session.add_member(PartyMember("p2", "Player2", "Mage", 5))
    
    # Third member should fail
    assert not session.add_member(PartyMember("p3", "Player3", "Rogue", 5))
    assert session.get_member_count() == 2
    print("✓ Multiplayer session party full")


def test_multiplayer_session_ready_status():
    """Test checking if party is ready."""
    session = MultiplayerSession("session1", "p1")
    member1 = PartyMember("p1", "Host", "Warrior", 5)
    member2 = PartyMember("p2", "Player2", "Mage", 5)
    
    session.add_member(member1)
    session.add_member(member2)
    
    assert not session.are_all_ready()
    
    member1.set_ready(True)
    member2.set_ready(True)
    
    assert session.are_all_ready()
    print("✓ Multiplayer session ready status")


def test_multiplayer_session_average_level():
    """Test calculating average party level."""
    session = MultiplayerSession("session1", "p1")
    session.add_member(PartyMember("p1", "Host", "Warrior", 5))
    session.add_member(PartyMember("p2", "Player2", "Mage", 7))
    session.add_member(PartyMember("p3", "Player3", "Rogue", 9))
    
    avg_level = session.get_average_level()
    assert avg_level == 7  # (5+7+9)/3 = 7
    print("✓ Multiplayer session average level")


# ============================================================================
# ADVENTURE SHARING TESTS
# ============================================================================

def test_adventure_rating_creation():
    """Test adventure rating creation."""
    rating = AdventureRating(
        rater_id="p1",
        rating=5,
        review="Amazing adventure!"
    )
    assert rating.rater_id == "p1"
    assert rating.rating == 5
    print("✓ Adventure rating creation")


def test_shared_adventure_creation():
    """Test shared adventure creation."""
    adventure = SharedAdventure(
        adventure_id="adv1",
        creator_id="p1",
        title="Lost Temple",
        description="Explore an ancient temple"
    )
    assert adventure.adventure_id == "adv1"
    assert adventure.creator_id == "p1"
    assert adventure.scope == ShareScope.PRIVATE
    print("✓ Shared adventure creation")


def test_shared_adventure_rating():
    """Test adding ratings to adventure."""
    adventure = SharedAdventure(
        "adv1", "p1", "Lost Temple", "Explore"
    )
    assert adventure.get_average_rating() == 0.0
    
    adventure.add_rating(AdventureRating("p2", 5, "Great!"))
    adventure.add_rating(AdventureRating("p3", 3, "Good"))
    
    avg = adventure.get_average_rating()
    assert avg == 4.0  # (5+3)/2 = 4
    print("✓ Shared adventure rating")


def test_shared_adventure_downloads():
    """Test adventure download tracking."""
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    assert adventure.downloads == 0
    
    adventure.record_download()
    adventure.record_download()
    
    assert adventure.downloads == 2
    print("✓ Shared adventure downloads")


def test_shared_adventure_tags():
    """Test adventure tagging."""
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    
    adventure.add_tag("fantasy")
    adventure.add_tag("dungeon")
    adventure.add_tag("fantasy")  # Duplicate
    
    assert len(adventure.tags) == 2
    assert "fantasy" in adventure.tags
    print("✓ Shared adventure tags")


# ============================================================================
# COMMUNITY HUB TESTS
# ============================================================================

def test_community_hub_creation():
    """Test community hub creation."""
    hub = CommunityHub()
    assert len(hub.adventures) == 0
    print("✓ Community hub creation")


def test_community_hub_publish_adventure():
    """Test publishing adventure."""
    hub = CommunityHub()
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    
    assert hub.publish_adventure(adventure)
    assert "adv1" in hub.adventures
    print("✓ Community hub publish adventure")


def test_community_hub_get_adventure():
    """Test retrieving adventure."""
    hub = CommunityHub()
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    hub.publish_adventure(adventure)
    
    retrieved = hub.get_adventure("adv1")
    assert retrieved is not None
    assert retrieved.adventure_id == "adv1"
    print("✓ Community hub get adventure")


def test_community_hub_rate_adventure():
    """Test rating adventure."""
    hub = CommunityHub()
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    hub.publish_adventure(adventure)
    
    rating = AdventureRating("p2", 5, "Great!")
    assert hub.rate_adventure("adv1", rating)
    
    retrieved = hub.get_adventure("adv1")
    assert len(retrieved.ratings) == 1
    print("✓ Community hub rate adventure")


def test_community_hub_favorite():
    """Test favoriting adventures."""
    hub = CommunityHub()
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    hub.publish_adventure(adventure)
    
    assert hub.favorite_adventure("p2", "adv1")
    favorites = hub.get_player_favorites("p2")
    assert len(favorites) == 1
    print("✓ Community hub favorite")


def test_community_hub_unfavorite():
    """Test unfavoriting adventures."""
    hub = CommunityHub()
    adventure = SharedAdventure("adv1", "p1", "Title", "Desc")
    hub.publish_adventure(adventure)
    hub.favorite_adventure("p2", "adv1")
    
    assert hub.unfavorite_adventure("p2", "adv1")
    favorites = hub.get_player_favorites("p2")
    assert len(favorites) == 0
    print("✓ Community hub unfavorite")


def test_community_hub_search():
    """Test searching adventures."""
    hub = CommunityHub()
    hub.publish_adventure(SharedAdventure("adv1", "p1", "Lost Temple", "Explore"))
    hub.publish_adventure(SharedAdventure("adv2", "p1", "Dragon's Lair", "Fight"))
    hub.publish_adventure(SharedAdventure("adv3", "p1", "Ancient Ruins", "Explore"))
    
    results = hub.search_adventures("Explore")
    assert len(results) == 2
    print("✓ Community hub search")


def test_community_hub_trending():
    """Test getting trending adventures."""
    hub = CommunityHub()
    adv1 = SharedAdventure("adv1", "p1", "Popular", "Desc")
    adv2 = SharedAdventure("adv2", "p1", "Less Popular", "Desc")
    
    hub.publish_adventure(adv1)
    hub.publish_adventure(adv2)
    
    # Give adv1 more downloads
    adv1.record_download()
    adv1.record_download()
    adv1.record_download()
    
    trending = hub.get_trending(10)
    assert trending[0].adventure_id == "adv1"
    print("✓ Community hub trending")


def test_community_hub_top_rated():
    """Test getting top-rated adventures."""
    hub = CommunityHub()
    adv1 = SharedAdventure("adv1", "p1", "Highly Rated", "Desc")
    adv2 = SharedAdventure("adv2", "p1", "Less Rated", "Desc")
    
    hub.publish_adventure(adv1)
    hub.publish_adventure(adv2)
    
    # Rate adv1 highly
    adv1.add_rating(AdventureRating("p2", 5, "Amazing"))
    adv2.add_rating(AdventureRating("p2", 3, "Good"))
    
    top_rated = hub.get_top_rated(10)
    assert top_rated[0].adventure_id == "adv1"
    print("✓ Community hub top rated")


def test_community_hub_featured():
    """Test featuring adventures."""
    hub = CommunityHub()
    adv = SharedAdventure("adv1", "p1", "Featured", "Desc")
    hub.publish_adventure(adv)
    
    assert hub.feature_adventure("adv1")
    featured = hub.get_featured()
    assert len(featured) == 1
    print("✓ Community hub featured")


def test_community_hub_multiplayer_session():
    """Test managing multiplayer sessions."""
    hub = CommunityHub()
    session = MultiplayerSession("session1", "p1")
    
    assert hub.create_multiplayer_session(session)
    retrieved = hub.get_multiplayer_session("session1")
    assert retrieved is not None
    assert hub.end_multiplayer_session("session1")
    print("✓ Community hub multiplayer session")


# ============================================================================
# PERFORMANCE MONITORING TESTS
# ============================================================================

def test_performance_monitor_creation():
    """Test performance monitor creation."""
    monitor = PerformanceMonitor()
    assert monitor.fps == 60.0
    assert monitor.latency_ms == 0.0
    print("✓ Performance monitor creation")


def test_performance_monitor_frame_time():
    """Test recording frame times."""
    monitor = PerformanceMonitor()
    monitor.record_frame_time(16.67)  # 60 FPS
    monitor.record_frame_time(16.67)
    monitor.record_frame_time(16.67)
    
    assert len(monitor.frame_times) == 3
    print("✓ Performance monitor frame time")


def test_performance_monitor_average_fps():
    """Test calculating average FPS."""
    monitor = PerformanceMonitor()
    monitor.record_frame_time(16.67)  # 60 FPS
    monitor.record_frame_time(16.67)
    monitor.record_frame_time(16.67)
    
    avg_fps = monitor.get_average_fps()
    assert 59 < avg_fps < 61
    print("✓ Performance monitor average FPS")


def test_performance_monitor_performance_check():
    """Test performance status check."""
    monitor = PerformanceMonitor()
    
    # Good performance
    monitor.record_frame_time(16.67)
    monitor.latency_ms = 50
    assert monitor.is_performance_good()
    
    # Poor performance
    monitor.latency_ms = 300
    assert not monitor.is_performance_good()
    print("✓ Performance monitor performance check")


# ============================================================================
# UI THEME TESTS
# ============================================================================

def test_ui_theme_manager_creation():
    """Test UI theme manager creation."""
    manager = UIThemeManager()
    assert manager.active_theme == "default"
    print("✓ UI theme manager creation")


def test_ui_theme_register():
    """Test registering themes."""
    manager = UIThemeManager()
    config = {"text_color": "white", "bg_color": "black"}
    manager.register_theme("dark", config)
    
    assert "dark" in manager.themes
    print("✓ UI theme register")


def test_ui_theme_set_active():
    """Test setting active theme."""
    manager = UIThemeManager()
    manager.register_theme("dark", {"text_color": "white"})
    
    assert manager.set_active_theme("dark")
    assert manager.active_theme == "dark"
    print("✓ UI theme set active")


def test_ui_theme_get_active():
    """Test getting active theme."""
    manager = UIThemeManager()
    config = {"text_color": "white", "bg_color": "black"}
    manager.register_theme("dark", config)
    manager.set_active_theme("dark")
    
    active = manager.get_active_theme()
    assert active["text_color"] == "white"
    print("✓ UI theme get active")


# ============================================================================
# CONTENT FILTER TESTS
# ============================================================================

def test_content_filter_creation():
    """Test content filter creation."""
    filter_obj = ContentFilter()
    assert len(filter_obj.blocked_words) == 0
    print("✓ Content filter creation")


def test_content_filter_block_word():
    """Test blocking words."""
    filter_obj = ContentFilter()
    filter_obj.add_blocked_word("badword")
    
    assert "badword" in filter_obj.blocked_words
    print("✓ Content filter block word")


def test_content_filter_check_clean():
    """Test checking content cleanliness."""
    filter_obj = ContentFilter()
    filter_obj.add_blocked_word("badword")
    
    assert filter_obj.is_content_clean("This is good content")
    assert not filter_obj.is_content_clean("This contains badword")
    print("✓ Content filter check clean")


def test_content_filter_warnings():
    """Test content warnings."""
    filter_obj = ContentFilter()
    adventure = SharedAdventure(
        "adv1", "p1", "Title", "Desc",
        difficulty="legendary", playtime_minutes=300
    )
    
    warnings = filter_obj.get_content_warnings(adventure)
    assert len(warnings) > 0
    assert any("Extreme difficulty" in w for w in warnings)
    print("✓ Content filter warnings")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_multiplayer_workflow():
    """Test complete multiplayer workflow."""
    # Create multiplayer session
    session = MultiplayerSession("session1", "p1")
    
    # Add party members
    member1 = PartyMember("p1", "Host", "Warrior", 5)
    member2 = PartyMember("p2", "Player2", "Mage", 5)
    
    assert session.add_member(member1)
    assert session.add_member(member2)
    
    # Set ready
    member1.set_ready(True)
    member2.set_ready(True)
    
    assert session.are_all_ready()
    assert session.get_average_level() == 5
    print("✓ Full multiplayer workflow")


def test_full_community_workflow():
    """Test complete community workflow."""
    hub = CommunityHub()
    
    # Create and publish adventure
    adventure = SharedAdventure(
        "adv1", "creator", "Lost Temple", "Explore ancient ruins",
        scope=ShareScope.PUBLIC
    )
    adventure.add_tag("adventure")
    adventure.add_tag("exploration")
    
    assert hub.publish_adventure(adventure)
    
    # Favorite and rate
    assert hub.favorite_adventure("player1", "adv1")
    hub.rate_adventure("adv1", AdventureRating("player1", 5, "Amazing!"))
    
    # Record download
    hub.download_adventure("adv1")
    
    # Verify
    retrieved = hub.get_adventure("adv1")
    assert retrieved.downloads == 1
    assert len(retrieved.ratings) == 1
    assert "adventure" in retrieved.tags
    print("✓ Full community workflow")


if __name__ == "__main__":
    # Replay Recording Tests
    test_replay_recorder_creation()
    test_replay_recorder_event()
    test_replay_recorder_stop()
    test_replay_recorder_duration()
    
    # Party Member Tests
    test_party_member_creation()
    test_party_member_ready()
    
    # Multiplayer Session Tests
    test_multiplayer_session_creation()
    test_multiplayer_session_add_member()
    test_multiplayer_session_remove_member()
    test_multiplayer_session_party_full()
    test_multiplayer_session_ready_status()
    test_multiplayer_session_average_level()
    
    # Adventure Sharing Tests
    test_adventure_rating_creation()
    test_shared_adventure_creation()
    test_shared_adventure_rating()
    test_shared_adventure_downloads()
    test_shared_adventure_tags()
    
    # Community Hub Tests
    test_community_hub_creation()
    test_community_hub_publish_adventure()
    test_community_hub_get_adventure()
    test_community_hub_rate_adventure()
    test_community_hub_favorite()
    test_community_hub_unfavorite()
    test_community_hub_search()
    test_community_hub_trending()
    test_community_hub_top_rated()
    test_community_hub_featured()
    test_community_hub_multiplayer_session()
    
    # Performance Monitoring Tests
    test_performance_monitor_creation()
    test_performance_monitor_frame_time()
    test_performance_monitor_average_fps()
    test_performance_monitor_performance_check()
    
    # UI Theme Tests
    test_ui_theme_manager_creation()
    test_ui_theme_register()
    test_ui_theme_set_active()
    test_ui_theme_get_active()
    
    # Content Filter Tests
    test_content_filter_creation()
    test_content_filter_block_word()
    test_content_filter_check_clean()
    test_content_filter_warnings()
    
    # Integration Tests
    test_full_multiplayer_workflow()
    test_full_community_workflow()
    
    print("\n" + "="*60)
    print("PHASE X: POLISH, PERFORMANCE & LAUNCH")
    print("✓ All 31 tests passed!")
    print("="*60)

