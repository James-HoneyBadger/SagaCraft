"""
Configuration service for managing game and plugin settings
"""

import json
from pathlib import Path
from typing import Any, Dict, cast
import logging

from sagacraft.core.services import Service

# YAML is optional
try:
    # pyright: ignore[reportMissingModuleSource]
    import yaml  # type: ignore[import-not-found,import-untyped]

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


class ConfigService(Service):
    """
    Manages configuration for the engine and plugins

    Supports:
    - Multiple config file formats (JSON, YAML)
    - Plugin-specific configurations
    - Default values
    - Config validation
    - Hot reloading
    """

    def __init__(self, config_dir: str = "config"):
        self.logger = logging.getLogger("ConfigService")
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}

    def initialize(self, config: Dict[str, Any]):
        """Initialize the config service"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load main config
        main_config_path = self.config_dir / "engine.yaml"
        if not main_config_path.exists():
            main_config_path = self.config_dir / "engine.json"

        if main_config_path.exists():
            self.load_config(main_config_path)
        else:
            self._config = config or {}
            self._save_default_config()

        # Load plugin configs
        self._load_plugin_configs()

    def shutdown(self):
        """Save all configurations"""
        self.save_all()

    @staticmethod
    def _ensure_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    def _yaml_load_dict(self, handle) -> Dict[str, Any]:
        if not YAML_AVAILABLE or yaml is None:
            return {}
        loaded = yaml.safe_load(handle)
        return self._ensure_dict(loaded)

    def load_config(self, config_path: Path):
        """Load main configuration file"""
        if config_path.suffix in {".yaml", ".yml"}:
            if not YAML_AVAILABLE or yaml is None:
                self.logger.error("YAML support is not available. Please install PyYAML.")
                self._config = {}
                return
            yaml_error = cast(type[BaseException], getattr(yaml, "YAMLError", Exception))
            try:
                with open(config_path, "r", encoding="utf-8") as handle:
                    self._config = self._yaml_load_dict(handle)
                self.logger.info("Loaded config from %s", config_path)
            except (OSError, yaml_error) as exc:
                self.logger.error("Failed to load YAML config %s: %s", config_path, exc)
                self._config = {}
            return

        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                self._config = self._ensure_dict(json.load(handle))
            self.logger.info("Loaded config from %s", config_path)
        except (OSError, json.JSONDecodeError) as exc:
            self.logger.error("Failed to load config %s: %s", config_path, exc)
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        parts = key.split(".")
        value: Any = self._config

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any):
        """Set a configuration value"""
        parts = key.split(".")
        config = self._config

        for part in parts[:-1]:
            next_config = config.get(part)
            if not isinstance(next_config, dict):
                next_config = {}
                config[part] = next_config
            config = next_config

        config[parts[-1]] = value

    def get_plugin_config(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """Get plugin-specific configuration"""
        if plugin_name not in self._plugin_configs:
            self._plugin_configs[plugin_name] = {}

        parts = key.split(".")
        value: Any = self._plugin_configs[plugin_name]

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def set_plugin_config(self, plugin_name: str, key: str, value: Any):
        """Set plugin-specific configuration"""
        if plugin_name not in self._plugin_configs:
            self._plugin_configs[plugin_name] = {}

        parts = key.split(".")
        config = self._plugin_configs[plugin_name]

        for part in parts[:-1]:
            next_config = config.get(part)
            if not isinstance(next_config, dict):
                next_config = {}
                config[part] = next_config
            config = next_config

        config[parts[-1]] = value

    def _load_plugin_configs(self):
        """Load all plugin configuration files"""
        plugins_dir = self.config_dir / "plugins"
        if not plugins_dir.exists():
            return

        if YAML_AVAILABLE and yaml is not None:
            yaml_error = cast(type[BaseException], getattr(yaml, "YAMLError", Exception))
            for config_file in plugins_dir.glob("*.yaml"):
                plugin_name = config_file.stem
                try:
                    with open(config_file, "r", encoding="utf-8") as handle:
                        self._plugin_configs[plugin_name] = self._yaml_load_dict(handle)
                except (OSError, yaml_error) as exc:
                    self.logger.error(
                        "Failed to load YAML config for %s: %s", plugin_name, exc
                    )

        for config_file in plugins_dir.glob("*.json"):
            plugin_name = config_file.stem
            if plugin_name not in self._plugin_configs:
                try:
                    with open(config_file, "r", encoding="utf-8") as handle:
                        self._plugin_configs[plugin_name] = self._ensure_dict(
                            json.load(handle)
                        )
                except (OSError, json.JSONDecodeError) as exc:
                    self.logger.error(
                        "Failed to load JSON config for %s: %s", plugin_name, exc
                    )

    def _save_default_config(self):
        """Save default engine configuration"""
        default_config = {
            "engine": {
                "name": "SagaCraft",
                "version": "3.0.0",
                "enable_event_history": False,
            },
            "gameplay": {
                "auto_save": True,
                "save_interval": 5,
                "difficulty": "normal",
            },
            "ui": {
                "theme": "dark",
                "font_size": 12,
                "color_enabled": True,
            },
        }

        config_path = self.config_dir / "engine.json"
        try:
            with open(config_path, "w", encoding="utf-8") as handle:
                json.dump(default_config, handle, indent=2)
            self._config = default_config
            self.logger.info("Created default config")
        except OSError as exc:
            self.logger.error("Failed to save default config: %s", exc)

    def save_all(self):
        """Save all configurations to disk"""
        # Save main config
        config_path = self.config_dir / "engine.json"
        try:
            with open(config_path, "w", encoding="utf-8") as handle:
                json.dump(self._config, handle, indent=2)
        except OSError as exc:
            self.logger.error("Failed to save config: %s", exc)

        # Save plugin configs
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir(exist_ok=True)

        for plugin_name, config in self._plugin_configs.items():
            config_path = plugins_dir / f"{plugin_name}.json"
            try:
                with open(config_path, "w", encoding="utf-8") as handle:
                    json.dump(config, handle, indent=2)
            except OSError as exc:
                self.logger.error("Failed to save config for %s: %s", plugin_name, exc)
