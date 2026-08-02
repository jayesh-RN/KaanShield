"""
App Controller Module for KaanShield.
The central brain of KaanShield. Manages application state, coordinates drivers,
voice feedback engine, audio mixer, real-time Transparency audio passthrough, Software ANC DSP, and emits Qt Signals.
Supports smart toggle-off behavior for Transparency, Ambient, and ANC modes.
"""

import logging
import asyncio
import threading
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal, Qt

from core.config_manager import ConfigManager
from core.voice_engine import VoiceEngine
from core.audio_mixer import AudioMixer, AudioStream
from core.audio_passthrough import AudioPassthroughManager
from core.audio_anc_dsp import AudioAncDspManager
from drivers.base_driver import BaseHeadphoneDriver
from drivers.mock_driver import MockHeadphoneDriver
from drivers.generic_driver import GenericBluetoothDriver
from drivers.sony_driver import SonyHeadphoneDriver
from drivers.airpods_driver import AirPodsHeadphoneDriver
from drivers.galaxy_buds_driver import GalaxyBudsHeadphoneDriver
from core.bluetooth_manager import BluetoothManager

logger = logging.getLogger(__name__)


class AppController(QObject):
    """
    Central Controller for KaanShield.
    Holds single source of truth state and coordinates all engine modules.
    Supports smart toggle-off behavior for Transparency, Ambient, and ANC modes.
    """
    anc_mode_changed = Signal(str)          # payload: new_mode ('ANC_ON', 'TRANSPARENCY', 'ANC_OFF', 'AMBIENT')
    ambient_level_changed = Signal(int)     # payload: level (0-20)
    battery_updated = Signal(dict)         # payload: {'left': int, 'right': int, 'case': int}
    device_connected = Signal(str, dict)    # payload: device_name, capability_flags
    device_disconnected = Signal()
    mic_mute_toggled = Signal(bool)         # payload: is_muted
    audio_streams_updated = Signal(list)    # payload: list of AudioStream objects

    def __init__(self, config_manager: ConfigManager) -> None:
        super().__init__()
        self.config: ConfigManager = config_manager
        self.voice_engine: VoiceEngine = VoiceEngine(
            language=self.config.get("voice_language", "hindi_tapori"),
            enabled=self.config.get("voice_feedback_enabled", True)
        )
        self.audio_mixer: AudioMixer = AudioMixer()
        self.passthrough_manager: AudioPassthroughManager = AudioPassthroughManager()
        self.anc_dsp_manager: AudioAncDspManager = AudioAncDspManager()
        self.driver: BaseHeadphoneDriver = MockHeadphoneDriver()

        # State Variables
        self.current_anc_mode: str = self.config.get("anc_mode", "ANC_ON")
        self.ambient_level: int = self.config.get("ambient_level", 12)
        self.is_mic_muted: bool = False
        self.battery_state: Dict[str, int] = {"left": 85, "right": 85, "case": 100}

        # Initialize default driver
        self._select_driver(self.config.get("selected_device_name", "Virtual Headphone Simulator"))

    def _select_driver(self, device_name: str) -> None:
        name_lower = device_name.lower()
        if "virtual" in name_lower or "simulator" in name_lower:
            self.driver = MockHeadphoneDriver()
        elif "sony" in name_lower:
            self.driver = SonyHeadphoneDriver()
        elif "airpods" in name_lower:
            self.driver = AirPodsHeadphoneDriver()
        elif "galaxy" in name_lower or "buds" in name_lower:
            self.driver = GalaxyBudsHeadphoneDriver()
        else:
            self.driver = GenericBluetoothDriver(device_name=device_name)

        logger.info("Selected driver: %s for device: %s", self.driver.__class__.__name__, device_name)

    def connect_device_async(self, address: str = "00:11:22:33:44:55", name: str = "Virtual Headphone Simulator", speak_welcome: bool = False) -> None:
        """
        Thread-safe asynchronous connection handler.
        """
        def worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.connect_device(address, name, speak_welcome))
                loop.close()
            except Exception as e:
                logger.error("Error in connect_device_async worker: %s", e)

        threading.Thread(target=worker, daemon=True).start()

    async def connect_device(self, address: str = "00:11:22:33:44:55", name: str = "Virtual Headphone Simulator", speak_welcome: bool = True) -> bool:
        self._select_driver(name)
        success = await self.driver.connect(address)
        if success:
            self.config.set("selected_device_name", name)
            self.config.set("selected_device_address", address)

            try:
                self.battery_state = await self.driver.get_battery()
            except Exception as e:
                logger.warning("Failed to fetch battery state: %s", e)
                real_val = BluetoothManager.get_real_device_battery(name)
                self.battery_state = {"left": real_val, "right": real_val, "case": 100}

            self.battery_updated.emit(self.battery_state)

            if speak_welcome:
                self.voice_engine.trigger("CONNECTED", title="KAANSHIELD CONNECTED")

            self.device_connected.emit(self.driver.device_name, self.driver.CAPABILITIES)
            logger.info("Device connected successfully: %s with battery: %s", name, self.battery_state)

        return success

    def toggle_anc(self) -> str:
        if self.current_anc_mode == "ANC_ON":
            new_mode = "TRANSPARENCY"
        elif self.current_anc_mode == "TRANSPARENCY":
            new_mode = "ANC_OFF"
        else:
            new_mode = "ANC_ON"

        self.set_anc_mode(new_mode)
        return new_mode

    def set_anc_mode(self, mode: str) -> bool:
        if mode not in ("ANC_ON", "TRANSPARENCY", "ANC_OFF", "AMBIENT"):
            logger.error("Invalid mode: %s", mode)
            return False

        # Smart Toggle Off: If clicking currently active mode again, turn it OFF!
        if self.current_anc_mode == mode and mode != "ANC_OFF":
            logger.info("Toggling mode '%s' OFF -> switching to ANC_OFF", mode)
            mode = "ANC_OFF"

        self.current_anc_mode = mode
        self.config.set("anc_mode", mode)

        dev_name = self.config.get("selected_device_name", "Harmonics Twins 33")

        # Hardware & Software Mode Control
        if mode == "ANC_ON":
            self.passthrough_manager.stop_passthrough()
            self.anc_dsp_manager.enable_anc()
        elif mode in ("TRANSPARENCY", "AMBIENT"):
            self.anc_dsp_manager.disable_anc()
            self.passthrough_manager.start_passthrough(device_name=dev_name, ambient_level=self.ambient_level)
        else:
            # ANC_OFF mode cuts off both passthrough and DSP noise suppression!
            self.passthrough_manager.stop_passthrough()
            self.anc_dsp_manager.disable_anc()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.driver.set_anc_mode(mode))
            loop.close()
        except Exception as e:
            logger.debug("Driver ANC set notice: %s", e)

        self.voice_engine.trigger(mode, title="KAANSHIELD ANC")
        self.anc_mode_changed.emit(mode)
        logger.info("ANC mode set to: %s", mode)
        return True

    def set_ambient_level(self, level: int) -> None:
        self.ambient_level = max(0, min(20, level))
        self.config.set("ambient_level", self.ambient_level)

        if self.current_anc_mode in ("TRANSPARENCY", "AMBIENT"):
            self.passthrough_manager.set_gain_from_ambient_level(self.ambient_level)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.driver.set_ambient_level(self.ambient_level))
            loop.close()
        except Exception as e:
            logger.debug("Driver ambient set notice: %s", e)

        self.ambient_level_changed.emit(self.ambient_level)
        logger.info("Ambient level set to: %d", self.ambient_level)

    def toggle_global_mic_mute(self) -> bool:
        self.is_mic_muted = not self.is_mic_muted
        self.voice_engine.trigger("MIC_MUTED", title="KAANSHIELD MIC")
        self.mic_mute_toggled.emit(self.is_mic_muted)
        logger.info("Global mic mute toggled: %s", self.is_mic_muted)
        return self.is_mic_muted

    def set_voice_language(self, language: str) -> None:
        self.voice_engine.set_language(language)
        self.config.set("voice_language", language)
        logger.info("Language changed to: %s", language)

    def get_audio_playback_streams(self) -> List[AudioStream]:
        return self.audio_mixer.get_all_app_streams()

    def get_microphone_recording_streams(self) -> List[AudioStream]:
        return self.audio_mixer.get_all_app_streams()

    def get_all_app_streams(self) -> List[AudioStream]:
        """
        Fetches all active application streams for the mixer table.
        """
        return self.audio_mixer.get_all_app_streams()
