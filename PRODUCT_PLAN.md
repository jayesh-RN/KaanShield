# 🎧 KaanShield - Product Specification & Master Architecture

**KaanShield** is an all-in-one, cross-platform (Windows & Linux) desktop utility written 100% in Python. It combines Active Noise Cancellation (ANC) control, battery monitoring, OS-wide hotkeys, per-app audio/mic stream routing, a **Multi-Language Crazy Voice Engine**, and an **Animated On-Screen HUD Pop-up Banner (OSD Overlay)**.

---

## 💥 Brand Identity: KAANSHIELD

* **Name Origin:** *"Kaan"* (Ear) + *"Shield"* (Protection against background noise).
* **Tagline:** *"Nuke the Noise. Protect the Vibe."*

---

## 🖼️ Animated On-Screen HUD Pop-up Banner (OSD Overlay)

Whenever you toggle ANC or mute your mic (via Hotkey `Ctrl+Alt+A` or Tray menu), a sleek, animated **Glassmorphism HUD Pop-up Banner** slides onto your screen:

```text
 ┌──────────────────────────────────────────────────────────────┐
 │ 🎧 KAANSHIELD - ANC ACTIVATED                                │
 │ 💬 "Oye Shor Band Paaji! Full Raula Khatam!"                 │
 └──────────────────────────────────────────────────────────────┘
```

* **Visual & Audio Sync:** The pop-up banner displays the exact crazy slang text on screen at the same instant the voice cue plays!
* **Non-Intrusive:** Fades in smoothly at the top/bottom of your screen for 2.5 seconds without stealing focus from your game, video, or work.

---

## 🗣️ Multi-Language Crazy Voice & Text Engine

| Event | 🚜 **Punjabi** | 🌾 **Haryanvi** | 🎬 **Bhojpuri** | 🇮🇳 **Hindi / Tapori** |
| :--- | :--- | :--- | :--- | :--- |
| **ANC ON** | *"Oye Shor Band Paaji! Full Raula Khatam!"* | *"Re Shor Band Kar Diya Raibo! Poora Sannaata!"* | *"Eey Shor-Shabaa Sab Band Ho Gayil Ba Ho!"* | *"Abe Shor Band! Full Shanti!"* |
| **Transparency** | *"Baahar Di Awaaz Aane De Veere!"* | *"Baahar Ki Sunne De Ib Thodi!"* | *"Bahariya Ka Aawaaj Aave Da Bhaiya!"* | *"Duniya ki baat sunne ka hai bhaya!"* |
| **ANC OFF** | *"Normal System Chalu Ho Gaya Paji!"* | *"Normal Mode Chalu Kar Diya Laadle!"* | *"Normal Mode Chalu Ho Gayil Ba Ho!"* | *"Normal mode chalu ho gaya boss!"* |
| **Mic Muted** | *"Mic Band Kar Ditta Veere!"* | *"Mic Nu Chup Karwa Diya Ib!"* | *"Micwa Mute Kar Dihini Hain Bhaiya!"* | *"Mic Chup! Mu pe tala!"* |
| **Connected** | *"Connect Ho Gaya Paaji! Chak De Phatte!"* | *"Headphone Connect Ho Gya Re Chhoro!"* | *"Headphone Connect Ho Gayil Ba Ho Raja!"* | *"Headphone Connect Ho Gaya Bhaya!"* |

---

## 🎛️ Master Feature Set

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                             KAANSHIELD UTILITY                              │
 ├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
 │  🎧 ANC & Noise  │  🗣️ Voice & HUD  │  🔊 Per-App      │  ⌨️ Global         │
 │     Controller   │     Overlay      │     Audio Mixer  │     Hotkeys        │
 ├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
 │ • ANC ON         │ • Punjabi        │ • Mute/Unmute    │ • Ctrl+Alt+A       │
 │ • Transparency   │ • Haryanvi       │ • Volume Slider  │   (Toggle ANC)     │
 │ • ANC Off        │ • Bhojpuri       │ • Device Router  │ • Ctrl+Alt+M       │
 │ • Ambient 0-20   │ • Hindi / South  │ • Mic Per-App    │   (Mute Mic)       │
 │ • Multi-Brand    │ • Animated OSD   │ • Chrome/Spotify │ • Sound Effects    │
 └──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

---

## 🏗️ 100% Python Architecture

```text
KaanShield/
├── main.py                    # Entry point & bootstrap
├── PRODUCT_PLAN.md            # Master Product Plan & Specification
├── requirements.txt           # Dependencies (PySide6, bleak, pynput, pyttsx3)
├── config.json                # User settings & voice mode preference
├── core/
│   ├── bluetooth_manager.py   # Async BLE / RFCOMM connection engine
│   ├── voice_engine.py        # Crazy Multi-Language Voice Feedback Engine
│   ├── audio_mixer.py         # Per-app audio & mic stream manager
│   ├── hotkey_manager.py      # OS-level keyboard shortcut listener
│   └── config_manager.py      # Preference persistence
├── drivers/
│   ├── base_driver.py         # Abstract headphone driver template
│   ├── mock_driver.py         # Virtual headphone simulator
│   ├── sony_driver.py         # Sony RFCOMM protocol driver
│   ├── airpods_driver.py      # AirPods BLE GATT protocol driver
│   └── galaxy_buds_driver.py  # Galaxy Buds SPP driver
└── ui/
    ├── tray_app.py            # PySide6 system tray icon & context menu
    ├── dashboard_window.py    # PySide6 main control window (ANC + Audio Mixer + Voice Selector)
    ├── hud_overlay.py         # Animated Glassmorphism On-Screen Display (OSD Slang Banner)
    └── styles.qss             # CSS-like glassmorphism dark mode styling
```

---

## 🧩 Device Compatibility & Graceful Degradation

KaanShield uses a **CapabilityFlags** system. Every headphone driver declares upfront which features it supports. If a device doesn't support a feature (e.g., boAt/pTron earbuds with no ANC), that section in the UI is **automatically greyed out** — no crashes, no confusing errors.

| Feature | Sony / AirPods / Galaxy Buds | boAt / pTron / Budget Brands |
| :--- | :--- | :--- |
| 🎧 ANC Control | ✅ Fully Supported | 🔒 Greyed Out (Not Supported) |
| 🔋 Battery Monitor | ✅ Fully Supported | 🔒 Greyed Out (Not Supported) |
| 🔊 Per-App Audio Mixer | ✅ Works for All Devices | ✅ Works for All Devices |
| 🎙️ Per-App Mic Control | ✅ Works for All Devices | ✅ Works for All Devices |
| ⌨️ Global Hotkeys | ✅ Works for All Devices | ✅ Works for All Devices |
| 🗣️ Voice + HUD Slang | ✅ Works for All Devices | ✅ Works for All Devices |

**Greyed-out message (Punjabi Mode):** *"Tera headphone yeh feature support nahi karta bhai! 😄"*

```python
class BoatGenericDriver(BaseDriver):
    CAPABILITIES = {
        "anc_control":     False,   # ❌ Not supported
        "battery_monitor": False,   # ❌ Not supported
        "audio_mixer":     True,    # ✅ OS-level, works always
        "mic_control":     True,    # ✅ OS-level, works always
    }
```

---

## 🔬 Community Reverse-Engineering Module (Future)

For unknown / budget brand headphones (boAt, pTron, Noise, etc.), KaanShield includes a **Packet Sniffer Mode**:
* Captures raw Bluetooth command traffic when official app buttons are pressed.
* Community members can submit discovered byte payloads to add support for new brands.
* This is how open source projects like `SonyHeadphonesClient` and `GalaxyBudsClient` grew their device support over time.

---

## 🗺️ Implementation Roadmap (4 Phases)

* **Phase 1: Core Engine, System Tray UI, Glassmorphism Dashboard & Virtual Simulator (`MockDriver`)**
* **Phase 2: Slang HUD Overlay Banner, Voice Engine (Punjabi/Haryanvi/Bhojpuri/Desi) & Global Hotkeys**
* **Phase 3: Per-App Audio/Mic Stream Mixer, CapabilityFlags System & Hardware Bluetooth Drivers**
* **Phase 4: Executable Packaging (`KaanShield.exe` & `KaanShield.AppImage`) + Community Reverse-Engineering Module**
