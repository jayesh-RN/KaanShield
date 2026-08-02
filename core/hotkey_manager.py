"""
Hotkey Manager Module for KaanShield.
Registers OS-level global keyboard shortcuts for instant ANC, Mic, Transparency, and ANC Off controls.
"""

import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput not available. Global hotkeys disabled.")


class HotkeyManager(QObject):
    """
    Listens for system-wide keyboard shortcuts in a background daemon thread.
    """
    anc_toggle_triggered = Signal()
    mic_mute_triggered = Signal()
    transparency_triggered = Signal()
    anc_off_triggered = Signal()

    def __init__(
        self,
        anc_hotkey: str = "<ctrl>+<alt>+a",
        mic_hotkey: str = "<ctrl>+<alt>+m",
        transparency_hotkey: str = "<ctrl>+<alt>+t",
        anc_off_hotkey: str = "<ctrl>+<alt>+o"
    ) -> None:
        super().__init__()
        self.anc_hotkey: str = anc_hotkey
        self.mic_hotkey: str = mic_hotkey
        self.transparency_hotkey: str = transparency_hotkey
        self.anc_off_hotkey: str = anc_off_hotkey
        self._listener: Optional[Any] = None
        self.is_running: bool = False

    def start(self) -> bool:
        if not PYNPUT_AVAILABLE:
            logger.warning("Cannot start HotkeyManager: pynput is missing.")
            return False

        try:
            hotkeys_dict = {
                self.anc_hotkey: lambda: self.anc_toggle_triggered.emit(),
                self.mic_hotkey: lambda: self.mic_mute_triggered.emit(),
                self.transparency_hotkey: lambda: self.transparency_triggered.emit(),
                self.anc_off_hotkey: lambda: self.anc_off_triggered.emit(),
            }
            self._listener = keyboard.GlobalHotKeys(hotkeys_dict)
            self._listener.start()
            self.is_running = True
            logger.info("HotkeyManager started with 4 global shortcuts.")
            return True
        except Exception as e:
            logger.error("Failed to start HotkeyManager: %s", e)
            return False

    def stop(self) -> None:
        if self._listener and self.is_running:
            try:
                self._listener.stop()
                self.is_running = False
                logger.info("HotkeyManager stopped.")
            except Exception as e:
                logger.error("Error stopping HotkeyManager: %s", e)
