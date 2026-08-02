"""
Main Entry Point Module for KaanShield.
Bootstraps application components, wires event signals/slots, and starts Qt event loop.
Sets official KaanShield 3D App Logo icon on application and taskbar windows.
"""

import os
import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from core.path_utils import get_resource_path
from core.config_manager import ConfigManager
from core.app_controller import AppController
from core.hotkey_manager import HotkeyManager
from ui.tray_app import TrayApp
from ui.dashboard_window import DashboardWindow
from ui.hud_overlay import HudOverlay

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("KaanShield")


def load_stylesheet(app: QApplication) -> None:
    """
    Loads central QSS glassmorphism stylesheet.
    """
    qss_path = get_resource_path(os.path.join("ui", "styles.qss"))
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            logger.info("Loaded QSS stylesheet from %s", qss_path)
        except Exception as e:
            logger.error("Failed to load stylesheet: %s", e)
    else:
        logger.warning("Stylesheet %s not found.", qss_path)


def main() -> None:
    """
    KaanShield application bootstrap.
    """
    logger.info("Starting KaanShield — Nuke the Noise. Protect the Vibe.")

    # 1. Initialize Qt Application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    app_logo_path = get_resource_path(os.path.join("assets", "icons", "app_logo.png"))
    if os.path.exists(app_logo_path):
        app.setWindowIcon(QIcon(app_logo_path))

    load_stylesheet(app)

    # 2. Initialize Core Engine & State Controller
    config_mgr = ConfigManager()
    controller = AppController(config_mgr)

    # 3. Initialize UI Components
    hud_overlay = HudOverlay(display_duration_ms=config_mgr.get("hud_duration_ms", 4500))
    dashboard = DashboardWindow(controller)
    tray = TrayApp(controller)
    tray.show()

    # 4. Wire Signals / Slots
    controller.voice_engine.hud_text_ready.connect(hud_overlay.show_banner)

    # Navigation
    tray.open_dashboard_requested.connect(dashboard.show)
    tray.open_dashboard_requested.connect(dashboard.raise_)
    tray.open_dashboard_requested.connect(dashboard.activateWindow)
    tray.quit_requested.connect(app.quit)

    # 5. Initialize Global Hotkeys
    if config_mgr.get("hotkeys_enabled", True):
        hotkey_mgr = HotkeyManager(
            anc_hotkey=config_mgr.get("hotkey_anc_toggle", "<ctrl>+<alt>+a"),
            mic_hotkey=config_mgr.get("hotkey_mic_mute", "<ctrl>+<alt>+m"),
            transparency_hotkey="<ctrl>+<alt>+t",
            anc_off_hotkey="<ctrl>+<alt>+o"
        )
        hotkey_mgr.anc_toggle_triggered.connect(controller.toggle_anc)
        hotkey_mgr.mic_mute_triggered.connect(controller.toggle_global_mic_mute)
        hotkey_mgr.transparency_triggered.connect(lambda: controller.set_anc_mode("TRANSPARENCY"))
        hotkey_mgr.anc_off_triggered.connect(lambda: controller.set_anc_mode("ANC_OFF"))
        hotkey_mgr.start()

    # Show dashboard initially
    dashboard.show()

    logger.info("KaanShield event loop running.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
