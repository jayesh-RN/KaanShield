"""
HUD Overlay Module for KaanShield.
Animated On-Screen Display (OSD Slang Pop-up Banner) widget.
Fades in smoothly to display current mode and slang text across all applications.
"""

import logging
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)


class HudOverlay(QWidget):
    """
    On-Screen Display (OSD) HUD Slang Pop-up Banner overlay.
    Frameless, transparent, stays on top of all windows without taking focus.
    """

    def __init__(self, display_duration_ms: int = 4500) -> None:
        super().__init__()
        self.display_duration_ms: int = display_duration_ms
        self._init_window_flags()
        self._init_ui()
        self._init_animations()

    def _init_window_flags(self) -> None:
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

    def _init_ui(self) -> None:
        self.setFixedSize(520, 100)

        # Main glass container
        self.container = QWidget(self)
        self.container.setObjectName("hudContainer")
        self.container.setFixedSize(510, 90)
        self.container.setStyleSheet("""
            QWidget#hudContainer {
                background-color: rgba(15, 23, 42, 0.96);
                border: 1px solid rgba(99, 102, 241, 0.6);
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(18, 12, 18, 12)

        # Header Row (Icon + Title)
        header_layout = QHBoxLayout()
        self.title_label = QLabel("🎧  KAANSHIELD — ANC ACTIVATED", self.container)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: #818cf8;")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Slang Message Row
        self.slang_label = QLabel('💬  "Oye Shor Band Paaji! Full Raula Khatam!"', self.container)
        self.slang_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.slang_label.setStyleSheet("color: #f8fafc;")
        self.slang_label.setWordWrap(True)
        layout.addWidget(self.slang_label)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.container)

    def _init_animations(self) -> None:
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self.hide_overlay)

    def show_banner(self, event_key: str, title: str, slang_text: str) -> None:
        """
        Populate banner text, position near top-right screen, and trigger fade-in animation.
        Duration increased to 4.5 seconds for comfortable reading!
        """
        icon_map = {
            "ANC_ON": "🟢 🎧",
            "TRANSPARENCY": "🟡 🎧",
            "ANC_OFF": "⚪ 🎧",
            "MIC_MUTED": "🎙️ 🚫",
            "CONNECTED": "⚡ 🎧",
            "LOW_BATTERY": "🔋 ⚠️"
        }
        icon = icon_map.get(event_key, "🎧")

        self.title_label.setText(f"{icon}  {title}")
        self.slang_label.setText(f'💬  "{slang_text}"')

        # Position near top right of screen
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            x = screen_geometry.width() - self.width() - 40
            y = 50
            self.move(x, y)

        self.show()
        self.fade_animation.stop()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

        # Reset dismiss timer to 4500ms (4.5 seconds)
        self.dismiss_timer.stop()
        self.dismiss_timer.start(self.display_duration_ms)

    def hide_overlay(self) -> None:
        """
        Triggers fade-out animation and hides widget.
        """
        self.fade_animation.stop()
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
