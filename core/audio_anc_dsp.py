"""
Audio ANC DSP Module for KaanShield.
Provides Software Active Noise Cancellation (DSP Frequency Equalization & Background Hiss Suppression)
for universal Bluetooth headphones (boAt, Noise, Zebronics, Harmonics Twins, pTron, etc.).
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class AudioAncDspManager:
    """
    Manages Software Active Noise Cancellation (DSP Noise Suppression) for universal Bluetooth headphones.
    """

    def __init__(self) -> None:
        self.is_anc_active: bool = False

    def enable_anc(self) -> bool:
        """
        Enables Software ANC (DSP Background Hiss & Hum Suppression).
        """
        self.is_anc_active = True
        logger.info("Software Active Noise Cancellation (DSP Noise Suppression) ENABLED.")
        return True

    def disable_anc(self) -> None:
        """
        Disables Software ANC.
        """
        self.is_anc_active = False
        logger.info("Software Active Noise Cancellation (DSP Noise Suppression) DISABLED.")

    def process_audio_chunk(self, chunk: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        """
        Applies real-time FFT frequency equalizer filter to attenuate low hums (50Hz-250Hz) and high hiss.
        """
        if not self.is_anc_active or len(chunk) == 0:
            return chunk

        try:
            fft_data = np.fft.rfft(chunk)
            freqs = np.fft.rfftfreq(len(chunk), 1.0 / sample_rate)

            # Attenuation mask for background hum & hiss frequencies
            mask = np.ones(len(freqs))
            mask[freqs < 200] *= 0.35
            mask[freqs > 8000] *= 0.40

            filtered_fft = fft_data * mask
            return np.fft.irfft(filtered_fft, n=len(chunk))
        except Exception as e:
            logger.error("Error in ANC DSP filter processing: %s", e)
            return chunk
