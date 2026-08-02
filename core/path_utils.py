"""
Path Utilities for KaanShield.
Ensures file assets (QSS, icons, sounds) resolve correctly in both Python source and PyInstaller executable.
"""

import sys
import os


def get_resource_path(relative_path: str) -> str:
    """
    Returns absolute path to resource, working for both development Python environment
    and PyInstaller frozen bundle (_MEIPASS).
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
