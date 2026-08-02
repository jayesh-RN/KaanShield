"""
Tray App Module for KaanShield.
System Taskbar Tray Icon and Right-Click Context Menu interface.
Uses official KaanShield 3D app icon for system tray notification area.
"""

import os
import logging
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QAction

from core.path_utils import get_resource_path
from core.app_controller import AppController

logger = logging.getLogger(__name__)


class TrayApp(QObject):
    """
    Manages the System Taskbar Tray Icon and Context Menu.
    Uses official KaanShield 3D app icon for system tray notification area.
    """
    open_dashboard_requested = Signal()
    quit_requested = Signal()

    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self.controller: AppController = controller
        self.tray_icon: QSystemTrayIcon = QSystemTrayIcon(self)
        self._init_icon()
        self._init_menu()
        self._wire_signals()

    def _create_default_icon(self) -> QIcon:
        """
        Generates a purple headphone icon pixmap programmatically as fallback.
        """
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#7c3aed"))
        painter.drawEllipse(2, 2, 28, 28)

        painter.setBrush(QColor("#0a0a12"))
        painter.drawEllipse(6, 6, 20, 20)

        painter.setBrush(QColor("#f8fafc"))
        painter.drawEllipse(13, 13, 6, 6)

        painter.end()
        return QIcon(pixmap)

    def _init_icon(self) -> None:
        app_logo_path = get_resource_path(os.path.join("assets", "icons", "app_logo.png"))
        if os.path.exists(app_logo_path):
            icon = QIcon(app_logo_path)
        else:
            icon = self._create_default_icon()

        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("KaanShield — Nuke the Noise. Protect the Vibe.")
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _init_menu(self) -> None:
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #0a0a12;
                color: #f8fafc;
                border: 1px solid rgba(249, 115, 22, 0.4);
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f97316;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
                margin: 4px 0px;
            }
        """)

        # Title Header
        self.header_action = QAction("🎧 KaanShield — Connected", self.menu)
        self.header_action.setEnabled(False)
        self.menu.addAction(self.header_action)

        self.battery_action = QAction("🔋 Battery: 90% (L:90% R:90% C:100%)", self.menu)
        self.battery_action.setEnabled(False)
        self.menu.addAction(self.battery_action)

        self.menu.addSeparator()

        # ANC Modes
        self.anc_on_action = QAction("🟢 Noise Cancelling (ANC ON)", self.menu)
        self.anc_on_action.triggered.connect(lambda: self.controller.set_anc_mode("ANC_ON"))
        self.menu.addAction(self.anc_on_action)

        self.transparency_action = QAction("🟡 Transparency Mode", self.menu)
        self.transparency_action.triggered.connect(lambda: self.controller.set_anc_mode("TRANSPARENCY"))
        self.menu.addAction(self.transparency_action)

        self.anc_off_action = QAction("⚪ ANC Off (All Off)", self.menu)
        self.anc_off_action.triggered.connect(lambda: self.controller.set_anc_mode("ANC_OFF"))
        self.menu.addAction(self.anc_off_action)

        self.menu.addSeparator()

        # Mic Mute
        self.mic_action = QAction("🎙️ Mute Microphone", self.menu)
        self.mic_action.triggered.connect(self.controller.toggle_global_mic_mute)
        self.menu.addAction(self.mic_action)

        self.menu.addSeparator()

        # Dashboard & Quit
        self.dashboard_action = QAction("🖥️ Open KaanShield Dashboard", self.menu)
        self.dashboard_action.triggered.connect(self.open_dashboard_requested.emit)
        self.menu.addAction(self.dashboard_action)

        self.quit_action = QAction("❌ Quit KaanShield", self.menu)
        self.quit_action.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.menu)

    def _wire_signals(self) -> None:
        self.controller.anc_mode_changed.connect(self._update_anc_checked_state)
        self.controller.battery_updated.connect(self._update_battery_display)
        self.controller.device_connected.connect(self._on_device_connected)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.Trigger:  # Single left click
            self.open_dashboard_requested.emit()

    def _update_anc_checked_state(self, mode: str) -> None:
        logger.debug("TrayApp updating checked mode: %s", mode)

    def _update_battery_display(self, battery: dict) -> None:
        left = battery.get("left", 90)
        right = battery.get("right", 90)
        case = battery.get("case", 100)
        self.battery_action.setText(f"🔋 Battery: {left}% (L:{left}% R:{right}% C:{case}%)")

    def _on_device_connected(self, device_name: str, capabilities: dict) -> None:
        self.header_action.setText(f"🎧 KaanShield — {device_name}")
        self.anc_on_action.setEnabled(capabilities.get("anc_control", True))
        self.transparency_action.setEnabled(capabilities.get("anc_control", True))
        self.anc_off_action.setEnabled(capabilities.get("anc_control", True))

    def show(self) -> None:
        self.tray_icon.show()
