"""
Configuration management for PortPilot.
"""

import json
from pathlib import Path
from typing import Any


class Config:
    """
    Application configuration manager.

    Handles loading/saving user preferences and app settings.
    """

    DEFAULT_CONFIG = {
        "refresh_interval": 5000,  # ms
        "dark_mode": True,
        "start_minimized": False,
        "auto_start": False,
        "show_notifications": True,
        "port_filters": {
            "http": [80, 443, 8080, 8443],
            "dev": [3000, 5000, 8000, 5173, 5174],
            "db": [5432, 3306, 27017, 6379]
        }
    }

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".portpilot" / "config.json"
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self._config = json.load(f)
            except (OSError, json.JSONDecodeError):
                self._config = {}

        # Merge with defaults
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value

    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        self.save()

    def reset(self) -> None:
        """Reset to default configuration."""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
