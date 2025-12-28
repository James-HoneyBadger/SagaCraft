"""
Phase IX: Web Integration & Cloud - Test Suite

Tests for cloud saves, achievements, leaderboards, web server, and sessions.
25+ tests covering all cloud features.

Tests:
    Player & Cloud Save Management
    Achievement System
    Leaderboard System
    Web Server API
    Session Management
    Authentication
"""

import sys
sys.path.insert(0, '/home/james/SagaCraft/src')

from sagacraft.systems.cloud import (
    Player, CloudSave, CloudManager, Achievement, AchievementCategory,
    AchievementUnlock, AchievementSystem, Leaderboard, LeaderboardManager,
    OnlineSession, SessionManager
)
from sagacraft.systems.web_server import (
    GameServerAPI, APIEndpoint, HTTPMethod, ErrorResponse, ErrorCode,
    GameStateDTO, RateLimiter, WebSocketManager, APIAuthenticator
)
import uuid
from datetime import datetime, timedelta


# ============================================================================
# PLAYER & CLOUD SAVE TESTS
# ============================================================================

def test_player_creation():
    """Test player profile creation."""
    player = Player(player_id="p1", username="Hero")
    assert player.player_id == "p1"
    assert player.username == "Hero"
    assert player.level == 1
    assert player.experience == 0
    print("✓ Player creation")


def test_player_to_dict():
    """Test player serialization."""
    player = Player(player_id="p1", username="Hero", level=5, experience=1000)
    data = player.to_dict()
    assert data["player_id"] == "p1"
    assert data["username"] == "Hero"
    assert data["level"] == 5
    assert data["experience"] == 1000
    print("✓ Player serialization")


def test_player_from_dict():
    """Test player deserialization."""
    data = {
        "player_id": "p1",
        "username": "Hero",
        "level": 5,
        "experience": 1000,
        "created_at": "2024-01-01 10:00:00",
        "last_login": "2024-01-02 11:00:00",
        "total_playtime_hours": 25.5
    }
    player = Player.from_dict(data)
    assert player.player_id == "p1"
    assert player.username == "Hero"
    assert player.level == 5
    print("✓ Player deserialization")


def test_cloud_save_creation():
    """Test cloud save creation."""
    game_state = {"location": "village", "health": 100}
    save = CloudSave(
        save_id="save1",
        player_id="p1",
        save_name="My Adventure",
        created_at="",
        last_updated="",
        game_state=game_state
    )
    assert save.save_id == "save1"
    assert save.player_id == "p1"
    assert save.game_state == game_state
    print("✓ Cloud save creation")


def test_cloud_save_json_serialization():
    """Test cloud save JSON serialization."""
    game_state = {"location": "village", "health": 100}
    save = CloudSave(
        save_id="save1",
        player_id="p1",
        save_name="My Adventure",
        created_at="2024-01-01 10:00:00",
        last_updated="2024-01-01 10:00:00",
        game_state=game_state
    )
    json_str = save.to_json()
    assert isinstance(json_str, str)
    loaded = CloudSave.from_json(json_str)
    assert loaded.save_id == save.save_id
    assert loaded.player_id == save.player_id
    print("✓ Cloud save JSON serialization")


def test_cloud_manager_save_game():
    """Test saving game to cloud."""
    manager = CloudManager()
    game_state = {"location": "village", "health": 100}
    save = CloudSave(
        save_id="save1",
        player_id="p1",
        save_name="My Adventure",
        created_at="2024-01-01 10:00:00",
        last_updated="2024-01-01 10:00:00",
        game_state=game_state
    )
    assert manager.save_game(save)
    assert "p1" in manager.saves
    print("✓ Cloud manager save game")


def test_cloud_manager_load_game():
    """Test loading game from cloud."""
    manager = CloudManager()
    game_state = {"location": "village", "health": 100}
    save = CloudSave(
        save_id="save1",
        player_id="p1",
        save_name="My Adventure",
        created_at="2024-01-01 10:00:00",
        last_updated="2024-01-01 10:00:00",
        game_state=game_state
    )
    manager.save_game(save)
    loaded = manager.load_game("p1", "save1")
    assert loaded is not None
    assert loaded.save_id == "save1"
    assert loaded.game_state == game_state
    print("✓ Cloud manager load game")


def test_cloud_manager_multiple_saves():
    """Test managing multiple saves per player."""
    manager = CloudManager()
    for i in range(3):
        save = CloudSave(
            save_id=f"save{i}",
            player_id="p1",
            save_name=f"Save {i}",
            created_at="2024-01-01 10:00:00",
            last_updated="2024-01-01 10:00:00",
            game_state={"checkpoint": i}
        )
        manager.save_game(save)
    
    saves = manager.get_player_saves("p1")
    assert len(saves) == 3
    print("✓ Cloud manager multiple saves")


def test_cloud_manager_delete_save():
    """Test deleting save."""
    manager = CloudManager()
    save = CloudSave(
        save_id="save1",
        player_id="p1",
        save_name="My Adventure",
        created_at="2024-01-01 10:00:00",
        last_updated="2024-01-01 10:00:00",
        game_state={}
    )
    manager.save_game(save)
    assert manager.delete_save("p1", "save1")
    assert manager.load_game("p1", "save1") is None
    print("✓ Cloud manager delete save")


# ============================================================================
# ACHIEVEMENT TESTS
# ============================================================================

def test_achievement_creation():
    """Test achievement definition."""
    achievement = Achievement(
        achievement_id="ach1",
        title="First Blood",
        description="Defeat your first enemy",
        category=AchievementCategory.COMBAT,
        points=10
    )
    assert achievement.achievement_id == "ach1"
    assert achievement.title == "First Blood"
    print("✓ Achievement creation")


def test_achievement_system_register():
    """Test registering achievements."""
    system = AchievementSystem()
    achievement = Achievement(
        achievement_id="ach1",
        title="First Blood",
        description="Defeat your first enemy",
        category=AchievementCategory.COMBAT
    )
    system.register_achievement(achievement)
    assert "ach1" in system.all_achievements
    print("✓ Achievement registration")


def test_achievement_unlock():
    """Test unlocking achievement."""
    system = AchievementSystem()
    achievement = Achievement(
        achievement_id="ach1",
        title="First Blood",
        description="Defeat your first enemy",
        category=AchievementCategory.COMBAT
    )
    system.register_achievement(achievement)
    
    assert system.unlock_achievement("p1", "ach1")
    assert system.is_unlocked("p1", "ach1")
    assert not system.unlock_achievement("p1", "ach1")  # Already unlocked
    print("✓ Achievement unlock")


def test_achievement_points():
    """Test achievement points calculation."""
    system = AchievementSystem()
    for i in range(3):
        achievement = Achievement(
            achievement_id=f"ach{i}",
            title=f"Achievement {i}",
            description="",
            category=AchievementCategory.COMBAT,
            points=10 * (i + 1)
        )
        system.register_achievement(achievement)
        system.unlock_achievement("p1", f"ach{i}")
    
    points = system.get_achievement_points("p1")
    assert points == 60  # 10 + 20 + 30
    print("✓ Achievement points")


def test_achievement_progress():
    """Test achievement progress tracking."""
    system = AchievementSystem()
    achievement = Achievement(
        achievement_id="ach_kill_10",
        title="Kill 10 Enemies",
        description="Defeat 10 enemies",
        category=AchievementCategory.COMBAT
    )
    system.register_achievement(achievement)
    
    system.set_progress("p1", "ach_kill_10", 5)
    assert system.get_progress("p1", "ach_kill_10") == 5
    
    system.set_progress("p1", "ach_kill_10", 10)
    assert system.unlock_achievement("p1", "ach_kill_10")
    print("✓ Achievement progress")


# ============================================================================
# LEADERBOARD TESTS
# ============================================================================

def test_leaderboard_creation():
    """Test leaderboard creation."""
    leaderboard = Leaderboard(
        leaderboard_id="lb_score",
        title="High Scores"
    )
    assert leaderboard.leaderboard_id == "lb_score"
    assert leaderboard.title == "High Scores"
    print("✓ Leaderboard creation")


def test_leaderboard_add_entry():
    """Test adding leaderboard entry."""
    leaderboard = Leaderboard(
        leaderboard_id="lb_score",
        title="High Scores"
    )
    rank = leaderboard.add_entry("p1", "Hero", 1000)
    assert rank == 1
    assert len(leaderboard.entries) == 1
    print("✓ Leaderboard add entry")


def test_leaderboard_ranking():
    """Test leaderboard ranking."""
    leaderboard = Leaderboard(
        leaderboard_id="lb_score",
        title="High Scores"
    )
    leaderboard.add_entry("p1", "Hero", 1000)
    leaderboard.add_entry("p2", "Warrior", 1500)
    leaderboard.add_entry("p3", "Mage", 800)
    
    assert leaderboard.get_player_rank("p2") == 1  # Highest score
    assert leaderboard.get_player_rank("p1") == 2
    assert leaderboard.get_player_rank("p3") == 3
    print("✓ Leaderboard ranking")


def test_leaderboard_get_top():
    """Test getting top entries."""
    leaderboard = Leaderboard(
        leaderboard_id="lb_score",
        title="High Scores"
    )
    for i in range(5):
        leaderboard.add_entry(f"p{i}", f"Player{i}", 1000 - i * 100)
    
    top = leaderboard.get_top(3)
    assert len(top) == 3
    assert top[0].rank == 1
    assert top[2].rank == 3
    print("✓ Leaderboard get top")


def test_leaderboard_manager():
    """Test leaderboard manager."""
    manager = LeaderboardManager()
    manager.create_leaderboard("lb_score", "High Scores")
    manager.create_leaderboard("lb_level", "Highest Level")
    
    rank1 = manager.submit_score("lb_score", "p1", "Hero", 1000)
    rank2 = manager.submit_score("lb_score", "p2", "Warrior", 1500)
    
    # p2 has higher score so should be rank 1
    assert manager.get_leaderboard_position("lb_score", "p1") == 2
    assert manager.get_leaderboard_position("lb_score", "p2") == 1
    print("✓ Leaderboard manager")


# ============================================================================
# SESSION TESTS
# ============================================================================

def test_session_creation():
    """Test session creation."""
    manager = SessionManager()
    session = manager.create_session("session1", "p1")
    assert session.player_id == "p1"
    assert session.is_active
    print("✓ Session creation")


def test_session_retrieval():
    """Test retrieving session."""
    manager = SessionManager()
    manager.create_session("session1", "p1")
    session = manager.get_session("session1")
    assert session is not None
    assert session.player_id == "p1"
    print("✓ Session retrieval")


def test_session_end():
    """Test ending session."""
    manager = SessionManager()
    manager.create_session("session1", "p1")
    assert manager.end_session("session1")
    session = manager.get_session("session1")
    assert not session.is_active
    print("✓ Session end")


def test_session_touch():
    """Test updating session activity."""
    manager = SessionManager()
    session = manager.create_session("session1", "p1")
    
    # Manually set a past time
    original_activity = "2024-01-01 10:00:00"
    session.last_activity = original_activity
    
    assert manager.touch_session("session1")
    updated_session = manager.get_session("session1")
    # Should have updated to current time (which will be later)
    assert updated_session.last_activity != original_activity
    print("✓ Session touch")


def test_session_cleanup():
    """Test cleaning up expired sessions."""
    manager = SessionManager()
    manager.create_session("session1", "p1")
    session = manager.get_session("session1")
    session.last_activity = "2020-01-01 00:00:00"
    
    cleaned = manager.cleanup_expired(timeout_minutes=30)
    assert cleaned == 1
    assert manager.get_session("session1") is None
    print("✓ Session cleanup")


# ============================================================================
# WEB SERVER API TESTS
# ============================================================================

def test_api_endpoint_registration():
    """Test registering API endpoint."""
    api = GameServerAPI()
    
    def handler(data):
        return {"status": "ok"}
    
    endpoint = APIEndpoint(
        path="/health",
        method=HTTPMethod.GET,
        handler=handler,
        requires_auth=False
    )
    api.register_endpoint(endpoint)
    
    assert "GET /health" in api.endpoints
    print("✓ API endpoint registration")


def test_api_call_endpoint():
    """Test calling API endpoint."""
    api = GameServerAPI()
    
    def handler(data):
        return {"status": "ok"}
    
    endpoint = APIEndpoint(
        path="/health",
        method=HTTPMethod.GET,
        handler=handler,
        requires_auth=False
    )
    api.register_endpoint(endpoint)
    
    response = api.call_endpoint("GET", "/health", {})
    assert response["success"]
    assert response["data"]["status"] == "ok"
    print("✓ API call endpoint")


def test_api_authentication_required():
    """Test authentication requirement."""
    api = GameServerAPI()
    
    def handler(data):
        return {"status": "ok"}
    
    endpoint = APIEndpoint(
        path="/secure",
        method=HTTPMethod.POST,
        handler=handler,
        requires_auth=True
    )
    api.register_endpoint(endpoint)
    
    response = api.call_endpoint("POST", "/secure", {})
    assert "error_code" in response
    assert response["error_code"] == "UNAUTHORIZED"
    print("✓ API authentication required")


def test_api_endpoint_not_found():
    """Test endpoint not found."""
    api = GameServerAPI()
    response = api.call_endpoint("GET", "/nonexistent", {})
    assert "error_code" in response
    assert response["error_code"] == "NOT_FOUND"
    print("✓ API endpoint not found")


def test_game_state_dto():
    """Test game state data transfer object."""
    dto = GameStateDTO(
        player_id="p1",
        location="village",
        level=5,
        experience=1000
    )
    assert dto.player_id == "p1"
    assert dto.location == "village"
    
    data = dto.to_dict()
    restored = GameStateDTO.from_dict(data)
    assert restored.player_id == "p1"
    print("✓ Game state DTO")


# ============================================================================
# RATE LIMITER TESTS
# ============================================================================

def test_rate_limiter():
    """Test rate limiter."""
    limiter = RateLimiter(requests_per_minute=3)
    
    # First 3 requests should be allowed
    assert limiter.is_allowed("client1")
    assert limiter.is_allowed("client1")
    assert limiter.is_allowed("client1")
    
    # 4th request should be blocked
    assert not limiter.is_allowed("client1")
    print("✓ Rate limiter")


def test_rate_limiter_different_clients():
    """Test rate limiter with different clients."""
    limiter = RateLimiter(requests_per_minute=2)
    
    assert limiter.is_allowed("client1")
    assert limiter.is_allowed("client2")
    assert limiter.is_allowed("client1")
    
    # Client1 should be limited, but client2 can still make a request
    assert not limiter.is_allowed("client1")
    assert limiter.is_allowed("client2")
    print("✓ Rate limiter different clients")


# ============================================================================
# WEB SOCKET TESTS
# ============================================================================

def test_websocket_connection():
    """Test WebSocket connection management."""
    manager = WebSocketManager()
    manager.register_connection("client1", "connection_obj")
    
    assert "client1" in manager.connections
    manager.disconnect("client1")
    assert "client1" not in manager.connections
    print("✓ WebSocket connection")


def test_websocket_subscriptions():
    """Test WebSocket subscriptions."""
    manager = WebSocketManager()
    manager.register_connection("client1", "conn1")
    manager.register_connection("client2", "conn2")
    
    manager.subscribe("client1", "game_updates")
    manager.subscribe("client2", "game_updates")
    
    count = manager.broadcast("game_updates", {"event": "new_quest"})
    assert count == 2
    print("✓ WebSocket subscriptions")


def test_websocket_broadcast():
    """Test WebSocket broadcasting."""
    manager = WebSocketManager()
    manager.register_connection("client1", "conn1")
    manager.register_connection("client2", "conn2")
    manager.subscribe("client1", "chat")
    manager.subscribe("client2", "chat")
    
    manager.broadcast("chat", {"message": "Hello"})
    messages = manager.get_pending_messages()
    
    assert len(messages) == 1
    assert messages[0]["topic"] == "chat"
    print("✓ WebSocket broadcast")


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_authenticator_create_token():
    """Test token creation."""
    authenticator = APIAuthenticator()
    token = authenticator.create_token("p1", "Hero")
    assert isinstance(token, str)
    assert len(token) > 0
    print("✓ Authenticator create token")


def test_authenticator_validate_token():
    """Test token validation."""
    authenticator = APIAuthenticator()
    token = authenticator.create_token("p1", "Hero")
    
    data = authenticator.validate_token(token)
    assert data is not None
    assert data["player_id"] == "p1"
    assert data["username"] == "Hero"
    print("✓ Authenticator validate token")


def test_authenticator_revoke_token():
    """Test token revocation."""
    authenticator = APIAuthenticator()
    token = authenticator.create_token("p1", "Hero")
    
    assert authenticator.revoke_token(token)
    assert authenticator.validate_token(token) is None
    print("✓ Authenticator revoke token")


def test_authenticator_cleanup_expired():
    """Test cleaning up expired tokens."""
    authenticator = APIAuthenticator()
    token = authenticator.create_token("p1", "Hero", expires_in_hours=0)
    
    import time
    time.sleep(0.1)
    
    cleaned = authenticator.cleanup_expired()
    assert cleaned > 0
    print("✓ Authenticator cleanup expired")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_cloud_workflow():
    """Test complete cloud save workflow."""
    # Create player
    player = Player(player_id="p1", username="Hero", level=5, experience=1000)
    
    # Create cloud save
    game_state = {"location": "castle", "health": 100, "companions": ["companion1"]}
    save = CloudSave(
        save_id="save1",
        player_id="p1",
        save_name="My Adventure",
        created_at="2024-01-01 10:00:00",
        last_updated="2024-01-01 10:00:00",
        game_state=game_state
    )
    
    # Save to cloud
    manager = CloudManager()
    assert manager.save_game(save)
    
    # Load from cloud
    loaded = manager.load_game("p1", "save1")
    assert loaded.game_state == game_state
    
    # Create achievement
    achievement_system = AchievementSystem()
    achievement = Achievement(
        achievement_id="ach1",
        title="Cloud Save Master",
        description="Save to cloud",
        category=AchievementCategory.PROGRESSION
    )
    achievement_system.register_achievement(achievement)
    achievement_system.unlock_achievement("p1", "ach1")
    
    # Create leaderboard entry
    leaderboard_manager = LeaderboardManager()
    leaderboard_manager.create_leaderboard("lb_level", "Highest Level")
    rank = leaderboard_manager.submit_score("lb_level", "p1", "Hero", player.level)
    
    assert rank == 1
    assert achievement_system.is_unlocked("p1", "ach1")
    print("✓ Full cloud workflow")


if __name__ == "__main__":
    # Cloud & Player Tests
    test_player_creation()
    test_player_to_dict()
    test_player_from_dict()
    test_cloud_save_creation()
    test_cloud_save_json_serialization()
    test_cloud_manager_save_game()
    test_cloud_manager_load_game()
    test_cloud_manager_multiple_saves()
    test_cloud_manager_delete_save()
    
    # Achievement Tests
    test_achievement_creation()
    test_achievement_system_register()
    test_achievement_unlock()
    test_achievement_points()
    test_achievement_progress()
    
    # Leaderboard Tests
    test_leaderboard_creation()
    test_leaderboard_add_entry()
    test_leaderboard_ranking()
    test_leaderboard_get_top()
    test_leaderboard_manager()
    
    # Session Tests
    test_session_creation()
    test_session_retrieval()
    test_session_end()
    test_session_touch()
    test_session_cleanup()
    
    # API Tests
    test_api_endpoint_registration()
    test_api_call_endpoint()
    test_api_authentication_required()
    test_api_endpoint_not_found()
    test_game_state_dto()
    
    # Rate Limiter Tests
    test_rate_limiter()
    test_rate_limiter_different_clients()
    
    # WebSocket Tests
    test_websocket_connection()
    test_websocket_subscriptions()
    test_websocket_broadcast()
    
    # Authentication Tests
    test_authenticator_create_token()
    test_authenticator_validate_token()
    test_authenticator_revoke_token()
    test_authenticator_cleanup_expired()
    
    # Integration Tests
    test_full_cloud_workflow()
    
    print("\n" + "="*60)
    print("PHASE IX: WEB INTEGRATION & CLOUD")
    print("✓ All 25 tests passed!")
    print("="*60)

