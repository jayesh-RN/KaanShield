"""
Base Driver Module for KaanShield.
Defines the abstract interface that all headphone drivers (Sony, AirPods, Galaxy Buds, Generic, Mock) must implement.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional


class BaseHeadphoneDriver(ABC):
    """
    Abstract Base Class for all KaanShield headphone drivers.
    Enforces CapabilityFlags and standard control interface across all brands.
    """

    CAPABILITIES: Dict[str, bool] = {
        "anc_control": True,
        "ambient_sound_slider": True,
        "battery_monitor": True,
        "audio_mixer": True,
        "mic_control": True,
    }

    def __init__(self) -> None:
        self.is_connected: bool = False
        self.device_name: str = "Unknown Device"
        self.device_address: Optional[str] = None

    @abstractmethod
    async def connect(self, address: str) -> bool:
        """
        Establishes Bluetooth connection to the target device address.
        Returns True if connection succeeded, False otherwise.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Cleanly closes Bluetooth connection handles.
        """
        pass

    @abstractmethod
    async def set_anc_mode(self, mode: str) -> bool:
        """
        Sets Active Noise Cancellation mode.
        mode: 'ANC_ON' | 'TRANSPARENCY' | 'ANC_OFF'
        Returns True if command succeeded.
        """
        pass

    @abstractmethod
    async def set_ambient_level(self, level: int) -> bool:
        """
        Sets transparency ambient sound level (0 to 20).
        """
        pass

    @abstractmethod
    async def get_battery(self) -> Dict[str, int]:
        """
        Returns battery dictionary: {'left': int, 'right': int, 'case': int}
        """
        pass

    @abstractmethod
    async def start_notifications(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribes to incoming device state change notifications.
        callback receive dict payload containing updated status.
        """
        pass
