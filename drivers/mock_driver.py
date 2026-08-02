"""
Mock Driver Module for KaanShield.
Virtual headphone simulator for instant development and testing on any computer.
"""

import asyncio
import logging
from typing import Callable, Dict, Any, Optional
from drivers.base_driver import BaseHeadphoneDriver

logger = logging.getLogger(__name__)


class MockHeadphoneDriver(BaseHeadphoneDriver):
    """
    Virtual headphone simulator driver.
    Simulates a fully-featured premium ANC headphone with full battery reporting.
    """

    CAPABILITIES: Dict[str, bool] = {
        "anc_control": True,
        "ambient_sound_slider": True,
        "battery_monitor": True,
        "audio_mixer": True,
        "mic_control": True,
    }

    def __init__(self) -> None:
        super().__init__()
        self.device_name = "Virtual Headphone Simulator"
        self.current_mode = "ANC_ON"
        self.ambient_level = 10
        self.battery_state = {"left": 90, "right": 85, "case": 70}
        self._notification_callback: Optional[Callable[[Dict[str, Any]], None]] = None

    async def connect(self, address: str = "00:11:22:33:44:55") -> bool:
        self.device_address = address
        self.is_connected = True
        logger.info("MockDriver connected to virtual device address: %s", address)
        return True

    async def disconnect(self) -> None:
        self.is_connected = False
        logger.info("MockDriver disconnected cleanly.")

    async def set_anc_mode(self, mode: str) -> bool:
        if mode not in ("ANC_ON", "TRANSPARENCY", "ANC_OFF"):
            logger.error("Invalid ANC mode specified: %s", mode)
            return False

        self.current_mode = mode
        logger.info("MockDriver set ANC mode to: %s", mode)

        if self._notification_callback:
            self._notification_callback({"event": "anc_mode_changed", "mode": mode})

        return True

    async def set_ambient_level(self, level: int) -> bool:
        self.ambient_level = max(0, min(20, level))
        logger.info("MockDriver set ambient sound level to: %d", self.ambient_level)
        return True

    async def get_battery(self) -> Dict[str, int]:
        return self.battery_state.copy()

    async def start_notifications(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._notification_callback = callback
        logger.info("MockDriver notification callback registered.")
