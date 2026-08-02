"""
Dashboard Window Module for KaanShield.
Single-Page Unified Control Dashboard Window matching target UI mockup with 2 active languages (Hindi & English).
All battery badges, device badges, ANC cards, ambient level sliders, and per-app audio volume sliders
are fully interactive and wired to backend APIs.
Features the official KaanShield 3D logo icon in top header & window taskbar icon.
"""

import os
import logging
import asyncio
import threading
from typing import Dict, List, Any
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QListWidget, QListWidgetItem, QFrame,
    QProgressBar, QCheckBox, QScrollArea
)
from PySide6.QtGui import QFont, QPixmap, QIcon

from core.path_utils import get_resource_path
from core.app_controller import AppController
from core.bluetooth_manager import BluetoothManager
from core.voice_engine import VOICE_LINES

logger = logging.getLogger(__name__)


class DashboardWindow(QMainWindow):
    """
    Main Control Dashboard Window matching target UI mockup layout.
    Features KaanShield 3D App Logo in top header & taskbar icon.
    """

    scan_completed = Signal(list)  # Signal emitted when background Bluetooth scan completes

    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self.controller: AppController = controller
        self.active_voice_pill: str = "hindi_tapori"
        self._init_window()
        self._init_ui()
        self._wire_signals()
        self._scan_bluetooth_devices()

    def _init_window(self) -> None:
        self.setWindowTitle("KaanShield — Audio & Headphone Command Center")
        self.resize(1180, 740)
        self.setMinimumSize(1060, 660)

        # Set Window Titlebar Icon & Taskbar Icon
        app_logo_path = get_resource_path(os.path.join("assets", "icons", "app_logo.png"))
        if os.path.exists(app_logo_path):
            self.setWindowIcon(QIcon(app_logo_path))

    def _init_ui(self) -> None:
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(16, 14, 16, 14)
        root_layout.setSpacing(10)

        # ---------------------------------------------------------------------
        # 1. TOP HEADER NAVIGATION BAR WITH KAANSHIELD APP LOGO
        # ---------------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Shield 3D Logo Image + Title + Tagline
        brand_h = QHBoxLayout()
        brand_h.setSpacing(10)

        logo_img_label = QLabel()
        app_logo_path = get_resource_path(os.path.join("assets", "icons", "app_logo.png"))
        if os.path.exists(app_logo_path):
            pixmap = QPixmap(app_logo_path).scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_img_label.setPixmap(pixmap)
        else:
            logo_img_label.setText("🛡️")
            logo_img_label.setFont(QFont("Segoe UI", 22))

        brand_v = QVBoxLayout()
        brand_v.setSpacing(1)
        title_label = QLabel("KAANSHIELD", self.central_widget)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #f97316; letter-spacing: 1px;")

        subtitle_label = QLabel("Nuke the Noise. Protect the Vibe.", self.central_widget)
        subtitle_label.setStyleSheet("color: #94a3b8; font-size: 11px;")

        brand_v.addWidget(title_label)
        brand_v.addWidget(subtitle_label)

        brand_h.addWidget(logo_img_label)
        brand_h.addLayout(brand_v)
        header_layout.addLayout(brand_h)

        header_layout.addStretch()

        # Top Device Selector Badge + Prominent Scan Button
        self.device_combo = QComboBox(self.central_widget)
        self.device_combo.setMinimumWidth(260)
        self.device_combo.addItem("🎧 Harmonics Twins 33 (Connected)", "00:11:22:33:44:55")
        self.device_combo.currentIndexChanged.connect(self._on_device_combo_changed)
        header_layout.addWidget(self.device_combo)

        self.btn_scan = QPushButton("🔄 Scan Bluetooth", self.central_widget)
        self.btn_scan.setStyleSheet("background-color: #f97316; font-weight: bold; color: white; padding: 6px 14px; border-radius: 6px;")
        self.btn_scan.clicked.connect(self._scan_bluetooth_devices)
        header_layout.addWidget(self.btn_scan)

        # Battery Badge (Dynamically Updated)
        batt_badge = QFrame()
        batt_badge.setObjectName("topStatusBadge")
        bb_layout = QHBoxLayout(batt_badge)
        bb_layout.setContentsMargins(8, 4, 8, 4)
        self.lbl_battery_top = QLabel("BATTERY 🔋 90% ∨")
        self.lbl_battery_top.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_battery_top.setStyleSheet("color: #22c55e;")
        bb_layout.addWidget(self.lbl_battery_top)
        header_layout.addWidget(batt_badge)

        # L / R Earbud Battery Badge (Dynamically Updated)
        lr_badge = QFrame()
        lr_badge.setObjectName("topStatusBadge")
        lr_layout = QHBoxLayout(lr_badge)
        lr_layout.setContentsMargins(8, 4, 8, 4)
        self.lbl_lr_top = QLabel("L 90% 🟢  |  R 90% 🟢 ∨")
        self.lbl_lr_top.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_lr_top.setStyleSheet("color: #38bdf8;")
        lr_layout.addWidget(self.lbl_lr_top)
        header_layout.addWidget(lr_badge)

        # ANC Active Status Badge
        anc_badge = QFrame()
        anc_badge.setObjectName("topStatusBadge")
        ab_layout = QHBoxLayout(anc_badge)
        ab_layout.setContentsMargins(8, 4, 8, 4)
        self.lbl_anc_top = QLabel("📶 ANC ON Active")
        self.lbl_anc_top.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_anc_top.setStyleSheet("color: #f97316;")
        ab_layout.addWidget(self.lbl_anc_top)
        header_layout.addWidget(anc_badge)

        root_layout.addLayout(header_layout)

        # ---------------------------------------------------------------------
        # 2. MAIN HERO SECTION (NOISE CONTROL + SPEECH BUBBLE + KID GOKU)
        # ---------------------------------------------------------------------
        hero_layout = QHBoxLayout()
        hero_layout.setSpacing(12)

        # Left Container: Noise Control Panel + Speech Bubble Card
        hero_panel = QFrame()
        hero_panel.setObjectName("panelGlass")
        hp_layout = QVBoxLayout(hero_panel)
        hp_layout.setContentsMargins(14, 12, 14, 12)
        hp_layout.setSpacing(10)

        inner_hero_row = QHBoxLayout()
        inner_hero_row.setSpacing(12)

        # Column 1: Noise Control Section
        nc_col = QVBoxLayout()
        nc_col.setSpacing(8)

        nc_title = QLabel("|||- NOISE CONTROL (CLICK TO TOGGLE ON/OFF)")
        nc_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        nc_title.setStyleSheet("color: #38bdf8; letter-spacing: 0.5px;")
        nc_col.addWidget(nc_title)

        # 4 Mode Cards (ANC ON, Transparency, ANC OFF, Ambient Level)
        cards_grid = QHBoxLayout()
        cards_grid.setSpacing(6)

        self.card_anc_on, self.sub_anc_on = self._create_mode_card("|||-", "ANC ON", "अबे शोर बंद!", "Active", "ANC_ON", is_active=True)
        self.card_transparency, self.sub_transparency = self._create_mode_card("👤", "TRANSPARENCY", "दुनिया की बात!", "Click to Turn On", "TRANSPARENCY")
        self.card_anc_off, self.sub_anc_off = self._create_mode_card("⏻", "ANC OFF", "नॉर्मल मोड", "All Off", "ANC_OFF")
        self.card_ambient, self.lbl_ambient_val = self._create_mode_card("☀️", "AMBIENT LEVEL", "12 / 20", "Pass-through", "AMBIENT")

        cards_grid.addWidget(self.card_anc_on)
        cards_grid.addWidget(self.card_transparency)
        cards_grid.addWidget(self.card_anc_off)
        cards_grid.addWidget(self.card_ambient)
        nc_col.addLayout(cards_grid)

        # Ambient Level Slider Track
        amb_row = QHBoxLayout()
        amb_lbl_min = QLabel("Ambient Level  0")
        amb_lbl_min.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        self.ambient_slider = QSlider(Qt.Horizontal)
        self.ambient_slider.setRange(0, 20)
        self.ambient_slider.setValue(12)
        self.ambient_slider.valueChanged.connect(self._on_ambient_slider_changed)
        amb_lbl_max = QLabel("20")
        amb_lbl_max.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")

        amb_row.addWidget(amb_lbl_min)
        amb_row.addWidget(self.ambient_slider, stretch=1)
        amb_row.addWidget(amb_lbl_max)
        nc_col.addLayout(amb_row)

        inner_hero_row.addLayout(nc_col, stretch=3)

        # Column 2: Speech Bubble Voice Quote Card + Voice Mode Quick Switch Pills
        right_speech_v = QVBoxLayout()
        right_speech_v.setSpacing(8)

        bubble_card = QFrame()
        bubble_card.setObjectName("speechBubbleCard")
        bc_layout = QVBoxLayout(bubble_card)
        bc_layout.setContentsMargins(12, 10, 12, 10)
        bc_layout.setSpacing(6)

        # Dropdown Header inside Speech Card (Hindi & English only)
        self.lang_combo_top = QComboBox()
        self.lang_combo_top.blockSignals(True)
        self.lang_combo_top.addItem("🌐 HINDI / TAPORI MODE", "hindi_tapori")
        self.lang_combo_top.addItem("🌐 ENGLISH MODE", "english")
        self.lang_combo_top.blockSignals(False)
        self.lang_combo_top.currentIndexChanged.connect(self._on_language_changed)
        bc_layout.addWidget(self.lang_combo_top)

        # Quote Text
        self.lbl_quote_main = QLabel('"अबे शोर बंद! फुल शांति!"')
        self.lbl_quote_main.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_quote_main.setStyleSheet("color: #ffffff;")

        self.lbl_quote_sub = QLabel("Full Raula Khatam!")
        self.lbl_quote_sub.setStyleSheet("color: #cbd5e1; font-size: 10px;")

        bc_layout.addWidget(self.lbl_quote_main)
        bc_layout.addWidget(self.lbl_quote_sub)

        # Audio Wave Graphic
        wave_gfx = QLabel("|||i|i|||i|i|||i|i|||i|i|||i|i|||")
        wave_gfx.setStyleSheet("color: #f97316; font-weight: bold; letter-spacing: 2px;")
        bc_layout.addWidget(wave_gfx)

        right_speech_v.addWidget(bubble_card)

        # Voice Mode Quick Switch Pills Row (Hindi & English strictly)
        pills_frame = QVBoxLayout()
        pills_frame.setSpacing(4)
        pills_hdr = QLabel("❖ VOICE MODE")
        pills_hdr.setStyleSheet("color: #f97316; font-size: 10px; font-weight: bold;")
        pills_frame.addWidget(pills_hdr)

        pills_row = QHBoxLayout()
        pills_row.setSpacing(8)

        self.pill_hindi = self._create_voice_pill("🇮🇳 Hindi / Tapori", "hindi_tapori", is_active=True)
        self.pill_english = self._create_voice_pill("🇬🇧 English", "english")

        pills_row.addWidget(self.pill_hindi)
        pills_row.addWidget(self.pill_english)
        pills_frame.addLayout(pills_row)

        right_speech_v.addLayout(pills_frame)
        inner_hero_row.addLayout(right_speech_v, stretch=2)

        hp_layout.addLayout(inner_hero_row)
        hero_layout.addWidget(hero_panel, stretch=3)

        # Right Container: Kid Goku Sunset Backdrop Image
        goku_card = QFrame()
        goku_card.setObjectName("panelGlass")
        goku_card.setFixedWidth(240)
        gc_layout = QVBoxLayout(goku_card)
        gc_layout.setContentsMargins(4, 4, 4, 4)

        goku_img_label = QLabel()
        goku_bg_path = get_resource_path(os.path.join("assets", "icons", "kid_goku_bg.png"))
        if os.path.exists(goku_bg_path):
            pixmap = QPixmap(goku_bg_path).scaled(230, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            goku_img_label.setPixmap(pixmap)
            goku_img_label.setAlignment(Qt.AlignCenter)
        else:
            goku_img_label.setText("🎨 Kid Goku Artwork")

        gc_layout.addWidget(goku_img_label)
        hero_layout.addWidget(goku_card, stretch=1)

        root_layout.addLayout(hero_layout)

        # ---------------------------------------------------------------------
        # 3. MIDDLE ROW (PER-APP MIXER + QUICK ACTIONS & LIVE STATUS)
        # ---------------------------------------------------------------------
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        # Left Section: PER-APP AUDIO & MIC CONTROL TABLE
        mixer_panel = QFrame()
        mixer_panel.setObjectName("panelGlass")
        mp_layout = QVBoxLayout(mixer_panel)
        mp_layout.setContentsMargins(14, 12, 14, 12)
        mp_layout.setSpacing(8)

        # Table Header Row
        mp_header = QHBoxLayout()
        m_title = QLabel("🎛️ PER-APP AUDIO & MIC CONTROL")
        m_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        m_title.setStyleSheet("color: #38bdf8;")

        mp_header.addWidget(m_title)
        mp_header.addStretch()

        lbl_h_audio = QLabel("Audio Volume")
        lbl_h_audio.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        lbl_h_output = QLabel("Audio Output")
        lbl_h_output.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        lbl_h_mic_vol = QLabel("Mic Volume")
        lbl_h_mic_vol.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        lbl_h_mic_dev = QLabel("Mic Device")
        lbl_h_mic_dev.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        lbl_h_mute = QLabel("Mute")
        lbl_h_mute.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")

        mp_header.addWidget(lbl_h_audio)
        mp_header.addSpacing(60)
        mp_header.addWidget(lbl_h_output)
        mp_header.addSpacing(30)
        mp_header.addWidget(lbl_h_mic_vol)
        mp_header.addSpacing(40)
        mp_header.addWidget(lbl_h_mic_dev)
        mp_header.addSpacing(20)
        mp_header.addWidget(lbl_h_mute)
        mp_layout.addLayout(mp_header)

        # App List Widget
        self.audio_list = QListWidget()
        self.audio_list.setFixedHeight(160)
        self.audio_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.audio_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.audio_list.setStyleSheet("background: transparent; border: none;")
        mp_layout.addWidget(self.audio_list)

        bottom_layout.addWidget(mixer_panel, stretch=3)

        # Right Section: QUICK ACTIONS & LIVE STATUS
        right_side_v = QVBoxLayout()
        right_side_v.setSpacing(10)

        # Quick Actions Card
        quick_panel = QFrame()
        quick_panel.setObjectName("panelGlass")
        qp_layout = QVBoxLayout(quick_panel)
        qp_layout.setContentsMargins(12, 10, 12, 10)
        qp_layout.setSpacing(6)

        q_title = QLabel("⚡ QUICK ACTIONS")
        q_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        q_title.setStyleSheet("color: #f97316;")
        qp_layout.addWidget(q_title)

        hk_grid = QVBoxLayout()
        hk_grid.setSpacing(4)

        hk_r1 = QHBoxLayout()
        hk_r1.setSpacing(4)

        card_anc_hk = self._create_hotkey_card("⌨️", "Ctrl + Alt + A", "Toggle ANC On/Off", "#a78bfa")
        card_anc_hk.mousePressEvent = lambda ev: self.controller.set_anc_mode("ANC_ON")

        card_mic_hk = self._create_hotkey_card("🎙️", "Ctrl + Alt + M", "Mute / Unmute Mic", "#38bdf8")
        card_mic_hk.mousePressEvent = lambda ev: self.controller.toggle_global_mic_mute()

        hk_r1.addWidget(card_anc_hk)
        hk_r1.addWidget(card_mic_hk)

        hk_r2 = QHBoxLayout()
        hk_r2.setSpacing(4)

        card_trans_hk = self._create_hotkey_card("📶", "Ctrl + Alt + T", "Transparency On/Off", "#f97316")
        card_trans_hk.mousePressEvent = lambda ev: self.controller.set_anc_mode("TRANSPARENCY")

        card_anc_off_hk = self._create_hotkey_card("⏻", "Ctrl + Alt + O", "Turn All Off", "#94a3b8")
        card_anc_off_hk.mousePressEvent = lambda ev: self.controller.set_anc_mode("ANC_OFF")

        hk_r2.addWidget(card_trans_hk)
        hk_r2.addWidget(card_anc_off_hk)

        hk_grid.addLayout(hk_r1)
        hk_grid.addLayout(hk_r2)
        qp_layout.addLayout(hk_grid)

        right_side_v.addWidget(quick_panel)

        # LIVE STATUS Card (3D Headphone Render)
        status_panel = QFrame()
        status_panel.setObjectName("panelGlass")
        sp_layout = QHBoxLayout(status_panel)
        sp_layout.setContentsMargins(12, 8, 12, 8)
        sp_layout.setSpacing(10)

        st_v = QVBoxLayout()
        st_v.setSpacing(3)
        st_title = QLabel("⚡ LIVE STATUS")
        st_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        st_title.setStyleSheet("color: #a78bfa;")
        st_v.addWidget(st_title)

        st_v.addWidget(QLabel("📶 Connection: <font color='#22c55e'><b>Strong</b></font>"))
        st_v.addWidget(QLabel("⏱️ Latency: <font color='#22c55e'><b>20 ms</b></font>"))
        st_v.addWidget(QLabel("🎵 Audio Codec: <font color='#f97316'><b>LDAC</b></font>"))
        self.lbl_status_anc_mode = QLabel("🎧 Mode: <font color='#f97316'><b>ANC Active</b></font>")
        st_v.addWidget(self.lbl_status_anc_mode)
        sp_layout.addLayout(st_v)

        hp_img_label = QLabel()
        hp_path = get_resource_path(os.path.join("assets", "icons", "headphone_3d.png"))
        if os.path.exists(hp_path):
            hp_pixmap = QPixmap(hp_path).scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            hp_img_label.setPixmap(hp_pixmap)
            hp_img_label.setAlignment(Qt.AlignCenter)
        else:
            hp_img_label.setText("🎧 3D Render")

        sp_layout.addWidget(hp_img_label)
        right_side_v.addWidget(status_panel)

        bottom_layout.addLayout(right_side_v, stretch=1)
        root_layout.addLayout(bottom_layout)

        # ---------------------------------------------------------------------
        # 4. BOTTOM BAR: VOICE CUE TEST & SYSTEM CONTROL
        # ---------------------------------------------------------------------
        golu_bar = QFrame()
        golu_bar.setObjectName("panelGlass")
        gb_layout = QHBoxLayout(golu_bar)
        gb_layout.setContentsMargins(14, 6, 14, 6)
        gb_layout.setSpacing(12)

        golu_avatar = QLabel("👦")
        golu_avatar.setFont(QFont("Segoe UI", 16))

        golu_title_v = QVBoxLayout()
        golu_title_v.setSpacing(1)
        golu_title = QLabel("CURRENT VOICE CUE PLAYBACK")
        golu_title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        golu_title.setStyleSheet("color: #a78bfa;")

        self.golu_quote = QLabel('"अबे शोर बंद! फुल शांति!"')
        self.golu_quote.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.golu_quote.setStyleSheet("color: #ffffff;")

        golu_title_v.addWidget(golu_title)
        golu_title_v.addWidget(self.golu_quote)

        gb_layout.addWidget(golu_avatar)
        gb_layout.addLayout(golu_title_v)

        golu_wave = QLabel("||i||i||i||i||i||i||")
        golu_wave.setStyleSheet("color: #f97316; letter-spacing: 2px;")
        gb_layout.addWidget(golu_wave)

        btn_play = QPushButton("🔊 Test Voice Cue")
        btn_play.setStyleSheet("background-color: #f97316; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
        btn_play.clicked.connect(lambda: self.controller.voice_engine.trigger(self.controller.current_anc_mode, title="KAANSHIELD PREVIEW"))
        gb_layout.addWidget(btn_play)

        gb_layout.addStretch()
        root_layout.addWidget(golu_bar)

        self._refresh_audio_streams()

    def _create_mode_card(self, icon: str, title: str, sub1: str, sub2: str, mode_key: str, is_active: bool = False):
        card = QFrame()
        card.setObjectName("modeSelectCard")
        card.setProperty("active", "true" if is_active else "false")
        card.setFixedWidth(105)

        v = QVBoxLayout(card)
        v.setContentsMargins(6, 8, 6, 8)
        v.setSpacing(3)
        v.setAlignment(Qt.AlignCenter)

        i_lbl = QLabel(icon)
        i_lbl.setAlignment(Qt.AlignCenter)
        i_lbl.setFont(QFont("Segoe UI", 12))
        if is_active:
            i_lbl.setStyleSheet("color: #f97316;")

        t_lbl = QLabel(title)
        t_lbl.setAlignment(Qt.AlignCenter)
        t_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))

        s1_lbl = QLabel(sub1)
        s1_lbl.setAlignment(Qt.AlignCenter)
        s1_lbl.setStyleSheet("color: #94a3b8; font-size: 8px;")

        s2_lbl = QLabel(sub2)
        s2_lbl.setAlignment(Qt.AlignCenter)
        s2_lbl.setStyleSheet("color: #94a3b8; font-size: 8px;")

        v.addWidget(i_lbl)
        v.addWidget(t_lbl)
        v.addWidget(s1_lbl)
        v.addWidget(s2_lbl)

        for child in (i_lbl, t_lbl, s1_lbl, s2_lbl):
            child.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        card.mousePressEvent = lambda ev: self.controller.set_anc_mode(mode_key)
        return card, s2_lbl

    def _create_voice_pill(self, label: str, lang_key: str, is_active: bool = False) -> QPushButton:
        btn = QPushButton(label)
        btn.setObjectName("voicePill")
        btn.setProperty("active", "true" if is_active else "false")
        btn.clicked.connect(lambda: self._select_voice_pill(lang_key, btn))
        return btn

    def _select_voice_pill(self, lang_key: str, btn_target: QPushButton) -> None:
        self.active_voice_pill = lang_key
        self.controller.set_voice_language(lang_key)

        for btn in (self.pill_hindi, self.pill_english):
            btn.setProperty("active", "true" if btn == btn_target else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        quote = self.controller.voice_engine.get_slang_text(self.controller.current_anc_mode)
        self.lbl_quote_main.setText(f'"{quote}"')
        self.golu_quote.setText(f'"{quote}"')

    def _create_hotkey_card(self, icon: str, shortcut: str, label: str, color_hex: str = "#a78bfa") -> QFrame:
        card = QFrame()
        card.setObjectName("quickHotkeyCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(6, 6, 6, 6)
        v.setSpacing(2)
        v.setAlignment(Qt.AlignCenter)

        i_lbl = QLabel(icon)
        i_lbl.setFont(QFont("Segoe UI", 12))
        i_lbl.setAlignment(Qt.AlignCenter)

        sc_lbl = QLabel(shortcut)
        sc_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        sc_lbl.setStyleSheet(f"color: {color_hex};")
        sc_lbl.setAlignment(Qt.AlignCenter)

        l_lbl = QLabel(label)
        l_lbl.setStyleSheet("color: #94a3b8; font-size: 8px;")
        l_lbl.setAlignment(Qt.AlignCenter)

        for child in (i_lbl, sc_lbl, l_lbl):
            child.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        v.addWidget(i_lbl)
        v.addWidget(sc_lbl)
        v.addWidget(l_lbl)
        return card

    def _scan_bluetooth_devices(self) -> None:
        self.btn_scan.setText("⏳ Scanning...")
        self.btn_scan.setEnabled(False)

        def worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                devices = loop.run_until_complete(BluetoothManager.scan_for_devices())
                loop.close()
            except Exception as e:
                logger.error("Error in background Bluetooth scan worker: %s", e)
                devices = []

            self.scan_completed.emit(devices)

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_completed(self, devices: List[Dict[str, Any]]) -> None:
        self.btn_scan.setText("🔄 Scan Bluetooth")
        self.btn_scan.setEnabled(True)

        self.device_combo.blockSignals(True)
        self.device_combo.clear()

        connected_index = 0
        for idx, dev in enumerate(devices):
            label = f"🎧 {dev['name']}"
            self.device_combo.addItem(label, dev['address'])
            if dev.get('is_connected', False) and connected_index == 0:
                connected_index = idx

        self.device_combo.setCurrentIndex(connected_index)
        self.device_combo.blockSignals(False)

        if devices:
            target_dev = devices[connected_index]
            dev_clean = target_dev['name'].replace(" (Connected)", "").replace(" (Paired)", "")
            self.controller.connect_device_async(address=target_dev['address'], name=dev_clean, speak_welcome=False)

            # FORCE REAL-TIME BATTERY REFRESH ON EVERY SCAN CLICK
            real_batt = BluetoothManager.get_real_device_battery(dev_clean)
            fresh_battery = {"left": real_batt, "right": real_batt, "case": 100}
            self.controller.battery_state = fresh_battery
            self._update_battery_ui(fresh_battery)

        logger.info("Device dropdown updated with %d discovered Bluetooth devices. Selected index %d.", len(devices), connected_index)

    def _on_device_combo_changed(self, index: int) -> None:
        dev_name = self.device_combo.itemText(index).replace("🎧 ", "").replace(" (Connected)", "").replace(" (Paired)", "")
        dev_addr = self.device_combo.itemData(index) or "00:11:22:33:44:55"
        self.controller.connect_device_async(address=dev_addr, name=dev_name, speak_welcome=False)

        # FORCE REAL-TIME BATTERY REFRESH ON DEVICE DROPDOWN SELECTION
        real_batt = BluetoothManager.get_real_device_battery(dev_name)
        fresh_battery = {"left": real_batt, "right": real_batt, "case": 100}
        self.controller.battery_state = fresh_battery
        self._update_battery_ui(fresh_battery)

    def _on_ambient_slider_changed(self, value: int) -> None:
        if hasattr(self, 'lbl_ambient_val'):
            self.lbl_ambient_val.setText(f"{value} / 20")
        self.controller.set_ambient_level(value)

    def _on_language_changed(self, index: int) -> None:
        lang_key = self.lang_combo_top.itemData(index)
        if lang_key:
            self.controller.set_voice_language(lang_key)
            quote = self.controller.voice_engine.get_slang_text(self.controller.current_anc_mode)
            self.lbl_quote_main.setText(f'"{quote}"')

    def _on_mute_clicked(self, process_name: str, mute_btn: QPushButton) -> None:
        """
        Handles clicking per-app mute button and updating visual feedback live.
        """
        is_muted = self.controller.audio_mixer.toggle_app_mute(process_name)
        if is_muted:
            mute_btn.setText("🚫 Muted")
            mute_btn.setStyleSheet("color: #ef4444; font-weight: bold; padding: 2px 6px; font-size: 10px;")
        else:
            mute_btn.setText("🎙️ Active")
            mute_btn.setStyleSheet("color: #22c55e; font-weight: bold; padding: 2px 6px; font-size: 10px;")

    def _refresh_audio_streams(self) -> None:
        self.audio_list.clear()
        streams = self.controller.get_all_app_streams()

        for stream in streams:
            item_widget = QWidget()
            h_layout = QHBoxLayout(item_widget)
            h_layout.setContentsMargins(4, 2, 4, 2)
            h_layout.setSpacing(6)

            icon_lbl = QLabel(stream.audio_icon)
            name_lbl = QLabel(stream.app_name)
            name_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
            name_lbl.setFixedWidth(100)

            aud_pct = QLabel(f"{int(stream.audio_volume * 100)}%")
            aud_pct.setFixedWidth(30)
            aud_pct.setStyleSheet("color: #f97316; font-weight: bold; font-size: 10px;")

            aud_slider = QSlider(Qt.Horizontal)
            aud_slider.setRange(0, 100)
            aud_slider.setValue(int(stream.audio_volume * 100))

            aud_slider.valueChanged.connect(
                lambda val, lbl=aud_pct, proc=stream.process_name: (
                    lbl.setText(f"{val}%"),
                    self.controller.audio_mixer.set_app_audio_volume(proc, val / 100.0)
                )
            )

            aud_out = QComboBox()
            aud_out.addItem(stream.audio_output)
            aud_out.setFixedWidth(95)

            if stream.has_mic:
                mic_pct = QLabel(f"{int(stream.mic_volume * 100)}%")
                mic_pct.setFixedWidth(30)
                mic_pct.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 10px;")

                mic_slider = QSlider(Qt.Horizontal)
                mic_slider.setRange(0, 100)
                mic_slider.setValue(int(stream.mic_volume * 100))
                mic_slider.valueChanged.connect(
                    lambda val, lbl=mic_pct, proc=stream.process_name: (
                        lbl.setText(f"{val}%"),
                        self.controller.audio_mixer.set_app_mic_volume(proc, val / 100.0)
                    )
                )

                mic_dev = QComboBox()
                mic_dev.addItem(stream.mic_device)
                mic_dev.setFixedWidth(105)

                mute_btn = QPushButton("🚫 Muted" if stream.is_muted else "🎙️ Active")
                mute_btn.setFixedWidth(68)
                if stream.is_muted:
                    mute_btn.setStyleSheet("color: #ef4444; font-weight: bold; padding: 2px 6px; font-size: 10px;")
                else:
                    mute_btn.setStyleSheet("color: #22c55e; font-weight: bold; padding: 2px 6px; font-size: 10px;")

                mute_btn.clicked.connect(lambda _, proc=stream.process_name, btn=mute_btn: self._on_mute_clicked(proc, btn))
            else:
                mic_slider = QLabel("—")
                mic_slider.setAlignment(Qt.AlignCenter)
                mic_pct = QLabel("")
                mic_dev = QLabel("—")
                mic_dev.setAlignment(Qt.AlignCenter)
                mute_btn = QLabel("🚫")

            h_layout.addWidget(icon_lbl)
            h_layout.addWidget(name_lbl)
            h_layout.addWidget(aud_slider, stretch=1)
            h_layout.addWidget(aud_pct)
            h_layout.addWidget(aud_out)
            h_layout.addSpacing(10)
            if isinstance(mic_slider, QSlider):
                h_layout.addWidget(mic_slider, stretch=1)
            else:
                h_layout.addWidget(mic_slider)
            h_layout.addWidget(mic_pct)
            if isinstance(mic_dev, QComboBox):
                h_layout.addWidget(mic_dev)
            else:
                h_layout.addWidget(mic_dev)
            h_layout.addSpacing(10)
            if isinstance(mute_btn, QPushButton):
                h_layout.addWidget(mute_btn)
            else:
                h_layout.addWidget(mute_btn)

            item = QListWidgetItem(self.audio_list)
            item.setSizeHint(QSize(0, 28))
            self.audio_list.addItem(item)
            self.audio_list.setItemWidget(item, item_widget)

    def _wire_signals(self) -> None:
        self.scan_completed.connect(self._on_scan_completed)
        self.controller.anc_mode_changed.connect(self._update_anc_ui)
        self.controller.battery_updated.connect(self._update_battery_ui, Qt.QueuedConnection)
        self.controller.device_connected.connect(self._on_device_connected)

    def _update_anc_ui(self, mode: str) -> None:
        self.card_anc_on.setProperty("active", "true" if mode == "ANC_ON" else "false")
        self.card_transparency.setProperty("active", "true" if mode == "TRANSPARENCY" else "false")
        self.card_anc_off.setProperty("active", "true" if mode == "ANC_OFF" else "false")
        self.card_ambient.setProperty("active", "true" if mode == "AMBIENT" else "false")

        # Dynamic Subtitle text updates for ON/OFF state
        self.sub_anc_on.setText("Active (Click to Turn Off)" if mode == "ANC_ON" else "Click to Turn On")
        self.sub_transparency.setText("Active (Click to Turn Off)" if mode == "TRANSPARENCY" else "Click to Turn On")
        self.sub_anc_off.setText("All Off" if mode == "ANC_OFF" else "Click to Turn All Off")

        for card in (self.card_anc_on, self.card_transparency, self.card_anc_off, self.card_ambient):
            card.style().unpolish(card)
            card.style().polish(card)

        # Update Top ANC Badge
        if mode == "ANC_ON":
            self.lbl_anc_top.setText("📶 ANC ON Active")
            self.lbl_anc_top.setStyleSheet("color: #f97316;")
            self.lbl_status_anc_mode.setText("🎧 Mode: <font color='#f97316'><b>ANC Active</b></font>")
        elif mode == "TRANSPARENCY":
            self.lbl_anc_top.setText("👤 Transparency Active")
            self.lbl_anc_top.setStyleSheet("color: #38bdf8;")
            self.lbl_status_anc_mode.setText("🎧 Mode: <font color='#38bdf8'><b>Transparency Active</b></font>")
        elif mode == "ANC_OFF":
            self.lbl_anc_top.setText("⏻ ANC OFF Active")
            self.lbl_anc_top.setStyleSheet("color: #94a3b8;")
            self.lbl_status_anc_mode.setText("🎧 Mode: <font color='#94a3b8'><b>Normal / Off</b></font>")
        elif mode == "AMBIENT":
            self.lbl_anc_top.setText("☀️ Ambient Active")
            self.lbl_anc_top.setStyleSheet("color: #a78bfa;")
            self.lbl_status_anc_mode.setText("🎧 Mode: <font color='#a78bfa'><b>Ambient Active</b></font>")

        quote = self.controller.voice_engine.get_slang_text(mode)
        self.lbl_quote_main.setText(f'"{quote}"')
        self.golu_quote.setText(f'"{quote}"')

    def _update_battery_ui(self, battery: dict) -> None:
        l = battery.get("left", 90)
        r = battery.get("right", 90)
        c = battery.get("case", 100)
        self.lbl_battery_top.setText(f"BATTERY 🔋 {l}% ∨")
        self.lbl_lr_top.setText(f"L {l}% 🟢  |  R {r}% 🟢 ∨")
        logger.info("UI Battery badges updated: Top=%d%%, Left Earbud=%d%%, Right Earbud=%d%%", l, l, r)

    def _on_device_connected(self, device_name: str, capabilities: dict) -> None:
        logger.info("UI notified of device connection: %s", device_name)
        self._update_battery_ui(self.controller.battery_state)
