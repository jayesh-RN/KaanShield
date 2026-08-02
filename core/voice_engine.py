"""
Voice Engine Module for KaanShield.
Supports custom user-recorded MP3 voice audio files, gTTS, and local TTS.
Re-binds audio playback handles dynamically to target connected Bluetooth headphone output.
Includes COM initialization for Windows background threads.
"""

import os
import sys
import hashlib
import logging
import queue
import threading
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal

from core.path_utils import get_resource_path

logger = logging.getLogger(__name__)

IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    try:
        import pythoncom
        PYTHONCOM_AVAILABLE = True
    except ImportError:
        PYTHONCOM_AVAILABLE = False
else:
    PYTHONCOM_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

SOUNDS_DIR = Path(get_resource_path("assets/sounds"))
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

LANG_CODE_MAP: Dict[str, str] = {
    "hindi_tapori": "hi",
    "english": "en"
}

VOICE_LINES: Dict[str, Dict[str, str]] = {
    "hindi_tapori": {
        "ANC_ON": "अबे शोर बंद! फुल शांति!",
        "TRANSPARENCY": "दुनिया की बात सुनने का है भइया!",
        "ANC_OFF": "नॉर्मल मोड चालू हो गया बॉस!",
        "MIC_MUTED": "माइक चुप! मुंह पे ताला!",
        "CONNECTED": "हेडफोन कनेक्ट हो गया भइया!",
        "LOW_BATTERY": "बॉस बैटरी का वाट लग गया!"
    },
    "english": {
        "ANC_ON": "Noise Cancellation Activated. Silence Engaged.",
        "TRANSPARENCY": "Transparency Mode On. External Audio Live.",
        "ANC_OFF": "Noise Control Off. Standard Audio Mode.",
        "MIC_MUTED": "Microphone Muted. Audio Isolated.",
        "CONNECTED": "Headphones Connected. Welcome Back.",
        "LOW_BATTERY": "Warning. Battery Low. Please Recharge."
    }
}


class VoiceEngine(QObject):
    """
    Handles playing slang voice cues and emitting text for HUD popups.
    Uses custom user MP3 audio recordings when available.
    Enforces dynamic re-binding to active connected Bluetooth headphone output.
    """
    hud_text_ready = Signal(str, str, str)  # event_key, title, slang_text

    def __init__(self, language: str = "hindi_tapori", enabled: bool = True) -> None:
        super().__init__()
        self.language: str = language.lower()
        self.enabled: bool = enabled
        self._speech_queue: queue.Queue = queue.Queue()
        self._worker_thread: threading.Thread = threading.Thread(target=self._speech_worker, daemon=True)
        self._worker_thread.start()

    def set_language(self, language: str) -> None:
        lang_key = language.lower()
        if lang_key in VOICE_LINES:
            self.language = lang_key
            logger.info("VoiceEngine language changed to: %s", self.language)
        else:
            self.language = "hindi_tapori"

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def get_slang_text(self, event_key: str) -> str:
        lang_dict = VOICE_LINES.get(self.language, VOICE_LINES["hindi_tapori"])
        return lang_dict.get(event_key, VOICE_LINES["hindi_tapori"].get(event_key, "Action Triggered"))

    def trigger(self, event_key: str, title: str = "KAANSHIELD") -> str:
        slang_text = self.get_slang_text(event_key)
        self.hud_text_ready.emit(event_key, title, slang_text)

        if self.enabled:
            self._speech_queue.put((self.language, event_key, slang_text))

        return slang_text

    def _speech_worker(self) -> None:
        if IS_WINDOWS and PYTHONCOM_AVAILABLE:
            try:
                pythoncom.CoInitialize()
            except Exception as e:
                logger.debug("CoInitialize note: %s", e)

        pyttsx_engine = None
        if TTS_AVAILABLE:
            try:
                pyttsx_engine = pyttsx3.init()
                pyttsx_engine.setProperty("rate", 160)
            except Exception as e:
                logger.error("Failed to init pyttsx3 worker: %s", e)

        while True:
            try:
                lang_key, event_key, text = self._speech_queue.get()
                logger.info("Speech worker processing: [%s] %s -> %s", lang_key, event_key, text)

                custom_file = SOUNDS_DIR / f"{lang_key}_{event_key}.mp3"
                played_custom = False

                if custom_file.exists() and PYGAME_AVAILABLE:
                    try:
                        logger.info("Playing custom voice recording into earphone: %s", custom_file)
                        if pygame.mixer.get_init():
                            pygame.mixer.quit()
                        pygame.mixer.init()

                        pygame.mixer.music.load(str(custom_file))
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        played_custom = True
                    except Exception as e:
                        logger.error("Failed to play custom MP3 %s: %s", custom_file, e)

                if not played_custom:
                    played_gtts = self._play_gtts(lang_key, text)

                    if not played_gtts and pyttsx_engine:
                        try:
                            pyttsx_engine.say(text)
                            pyttsx_engine.runAndWait()
                        except Exception as err:
                            logger.error("pyttsx3 speech error: %s", err)

                self._speech_queue.task_done()
            except Exception as e:
                logger.error("Unexpected error in speech worker: %s", e)

    def _play_gtts(self, lang_key: str, text: str) -> bool:
        gtts_code = LANG_CODE_MAP.get(lang_key, "hi")
        text_hash = hashlib.md5(f"{gtts_code}_{text}".encode("utf-8")).hexdigest()
        cache_file = SOUNDS_DIR / f"{text_hash}.mp3"

        if not cache_file.exists() and GTTS_AVAILABLE:
            try:
                tts = gTTS(text=text, lang=gtts_code, slow=False)
                tts.save(str(cache_file))
                logger.info("Cached gTTS audio file for '%s' -> %s", text, cache_file)
            except Exception as e:
                logger.warning("gTTS audio generation failed for '%s': %s", text, e)
                return False

        if cache_file.exists() and PYGAME_AVAILABLE:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.quit()
                pygame.mixer.init()

                pygame.mixer.music.load(str(cache_file))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                return True
            except Exception as e:
                logger.error("Pygame audio playback error: %s", e)

        return False
