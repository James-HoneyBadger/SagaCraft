"""Centralized system configuration and registry - enables easy system management."""

from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum

from sagacraft.core.system_base import (
    GameSystem,
    SystemConfig,
    SystemType,
    SystemFactory,
)


@dataclass
class FeatureFlag:
    """Feature flag for enabling/disabling systems."""
    name: str
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemRegistry:
    """
    Centralized registry for managing all game systems.
    Single point of truth for system state and configuration.
    """

    def __init__(self):
        self.factory = SystemFactory()
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.system_configs: Dict[str, SystemConfig] = {}
        self.system_dependencies: Dict[str, List[str]] = {}
        self._initialized = False

    def register_system_class(self, system_id: str, system_class: Type[GameSystem]) -> None:
        """Register a system class for later instantiation."""
        self.factory.register(system_id, system_class)

    def define_system(
        self,
        system_id: str,
        system_type: SystemType,
        enabled: bool = True,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Define a system configuration."""
        config = SystemConfig(
            system_id=system_id,
            system_type=system_type,
            enabled=enabled,
            priority=priority,
            metadata=metadata or {},
        )
        self.system_configs[system_id] = config
        self.system_dependencies[system_id] = dependencies or []

        # Create feature flag
        self.feature_flags[system_id] = FeatureFlag(name=system_id, enabled=enabled)

    def enable_system(self, system_id: str) -> None:
        """Enable a system."""
        if system_id in self.feature_flags:
            self.feature_flags[system_id].enabled = True
            if system := self.factory.get(system_id):
                system.enable()

    def disable_system(self, system_id: str) -> None:
        """Disable a system."""
        if system_id in self.feature_flags:
            self.feature_flags[system_id].enabled = False
            if system := self.factory.get(system_id):
                system.disable()

    def is_enabled(self, system_id: str) -> bool:
        """Check if system is enabled."""
        flag = self.feature_flags.get(system_id)
        return flag.enabled if flag else False

    def create_system(self, system_id: str) -> Optional[GameSystem]:
        """Create and register a system instance."""
        if system_id not in self.system_configs:
            raise ValueError(f"System {system_id} not configured")

        config = self.system_configs[system_id]
        return self.factory.create(system_id, config)

    def initialize_all(self, system_ids: Optional[List[str]] = None) -> None:
        """Initialize all or specific systems in dependency order."""
        systems_to_init = system_ids or list(self.system_configs.keys())

        # Sort by priority (higher first)
        systems_to_init.sort(
            key=lambda sid: self.system_configs[sid].priority,
            reverse=True
        )

        for system_id in systems_to_init:
            if not self.is_enabled(system_id):
                continue

            # Check dependencies
            deps = self.system_dependencies.get(system_id, [])
            for dep in deps:
                if dep not in self.factory.systems:
                    raise RuntimeError(f"Dependency {dep} not initialized for {system_id}")

            # Create if not exists
            if self.factory.get(system_id) is None:
                self.create_system(system_id)

        self._initialized = True

    def shutdown_all(self) -> None:
        """Shutdown all systems."""
        self.factory.shutdown_all()
        self._initialized = False

    def get_system(self, system_id: str) -> Optional[GameSystem]:
        """Get a system instance."""
        return self.factory.get(system_id)

    def get_systems_by_type(self, system_type: SystemType) -> List[GameSystem]:
        """Get all systems of a specific type."""
        return self.factory.get_by_type(system_type)

    def get_all_systems(self) -> Dict[str, GameSystem]:
        """Get all systems."""
        return self.factory.get_all()

    def validate_dependencies(self, system_id: str) -> bool:
        """Validate that all dependencies are initialized."""
        deps = self.system_dependencies.get(system_id, [])
        for dep in deps:
            if self.factory.get(dep) is None:
                return False
        return True


# Global registry instance
_global_registry: Optional[SystemRegistry] = None


def get_registry() -> SystemRegistry:
    """Get or create global system registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SystemRegistry()
    return _global_registry


def setup_default_systems() -> SystemRegistry:
    """Setup default game systems configuration."""
    registry = get_registry()

    # Core progression systems
    registry.define_system("difficulty", SystemType.GAMEPLAY, priority=100)
    registry.define_system("progression", SystemType.PROGRESSION, priority=90)
    registry.define_system("skill_trees", SystemType.PROGRESSION, priority=85, dependencies=["progression"])
    registry.define_system("battle_pass", SystemType.PROGRESSION, priority=80, dependencies=["progression"])
    registry.define_system("prestige", SystemType.PROGRESSION, priority=75, dependencies=["progression"])

    # Gameplay systems
    registry.define_system("game_modes", SystemType.GAMEPLAY, priority=70)
    registry.define_system("crafting", SystemType.GAMEPLAY, priority=65)
    registry.define_system("environmental", SystemType.GAMEPLAY, priority=60)
    registry.define_system("dungeon_scaling", SystemType.GAMEPLAY, priority=55)

    # Social systems
    registry.define_system("guilds", SystemType.SOCIAL, priority=50)
    registry.define_system("economy", SystemType.SOCIAL, priority=45)
    registry.define_system("mentorship", SystemType.SOCIAL, priority=40)
    registry.define_system("pvp_arenas", SystemType.SOCIAL, priority=35)

    # Content systems
    registry.define_system("daily_challenges", SystemType.CONTENT, priority=30)
    registry.define_system("seasonal", SystemType.CONTENT, priority=25)
    registry.define_system("cosmetics", SystemType.CONTENT, priority=20)
    registry.define_system("achievements", SystemType.CONTENT, priority=15, dependencies=["progression"])

    # Infrastructure systems
    registry.define_system("cloud_saves", SystemType.INFRASTRUCTURE, priority=10)
    registry.define_system("analytics", SystemType.INFRASTRUCTURE, priority=5)

    return registry


class SystemValidator:
    """Validates system configurations and state."""

    @staticmethod
    def validate_system_id(system_id: str) -> bool:
        """Validate system ID format."""
        return bool(system_id) and system_id.replace("_", "").isalnum()

    @staticmethod
    def validate_priority(priority: int) -> bool:
        """Validate priority value."""
        return 0 <= priority <= 1000

    @staticmethod
    def validate_configuration(registry: SystemRegistry, system_id: str) -> tuple[bool, str]:
        """Validate system configuration."""
        if system_id not in registry.system_configs:
            return False, f"System {system_id} not configured"

        config = registry.system_configs[system_id]

        if not SystemValidator.validate_system_id(system_id):
            return False, f"Invalid system ID: {system_id}"

        if not SystemValidator.validate_priority(config.priority):
            return False, f"Invalid priority: {config.priority}"

        # Check dependencies exist
        for dep in registry.system_dependencies.get(system_id, []):
            if dep not in registry.system_configs:
                return False, f"Dependency {dep} not configured"

        return True, "Configuration valid"

    @staticmethod
    def validate_all(registry: SystemRegistry) -> tuple[bool, List[str]]:
        """Validate entire registry configuration."""
        errors = []

        for system_id in registry.system_configs:
            valid, msg = SystemValidator.validate_configuration(registry, system_id)
            if not valid:
                errors.append(msg)

        return len(errors) == 0, errors
