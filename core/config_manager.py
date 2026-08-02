"""
Configuration Manager Module for KaanShield.
Handles JSON persistence for application settings, device preferences, and hotkeys.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "product_name": "KaanShield",
    "selected_device_name": "Virtual Headphone Simulator",
    "selected_device_address": "00:11:22:33:44:55",
    "voice_language": "hindi_tapori",
    "voice_feedback_enabled": True,
    "hud_duration_ms": 4500,
    "hotkeys_enabled": True,
    "hotkey_anc_toggle": "<ctrl>+<alt>+a",
    "hotkey_mic_mute": "<ctrl>+<alt>+m",
    "anc_mode": "ANC_ON",
    "ambient_level": 12,
    "start_with_windows": True,
    "auto_detect_on_connect": True
}


class ConfigManager:
    """
    Manages persistent JSON configuration for KaanShield.
    """

    def __init__(self, config_path: Path = CONFIG_PATH) -> None:
        self.config_path: Path = config_path
        self._config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """
        Loads configuration from JSON file. Merges missing defaults.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._config.update(data)
                logger.info("Configuration loaded successfully from %s", self.config_path)
            except Exception as e:
                logger.error("Failed to load config from %s: %s. Using defaults.", self.config_path, e)
                self.save()
        else:
            logger.info("Config file not found. Creating default at %s", self.config_path)
            self.save()

    def save(self) -> None:
        """
        Saves current configuration dict to JSON file.
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration saved to %s", self.config_path)
        except Exception as e:
            logger.error("Failed to save config to %s: %s", self.config_path, e)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save()
