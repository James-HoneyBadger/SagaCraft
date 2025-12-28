"""
Phase IX: Web Server Integration

FastAPI server setup for SagaCraft.
Provides REST API endpoints for game state, saves, achievements, and leaderboards.

Classes:
    GameServerAPI: Main FastAPI application wrapper
    APIEndpoint: Endpoint configuration
    GameStateDTO: Data transfer object for game state
    ErrorResponse: Standard error response

Type Hints: 100%
External Dependencies: FastAPI (optional for web server)
Test Coverage: 25+ tests
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ErrorCode(Enum):
    """API error codes."""
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_REQUEST = "INVALID_REQUEST"
    SERVER_ERROR = "SERVER_ERROR"
    CONFLICT = "CONFLICT"


@dataclass
class ErrorResponse:
    """Standard error response."""
    error_code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class GameStateDTO:
    """Data transfer object for game state."""
    player_id: str
    location: str
    level: int
    experience: int
    health: int = 0
    mana: int = 0
    inventory: List[str] = field(default_factory=list)
    companions: List[str] = field(default_factory=list)
    active_quests: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "player_id": self.player_id,
            "location": self.location,
            "level": self.level,
            "experience": self.experience,
            "health": self.health,
            "mana": self.mana,
            "inventory": self.inventory,
            "companions": self.companions,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GameStateDTO':
        """Create from dictionary."""
        return GameStateDTO(**{k: v for k, v in data.items() if k in [
            'player_id', 'location', 'level', 'experience', 'health', 'mana',
            'inventory', 'companions', 'active_quests', 'completed_quests', 'metadata'
        ]})
    
    @staticmethod
    def from_json(json_str: str) -> 'GameStateDTO':
        """Create from JSON."""
        data = json.loads(json_str)
        return GameStateDTO.from_dict(data)


@dataclass
class APIEndpoint:
    """API endpoint configuration."""
    path: str
    method: HTTPMethod
    handler: Callable[[Dict[str, Any]], Any]
    requires_auth: bool = True
    rate_limit: Optional[int] = None  # Requests per minute
    description: str = ""


@dataclass
class GameServerAPI:
    """
    Main FastAPI application wrapper.
    
    Provides REST API for SagaCraft game server.
    
    Attributes:
        endpoints: Dict[path, APIEndpoint]
        middleware: List of middleware functions
        rate_limiters: Dict[endpoint_path, RateLimiter]
    """
    endpoints: Dict[str, APIEndpoint] = field(default_factory=dict)
    middleware: List[Callable] = field(default_factory=list)
    rate_limiters: Dict[str, 'RateLimiter'] = field(default_factory=dict)
    api_version: str = "1.0"
    max_request_size: int = 10_000_000  # 10MB
    
    def register_endpoint(self, endpoint: APIEndpoint) -> None:
        """
        Register API endpoint.
        
        Args:
            endpoint: APIEndpoint to register
        """
        key = f"{endpoint.method.value} {endpoint.path}"
        self.endpoints[key] = endpoint
        
        if endpoint.rate_limit:
            self.rate_limiters[endpoint.path] = RateLimiter(endpoint.rate_limit)
    
    def register_middleware(self, middleware: Callable) -> None:
        """Register middleware function."""
        self.middleware.append(middleware)
    
    def call_endpoint(self, method: str, path: str, 
                     data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """
        Call endpoint handler.
        
        Args:
            method: HTTP method
            path: Request path
            data: Request data
            token: Auth token
            
        Returns:
            Response data
        """
        key = f"{method} {path}"
        endpoint = self.endpoints.get(key)
        
        if not endpoint:
            return ErrorResponse(
                ErrorCode.NOT_FOUND,
                f"Endpoint not found: {key}"
            ).to_dict()
        
        # Check authentication
        if endpoint.requires_auth and not token:
            return ErrorResponse(
                ErrorCode.UNAUTHORIZED,
                "Authentication required"
            ).to_dict()
        
        # Check rate limit
        if endpoint.path in self.rate_limiters:
            limiter = self.rate_limiters[endpoint.path]
            if not limiter.is_allowed(token or "anonymous"):
                return ErrorResponse(
                    ErrorCode.CONFLICT,
                    "Rate limit exceeded"
                ).to_dict()
        
        # Run through middleware
        request_data = data
        for mw in self.middleware:
            request_data = mw(request_data)
        
        # Call handler
        try:
            result = endpoint.handler(request_data)
            return {"success": True, "data": result}
        except Exception as e:
            return ErrorResponse(
                ErrorCode.SERVER_ERROR,
                str(e)
            ).to_dict()
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all registered routes."""
        routes = []
        for key, endpoint in self.endpoints.items():
            routes.append({
                "path": endpoint.path,
                "method": endpoint.method.value,
                "requires_auth": endpoint.requires_auth,
                "rate_limit": endpoint.rate_limit,
                "description": endpoint.description
            })
        return routes


@dataclass
class RateLimiter:
    """Rate limiter for API endpoints."""
    requests_per_minute: int
    requests: Dict[str, List[float]] = field(default_factory=dict)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            identifier: Client identifier (IP, token, etc.)
            
        Returns:
            True if allowed, False if rate limited
        """
        import time
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            t for t in self.requests[identifier] if t > minute_ago
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False
        
        # Record request
        self.requests[identifier].append(current_time)
        return True


@dataclass
class WebSocketManager:
    """
    Manages WebSocket connections for real-time features.
    
    Attributes:
        connections: Dict[client_id, connection]
        subscriptions: Dict[topic, Set[client_id]]
        messages: List of pending messages
    """
    connections: Dict[str, Any] = field(default_factory=dict)
    subscriptions: Dict[str, set] = field(default_factory=dict)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    
    def register_connection(self, client_id: str, connection: Any) -> None:
        """Register WebSocket connection."""
        self.connections[client_id] = connection
    
    def disconnect(self, client_id: str) -> None:
        """Disconnect client."""
        if client_id in self.connections:
            del self.connections[client_id]
        
        # Remove from all subscriptions
        for topic_subscribers in self.subscriptions.values():
            topic_subscribers.discard(client_id)
    
    def subscribe(self, client_id: str, topic: str) -> None:
        """Subscribe client to topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(client_id)
    
    def unsubscribe(self, client_id: str, topic: str) -> None:
        """Unsubscribe client from topic."""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)
    
    def broadcast(self, topic: str, message: Dict[str, Any]) -> int:
        """
        Broadcast message to all subscribers.
        
        Args:
            topic: Topic to broadcast to
            message: Message to send
            
        Returns:
            Number of clients notified
        """
        if topic not in self.subscriptions:
            return 0
        
        message_with_topic = {"topic": topic, **message}
        self.messages.append(message_with_topic)
        
        return len(self.subscriptions[topic])
    
    def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific client."""
        if client_id not in self.connections:
            return False
        
        message["target_client"] = client_id
        self.messages.append(message)
        return True
    
    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """Get pending messages."""
        pending = self.messages.copy()
        self.messages.clear()
        return pending
    
    def get_active_connections(self) -> int:
        """Get count of active connections."""
        return len(self.connections)


@dataclass
class APIAuthenticator:
    """Manages API authentication and tokens."""
    tokens: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def create_token(self, player_id: str, username: str,
                    expires_in_hours: int = 24) -> str:
        """
        Create authentication token.
        
        Args:
            player_id: Player identifier
            username: Player username
            expires_in_hours: Token expiration time
            
        Returns:
            Token string
        """
        import hashlib
        import time
        
        token_data = f"{player_id}:{username}:{time.time()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        self.tokens[token] = {
            "player_id": player_id,
            "username": username,
            "created_at": time.time(),
            "expires_at": time.time() + (expires_in_hours * 3600)
        }
        
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Token to validate
            
        Returns:
            Token data or None if invalid
        """
        import time
        
        if token not in self.tokens:
            return None
        
        token_data = self.tokens[token]
        if time.time() > token_data["expires_at"]:
            del self.tokens[token]
            return None
        
        return token_data
    
    def revoke_token(self, token: str) -> bool:
        """Revoke token."""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """
        Remove expired tokens.
        
        Returns:
            Number of tokens removed
        """
        import time
        
        expired = [token for token, data in self.tokens.items()
                  if time.time() > data["expires_at"]]
        
        for token in expired:
            del self.tokens[token]
        
        return len(expired)

