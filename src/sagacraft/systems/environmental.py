"""Environmental Hazards System - dynamic weather, traps, and destructible objects."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set


class WeatherType(Enum):
    """Weather types in the game."""
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    SANDSTORM = "sandstorm"
    FOG = "fog"


class HazardType(Enum):
    """Types of environmental hazards."""
    TRAP = "trap"
    HAZARD_FIELD = "hazard_field"
    COLLAPSING_STRUCTURE = "collapsing_structure"
    FALLING_DEBRIS = "falling_debris"
    FIRE = "fire"
    ICE = "ice"
    POISON = "poison"


class HazardTrigger(Enum):
    """How a hazard is triggered."""
    PROXIMITY = "proximity"
    INTERACTION = "interaction"
    TIME_BASED = "time_based"
    RANDOM = "random"
    TRIGGERED_BY_PLAYER = "triggered_by_player"


@dataclass
class WeatherEffect:
    """Effects of weather on gameplay."""
    weather_type: WeatherType
    visibility_penalty: float = 0.0  # 0-1, affects spotting
    movement_penalty: float = 0.0  # 0-1, affects speed
    damage_per_turn: int = 0  # Environmental damage
    heal_per_turn: int = 0  # Environmental healing (rare)
    accuracy_penalty: float = 0.0
    description: str = ""


@dataclass
class EnvironmentalHazard:
    """An environmental hazard in a location."""
    id: str
    name: str
    hazard_type: HazardType
    trigger_type: HazardTrigger
    damage: int = 0
    trigger_radius: float = 1.0
    cooldown_turns: int = 0
    can_be_disabled: bool = False
    disarm_difficulty: int = 0  # 1-5 for difficulty
    active: bool = True
    description: str = ""


@dataclass
class DestructibleObject:
    """An object that can be destroyed."""
    id: str
    name: str
    location_id: str
    health: int
    max_health: int
    destroyed: bool = False
    drops_loot: List[str] = field(default_factory=list)
    blocking: bool = True  # Blocks player movement


@dataclass
class EnvironmentState:
    """Current state of an environment/location."""
    location_id: str
    current_weather: WeatherType = WeatherType.CLEAR
    weather_turns_remaining: int = 0
    active_hazards: Set[str] = field(default_factory=set)
    destructible_objects: Dict[str, DestructibleObject] = field(default_factory=dict)
    hazard_cooldowns: Dict[str, int] = field(default_factory=dict)


class EnvironmentalSystem:
    """Manages environmental hazards and weather."""

    def __init__(self):
        self.weather_effects: Dict[WeatherType, WeatherEffect] = {}
        self.hazards: Dict[str, EnvironmentalHazard] = {}
        self.environment_states: Dict[str, EnvironmentState] = {}
        self._init_weather()
        self._init_hazards()

    def _init_weather(self) -> None:
        """Initialize weather effects."""
        self.weather_effects[WeatherType.CLEAR] = WeatherEffect(
            weather_type=WeatherType.CLEAR,
            description="Perfect weather. No penalties.",
        )

        self.weather_effects[WeatherType.RAIN] = WeatherEffect(
            weather_type=WeatherType.RAIN,
            movement_penalty=0.1,
            accuracy_penalty=0.1,
            description="Rain reduces visibility and movement speed.",
        )

        self.weather_effects[WeatherType.STORM] = WeatherEffect(
            weather_type=WeatherType.STORM,
            visibility_penalty=0.4,
            movement_penalty=0.2,
            accuracy_penalty=0.2,
            damage_per_turn=10,
            description="Severe storm! Lightning strikes deal damage.",
        )

        self.weather_effects[WeatherType.SNOW] = WeatherEffect(
            weather_type=WeatherType.SNOW,
            movement_penalty=0.15,
            damage_per_turn=5,
            description="Snow slows movement and causes cold damage.",
        )

        self.weather_effects[WeatherType.SANDSTORM] = WeatherEffect(
            weather_type=WeatherType.SANDSTORM,
            visibility_penalty=0.5,
            accuracy_penalty=0.3,
            damage_per_turn=8,
            description="Sandstorm reduces visibility and damages eyes.",
        )

        self.weather_effects[WeatherType.FOG] = WeatherEffect(
            weather_type=WeatherType.FOG,
            visibility_penalty=0.6,
            accuracy_penalty=0.25,
            description="Thick fog makes navigation difficult.",
        )

    def _init_hazards(self) -> None:
        """Initialize common hazards."""
        # Floor spikes trap
        self.hazards["spike_trap"] = EnvironmentalHazard(
            id="spike_trap",
            name="Spike Trap",
            hazard_type=HazardType.TRAP,
            trigger_type=HazardTrigger.PROXIMITY,
            damage=15,
            trigger_radius=1.0,
            cooldown_turns=5,
            can_be_disabled=True,
            disarm_difficulty=2,
            description="Sharp spikes emerge from the ground.",
        )

        # Poison cloud
        self.hazards["poison_cloud"] = EnvironmentalHazard(
            id="poison_cloud",
            name="Poison Cloud",
            hazard_type=HazardType.HAZARD_FIELD,
            trigger_type=HazardTrigger.PROXIMITY,
            damage=8,
            trigger_radius=2.0,
            cooldown_turns=0,
            description="Noxious green cloud lingers in the area.",
        )

        # Fire hazard
        self.hazards["fire_hazard"] = EnvironmentalHazard(
            id="fire_hazard",
            name="Fire Pit",
            hazard_type=HazardType.FIRE,
            trigger_type=HazardTrigger.PROXIMITY,
            damage=20,
            trigger_radius=1.5,
            cooldown_turns=3,
            description="Blazing fire consumes the area.",
        )

        # Crumbling ceiling
        self.hazards["crumbling_ceiling"] = EnvironmentalHazard(
            id="crumbling_ceiling",
            name="Crumbling Ceiling",
            hazard_type=HazardType.FALLING_DEBRIS,
            trigger_type=HazardTrigger.RANDOM,
            damage=25,
            trigger_radius=3.0,
            cooldown_turns=4,
            description="Chunks of ceiling fall down without warning.",
        )

    def get_environment(self, location_id: str) -> EnvironmentState:
        """Get or create environment state for a location."""
        if location_id not in self.environment_states:
            self.environment_states[location_id] = EnvironmentState(location_id=location_id)
        return self.environment_states[location_id]

    def change_weather(self, location_id: str, weather_type: WeatherType, duration_turns: int) -> str:
        """Change the weather in a location."""
        env = self.get_environment(location_id)
        env.current_weather = weather_type
        env.weather_turns_remaining = duration_turns

        effect = self.weather_effects.get(weather_type)
        return f"Weather changed to {weather_type.value}. {effect.description if effect else ''}"

    def update_weather(self, location_id: str) -> None:
        """Update weather state (call each turn)."""
        env = self.get_environment(location_id)
        if env.weather_turns_remaining > 0:
            env.weather_turns_remaining -= 1
            if env.weather_turns_remaining == 0:
                env.current_weather = WeatherType.CLEAR

    def add_hazard(self, location_id: str, hazard_id: str) -> Tuple[bool, str]:
        """Add a hazard to a location."""
        if hazard_id not in self.hazards:
            return False, "Hazard not found"

        env = self.get_environment(location_id)
        env.active_hazards.add(hazard_id)
        env.hazard_cooldowns[hazard_id] = 0

        hazard = self.hazards[hazard_id]
        return True, f"Hazard '{hazard.name}' activated in this area!"

    def trigger_hazard(
        self, location_id: str, hazard_id: str, player_level: int = 1
    ) -> Tuple[int, str]:
        """Check if a hazard triggers and deal damage."""
        env = self.get_environment(location_id)
        if hazard_id not in env.active_hazards:
            return 0, "Hazard not active"

        hazard = self.hazards[hazard_id]

        # Check cooldown
        if env.hazard_cooldowns.get(hazard_id, 0) > 0:
            return 0, "Hazard on cooldown"

        # Damage affected by player level
        damage = max(1, hazard.damage - (player_level // 5))

        if hazard.cooldown_turns > 0:
            env.hazard_cooldowns[hazard_id] = hazard.cooldown_turns

        return damage, f"Hit by {hazard.name}! Takes {damage} damage."

    def disarm_hazard(self, location_id: str, hazard_id: str, player_level: int = 1) -> Tuple[bool, str]:
        """Attempt to disarm a hazard."""
        env = self.get_environment(location_id)
        if hazard_id not in env.active_hazards:
            return False, "Hazard not active"

        hazard = self.hazards[hazard_id]
        if not hazard.can_be_disabled:
            return False, f"{hazard.name} cannot be disarmed"

        # Check if player level is high enough
        if player_level < hazard.disarm_difficulty * 5:
            return False, f"Too difficult to disarm (need level {hazard.disarm_difficulty * 5})"

        env.active_hazards.discard(hazard_id)
        return True, f"Successfully disarmed {hazard.name}"

    def add_destructible(
        self, location_id: str, obj_id: str, name: str, health: int, drops: List[str] = None
    ) -> None:
        """Add a destructible object to a location."""
        env = self.get_environment(location_id)
        obj = DestructibleObject(
            id=obj_id,
            name=name,
            location_id=location_id,
            health=health,
            max_health=health,
            drops_loot=drops or [],
        )
        env.destructible_objects[obj_id] = obj

    def damage_object(self, location_id: str, obj_id: str, damage: int) -> Tuple[bool, List[str]]:
        """Deal damage to a destructible object."""
        env = self.get_environment(location_id)
        if obj_id not in env.destructible_objects:
            return False, []

        obj = env.destructible_objects[obj_id]
        if obj.destroyed:
            return False, []

        obj.health -= damage
        drops = []

        if obj.health <= 0:
            obj.destroyed = True
            drops = obj.drops_loot

        return True, drops

    def get_weather_effects(self, location_id: str) -> WeatherEffect:
        """Get current weather effects for a location."""
        env = self.get_environment(location_id)
        return self.weather_effects.get(env.current_weather, self.weather_effects[WeatherType.CLEAR])

    def get_location_hazards(self, location_id: str) -> List[EnvironmentalHazard]:
        """Get all active hazards in a location."""
        env = self.get_environment(location_id)
        return [self.hazards[hid] for hid in env.active_hazards if hid in self.hazards]

    def update_location(self, location_id: str) -> None:
        """Update all environmental state for a location (call each turn)."""
        env = self.get_environment(location_id)

        # Update weather
        self.update_weather(location_id)

        # Decrement hazard cooldowns
        for hazard_id in env.hazard_cooldowns:
            if env.hazard_cooldowns[hazard_id] > 0:
                env.hazard_cooldowns[hazard_id] -= 1
