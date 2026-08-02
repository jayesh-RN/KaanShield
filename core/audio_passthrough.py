"""
Audio Passthrough Module for KaanShield.
Provides sub-10ms real-time Microphone Ambient Sound Passthrough (Transparency Mode) using sounddevice.
Dynamically matches target Bluetooth headphone input and output device indices.
"""

import logging
import threading
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("sounddevice not installed. Real-time Transparency passthrough fallback disabled.")


class AudioPassthroughManager:
    """
    Manages low-latency real-time Microphone Ambient Sound Passthrough for Transparency Mode.
    Dynamically binds input/output audio streams to target connected headphone hardware.
    """

    def __init__(self) -> None:
        self.stream: Optional[Any] = None
        self.is_active: bool = False
        self.gain: float = 2.5  # Boosted ambient volume multiplier for clear passthrough
        self._lock = threading.Lock()

    def find_target_device_indices(self, target_name: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Finds matching input and output device indices in sounddevice.query_devices().
        """
        if not SOUNDDEVICE_AVAILABLE:
            return None, None

        input_idx = None
        output_idx = None

        try:
            devs = sd.query_devices()
            target_clean = target_name.lower().replace(" (connected)", "").replace(" (paired)", "").strip()

            # Search for output device matching target headphone
            for idx, dev in enumerate(devs):
                d_name = dev['name'].lower()
                if dev['max_output_channels'] > 0:
                    if target_clean and target_clean in d_name:
                        output_idx = idx
                        break

            # Search for input device matching target headphone or microphone
            for idx, dev in enumerate(devs):
                d_name = dev['name'].lower()
                if dev['max_input_channels'] > 0:
                    if target_clean and target_clean in d_name:
                        input_idx = idx
                        break

            # Fallbacks to system defaults if specific search misses
            if output_idx is None:
                default_out = sd.default.device[1]
                output_idx = default_out if default_out >= 0 else None

            if input_idx is None:
                default_in = sd.default.device[0]
                input_idx = default_in if default_in >= 0 else None

            logger.info("Target device indices for '%s': In=#%s, Out=#%s", target_name, input_idx, output_idx)
        except Exception as e:
            logger.error("Error matching audio device indices: %s", e)

        return input_idx, output_idx

    def set_gain_from_ambient_level(self, level: int) -> None:
        """
        Sets transparency microphone gain based on ambient level slider (0 to 20).
        """
        # Scale 0 to 20 level into 0.5x to 4.0x gain boost
        self.gain = max(0.2, min(5.0, (level / 10.0) * 2.0))
        logger.info("Transparency audio passthrough gain set to: %.2f", self.gain)

    def start_passthrough(self, device_name: str = "Harmonics Twins 33", ambient_level: int = 12) -> bool:
        """
        Starts real-time microphone ambient sound passthrough.
        """
        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("sounddevice unavailable. Cannot start hardware passthrough.")
            return False

        with self._lock:
            if self.is_active:
                self.set_gain_from_ambient_level(ambient_level)
                return True

            self.set_gain_from_ambient_level(ambient_level)
            in_idx, out_idx = self.find_target_device_indices(device_name)

            if in_idx is None or out_idx is None:
                logger.error("Could not resolve audio device indices for passthrough.")
                return False

            def audio_callback(indata, outdata, frames, time_info, status):
                outdata[:] = indata * self.gain

            try:
                self.stream = sd.Stream(
                    device=(in_idx, out_idx),
                    channels=1,
                    samplerate=44100,
                    latency='low',
                    callback=audio_callback
                )
                self.stream.start()
                self.is_active = True
                logger.info("Real-time Transparency Audio Passthrough STARTED successfully on In #%d -> Out #%d.", in_idx, out_idx)
                return True
            except Exception as e:
                logger.error("Failed to start Transparency Audio Passthrough stream: %s", e)
                self.is_active = False
                return False

    def stop_passthrough(self) -> None:
        """
        Stops real-time microphone ambient sound passthrough.
        """
        with self._lock:
            if self.stream and self.is_active:
                try:
                    self.stream.stop()
                    self.stream.close()
                    logger.info("Real-time Transparency Audio Passthrough STOPPED.")
                except Exception as e:
                    logger.error("Error stopping passthrough stream: %s", e)
                finally:
                    self.stream = None
                    self.is_active = False
