# 📐 KaanShield — Engineering Standards & Rules

> **This document is the law of the codebase.**
> Every single file, function, class, and commit in KaanShield must follow these rules.
> No exceptions. No shortcuts. Clean code only.

---

## 📁 1. File & Folder Structure Rules

### Rule 1.1 — Strict Directory Ownership
Every folder has **one job only**. Never mix concerns across folders.

```text
KaanShield/
├── main.py               ← ONLY bootstrapping. No business logic here.
├── requirements.txt      ← ONLY dependencies. Nothing else.
├── config.json           ← ONLY user settings. Auto-generated. Never edit manually.
├── PRODUCT_PLAN.md       ← Product documentation. Never mix with code.
├── STANDARDS.md          ← This file. Engineering rules.
│
├── assets/               ← ONLY static assets (icons, sounds, images)
│   ├── icons/            ← App icons (.ico for Windows, .png for Linux)
│   ├── sounds/           ← Cached TTS audio files (.mp3)
│   └── fonts/            ← Custom fonts if any
│
├── core/                 ← ONLY business logic. No UI code allowed here.
│   ├── app_controller.py ← Central state brain. Emits signals. No Bluetooth code.
│   ├── bluetooth_manager.py  ← ONLY connection lifecycle. No UI code.
│   ├── audio_mixer.py    ← ONLY OS audio stream APIs. No UI code.
│   ├── voice_engine.py   ← ONLY TTS + audio playback. No UI code.
│   ├── hotkey_manager.py ← ONLY OS hotkey listener. No UI code.
│   └── config_manager.py ← ONLY JSON read/write. No UI code.
│
├── drivers/              ← ONLY Bluetooth device protocol code.
│   ├── base_driver.py    ← Abstract base class ONLY. No implementation.
│   ├── mock_driver.py    ← ONLY fake simulator logic.
│   ├── generic_driver.py ← ONLY fallback for unknown devices.
│   ├── sony_driver.py    ← ONLY Sony RFCOMM protocol.
│   ├── airpods_driver.py ← ONLY AirPods BLE GATT protocol.
│   └── galaxy_buds_driver.py ← ONLY Galaxy Buds SPP protocol.
│
└── ui/                   ← ONLY visual components. No business logic allowed here.
    ├── tray_app.py       ← ONLY system tray icon and context menu.
    ├── dashboard_window.py  ← ONLY the main window and tabs.
    ├── hud_overlay.py    ← ONLY the on-screen slang banner.
    └── styles.qss        ← ONLY QSS CSS styles. No Python logic.
```

### Rule 1.2 — File Naming
* All Python files: `snake_case.py` ✅ (`audio_mixer.py`)
* All asset files: `snake_case.ext` ✅ (`anc_on_punjabi.mp3`)
* All doc files: `UPPER_SNAKE_CASE.md` ✅ (`PRODUCT_PLAN.md`)
* Never use spaces or hyphens in filenames ❌ (`audio mixer.py`, `audio-mixer.py`)

---

## 🐍 2. Python Code Style Rules

### Rule 2.1 — Follow PEP 8 Always
* **Indentation:** 4 spaces. Never tabs.
* **Max line length:** 100 characters. Break long lines.
* **Blank lines:** 2 blank lines between top-level class/function definitions. 1 blank line between methods inside a class.

### Rule 2.2 — Type Hints are Mandatory
Every function must have full type hints on all parameters and return values.

```python
# ✅ CORRECT
async def set_anc_mode(self, mode: str) -> bool:
    ...

def get_voice_line(language: str, event: str) -> str:
    ...

# ❌ WRONG — no type hints
async def set_anc_mode(self, mode):
    ...
```

### Rule 2.3 — Docstrings are Mandatory
Every class and every public method must have a docstring.

```python
# ✅ CORRECT
class SonyDriver(BaseHeadphoneDriver):
    """
    Bluetooth driver for Sony WH/WF headphone series.
    Communicates via RFCOMM (Serial Port Profile) using Sony's proprietary byte protocol.
    Compatible: WH-1000XM3, XM4, XM5, WF-1000XM4, WF-1000XM5.
    """

    async def set_anc_mode(self, mode: str) -> bool:
        """
        Send an ANC mode command to the headphone via RFCOMM socket.

        Args:
            mode: One of 'ANC_ON', 'TRANSPARENCY', 'ANC_OFF'

        Returns:
            True if command was sent successfully, False otherwise.
        """

# ❌ WRONG — no docstring
class SonyDriver(BaseHeadphoneDriver):
    async def set_anc_mode(self, mode: str) -> bool:
        ...
```

### Rule 2.4 — No Magic Numbers or Magic Strings
Never hardcode raw bytes, numbers, or strings inline. Always define them as named constants at the top of the file.

```python
# ✅ CORRECT — constants are self-documenting
SONY_HANDSHAKE_PACKET   = bytes([0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00])
SONY_ANC_ON_PAYLOAD     = bytes([0x3E, 0x0C, 0x00, 0x00, 0x00, 0x0C, 0x4A, 0x01, 0x02])
SONY_TRANSPARENCY_PAYLOAD = bytes([0x3E, 0x0C, 0x00, 0x00, 0x00, 0x0C, 0x4A, 0x01, 0x11])
SONY_ANC_OFF_PAYLOAD    = bytes([0x3E, 0x0C, 0x00, 0x00, 0x00, 0x0C, 0x4A, 0x01, 0x00])

LOW_BATTERY_THRESHOLD   = 20  # percent
HUD_DISPLAY_DURATION_MS = 2500

# ❌ WRONG — magic bytes inline
await socket.send(bytes([0x3E, 0x0C, 0x00, 0x00, 0x00, 0x0C, 0x4A, 0x01, 0x02]))
```

### Rule 2.5 — No print() in Production Code
* Use Python's `logging` module everywhere. Never `print()`.
* Log levels: `DEBUG` for low-level detail, `INFO` for state changes, `WARNING` for soft failures, `ERROR` for hard failures.

```python
import logging
logger = logging.getLogger(__name__)

# ✅ CORRECT
logger.info("ANC mode changed to: %s", mode)
logger.error("Bluetooth connection failed for device: %s", device_name)

# ❌ WRONG
print(f"ANC mode changed to: {mode}")
```

### Rule 2.6 — Constants use UPPER_SNAKE_CASE
```python
# ✅ CORRECT
MAX_AMBIENT_LEVEL = 20
DEFAULT_LANGUAGE  = "punjabi"
HUD_FADE_DURATION = 250  # ms

# ❌ WRONG
maxAmbientLevel = 20
default_language = "punjabi"
```

### Rule 2.7 — Classes use PascalCase, Functions use snake_case
```python
# ✅ CORRECT
class SonyDriver:
    async def set_anc_mode(self):
        ...

# ❌ WRONG
class sony_driver:
    async def SetAncMode(self):
        ...
```

---

## 🏗️ 3. Low-Level Design (LLD) Rules

### Rule 3.1 — Single Responsibility Principle (SRP)
Every class does **exactly one thing**.

```python
# ✅ CORRECT — SonyDriver only handles Sony Bluetooth protocol
class SonyDriver(BaseHeadphoneDriver):
    async def set_anc_mode(self, mode: str): ...
    async def get_battery(self) -> dict: ...

# ❌ WRONG — mixing Bluetooth + UI in one class
class SonyDriver:
    async def set_anc_mode(self): ...
    def update_ui_label(self): ...  # ← UI code doesn't belong in driver!
```

### Rule 3.2 — Dependency Injection (DI)
Never instantiate dependencies inside a class. Pass them in via the constructor.

```python
# ✅ CORRECT — dependencies injected from outside
class AppController(QObject):
    def __init__(self, config: ConfigManager, driver: BaseHeadphoneDriver,
                 voice: VoiceEngine, mixer: AudioMixer):
        self.config = config
        self.driver = driver
        self.voice  = voice
        self.mixer  = mixer

# ❌ WRONG — creating dependencies inside the class (hard to test, hard to swap)
class AppController(QObject):
    def __init__(self):
        self.config = ConfigManager()       # ← tightly coupled!
        self.driver = SonyDriver()          # ← what if we want AirPods?
        self.voice  = VoiceEngine()
```

### Rule 3.3 — Always Use the Abstract Base Class (ABC) for Drivers
The rest of the app only ever types against `BaseHeadphoneDriver`. Never import a concrete driver directly into UI or core modules.

```python
# ✅ CORRECT — type hint uses the abstract base
def __init__(self, driver: BaseHeadphoneDriver):
    self.driver = driver

# ❌ WRONG — tied to a specific brand
def __init__(self, driver: SonyDriver):
    self.driver = driver
```

### Rule 3.4 — All Cross-Thread Communication via Qt Signals
The Bluetooth background thread must never directly call UI methods. Always use Qt Signals.

```python
# ✅ CORRECT — safe cross-thread event
class BluetoothWorker(QThread):
    battery_received = Signal(dict)

    def _on_battery_event(self, data: dict):
        self.battery_received.emit(data)  # Qt handles thread safety

# ❌ WRONG — calling UI directly from background thread (will crash!)
class BluetoothWorker(QThread):
    def _on_battery_event(self, data: dict):
        self.ui_label.setText(str(data["left"]))  # ← CRASH
```

### Rule 3.5 — Async/Await for ALL Bluetooth Operations
All driver methods that do Bluetooth I/O must be `async`. Never do blocking I/O on the main thread.

```python
# ✅ CORRECT
async def set_anc_mode(self, mode: str) -> bool:
    await self.socket.send(SONY_ANC_PAYLOADS[mode])
    return True

# ❌ WRONG — blocking call on main thread freezes entire UI
def set_anc_mode(self, mode: str):
    self.socket.send(SONY_ANC_PAYLOADS[mode])  # blocks!
```

---

## 🎨 4. UI / QSS Styling Rules

### Rule 4.1 — All Styles Go in `styles.qss` Only
Never write inline styles using `setStyleSheet()` in Python code for component-level styles.

```python
# ✅ CORRECT — load styles centrally once in main.py
with open("ui/styles.qss", "r") as f:
    app.setStyleSheet(f.read())

# ❌ WRONG — inline styles scattered everywhere
self.button.setStyleSheet("background-color: #7c3aed; border-radius: 8px;")
```

### Rule 4.2 — Use Object Names for QSS Targeting
Use `setObjectName()` to give widgets specific CSS-style IDs, then target them in `styles.qss`.

```python
# Python:
self.anc_button = QPushButton("ANC ON")
self.anc_button.setObjectName("ancOnButton")  # ← sets the "id"

# styles.qss:
# QPushButton#ancOnButton { background: #7c3aed; border-radius: 10px; }
```

### Rule 4.3 — Design Token Variables (Keep Colors Consistent)
Define the color palette at the top of `styles.qss` as a reference comment block. Never use a raw color hex code without referencing this palette.

```css
/*
  KaanShield Design Tokens
  ========================
  Background Primary:  #0a0a12
  Background Panel:    rgba(255,255,255,0.05)
  Accent Purple:       #7c3aed
  Accent Glow:         #5b21b6
  Text Primary:        #f8fafc
  Text Secondary:      #94a3b8
  Success Green:       #22c55e
  Warning Yellow:      #eab308
  Error Red:           #ef4444
  Border:              rgba(255,255,255,0.10)
  Border Radius:       12px
*/
```

---

## 🗣️ 5. Voice Engine Content Rules

### Rule 5.1 — All Voice Lines in One Central File
All language strings live in `core/voice_engine.py` in the `VOICE_LINES` dictionary. Never hardcode voice strings anywhere else.

### Rule 5.2 — All Languages Must Have the Same Events
Every language entry must define voice lines for all 6 events:
`ANC_ON`, `TRANSPARENCY`, `ANC_OFF`, `MIC_MUTED`, `CONNECTED`, `LOW_BATTERY`

```python
# ✅ CORRECT — all 6 events defined
"punjabi": {
    "ANC_ON":       "...",
    "TRANSPARENCY": "...",
    "ANC_OFF":      "...",
    "MIC_MUTED":    "...",
    "CONNECTED":    "...",
    "LOW_BATTERY":  "...",
}

# ❌ WRONG — missing events will cause KeyError crashes
"punjabi": {
    "ANC_ON": "...",
    "MIC_MUTED": "...",
}
```

---

## ✅ 6. Git Commit Message Rules

Every commit message must follow the **Conventional Commits** format:

```
<type>(<scope>): <short description>
```

### Allowed Types:
| Type | When to Use |
| :--- | :--- |
| `feat` | Adding a new feature |
| `fix` | Fixing a bug |
| `refactor` | Restructuring code (no behavior change) |
| `style` | CSS/QSS styling changes only |
| `docs` | Documentation changes only |
| `test` | Adding or updating tests |
| `chore` | Build scripts, configs, dependencies |

### Examples:
```bash
# ✅ CORRECT
git commit -m "feat(drivers): add Sony WH-1000XM5 RFCOMM driver"
git commit -m "feat(voice): add Haryanvi language voice lines"
git commit -m "fix(hud): fix HUD banner not dismissing on second toggle"
git commit -m "style(dashboard): update ANC button glassmorphism glow effect"
git commit -m "docs: update PRODUCT_PLAN.md with CapabilityFlags section"

# ❌ WRONG
git commit -m "updated stuff"
git commit -m "fixed bug"
git commit -m "changes"
```

---

## 🧪 7. Testing Rules

### Rule 7.1 — Always Test with MockDriver First
Before testing with real Bluetooth hardware, all features must pass fully with `MockDriver`. If it breaks with `MockDriver`, it will definitely break with real hardware.

### Rule 7.2 — Test on Both Windows and Linux
Every new feature must be tested on both platforms before it's considered done.

### Rule 7.3 — No Feature is Done Until It Handles Errors Gracefully
Every driver call must be wrapped in a try/except. Bluetooth can fail at any time (device turned off, out of range). The app must never crash — it must show a clean error state.

```python
# ✅ CORRECT
try:
    await self.driver.set_anc_mode(mode)
    logger.info("ANC mode set to: %s", mode)
except Exception as e:
    logger.error("Failed to set ANC mode: %s", e)
    self.show_error_notification("Could not change ANC mode. Is your device connected?")

# ❌ WRONG — unhandled exception will crash the whole app
await self.driver.set_anc_mode(mode)
```

---

## 🔐 8. Config & Security Rules

### Rule 8.1 — Never Hardcode Bluetooth MAC Addresses
MAC addresses are user-specific and must always be stored in `config.json`. Never hardcode them.

### Rule 8.2 — Never Commit `config.json` to Git
Add `config.json` to `.gitignore`. It contains user-specific device pairing information.

```gitignore
# .gitignore
config.json
__pycache__/
*.pyc
dist/
build/
*.spec
assets/sounds/*.mp3   ← generated TTS cache files, don't commit
```
