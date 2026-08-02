<div align="center">

# 🛡️ KAANSHIELD
### *Nuke the Noise. Protect the Vibe.*

[![Windows 11 Support](https://img.shields.io/badge/Windows-10%20%2F%2011%20Supported-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/jayesh-RN/KaanShield)
[![Linux Pending](https://img.shields.io/badge/Linux-Coming%20Soon-FCC624?style=for-the-badge&logo=linux&logoColor=black)](#-os-compatibility)
[![PySide6 GUI](https://img.shields.io/badge/GUI-PySide6%20Glassmorphism-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pyside.org)
[![Build Status](https://img.shields.io/badge/Release-v1.0.0%20Ready-f97316?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/jayesh-RN/KaanShield/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

<br/>

<img src="assets/icons/app_logo.png" width="220" alt="KaanShield 3D Cybernetic Shield Logo"/>

<br/>

*The ultimate desktop command center for Bluetooth headphones & earphones.*  
*Real-time ambient sound passthrough, software ANC noise suppression, WASAPI per-app mixer, dynamic battery telemetry, and slang voice feedback!*

---

</div>

<br/>

> [!IMPORTANT]
> **🚀 1-CLICK DOWNLOAD READY:** No Python or setup required! Download **[KaanShield_Setup_v1.0.exe](https://github.com/jayesh-RN/KaanShield/releases/tag/v1.0.0)** or **`KaanShield_v1.0_Windows.zip`** directly from our **[v1.0.0 Release Page](https://github.com/jayesh-RN/KaanShield/releases/tag/v1.0.0)** and run instantly!

<br/>

---

## ⚡ Why KaanShield?

Standard Windows Bluetooth controls suck. Budget Bluetooth earphones (boAt, Noise, Zebronics, Portronics, pTron) don't have desktop apps, and Windows offers zero sidetone/passthrough options. **KaanShield fixes this.**

```text
 ╔═════════════════════════════════════════════════════════════════════════════╗
 ║  👤 REAL-TIME TRANSPARENCY    Sub-10ms Mic-to-Speaker Sidetone Passthrough ║
 ║  📶 SOFTWARE ANC (FFT DSP)    Low-Pass Equalizer Noise & Hiss Suppression   ║
 ║  🎛️ WASAPI PER-APP MIXER      Control Master & Individual App Volumes Live   ║
 ║  🔋 DYNAMIC BATTERY TELEMETRY Real-time Left (L) & Right (R) Earbud Badges  ║
 ║  🗣️ SLANG VOICE CUES         Hindi/Tapori & English Voice Feedback Lines   ║
 ╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## 🖥️ OS Compatibility & System Matrix

| OS Platform | Compatibility | Real-Time Passthrough | Software ANC DSP | WASAPI Mixer |
| :--- | :---: | :---: | :---: | :---: |
| **Windows 11** | 🟢 **100% Active** | 🟢 Sub-10ms | 🟢 Active | 🟢 Native |
| **Windows 10** | 🟢 **100% Active** | 🟢 Sub-10ms | 🟢 Active | 🟢 Native |
| **Linux (Ubuntu / Arch)** | 🟡 **Pending** | ⏳ PipeWire | ⏳ PulseDSP | ⏳ ALSA |
| **macOS** | 🔴 **Unsupported** | ❌ | ❌ | ❌ |

---

## 🌟 Feature Breakdown

<details>
<summary><b>👤 1. Real-Time Environmental Passthrough (Transparency Mode)</b></summary>
<br/>

Using `sounddevice` low-latency callback streams, KaanShield captures ambient room sounds from your microphone and feeds them **directly into your earphone speakers with <10ms delay**.
* **Ambient Slider (0 - 20):** Adjust real-time microphone gain multiplier dynamically (`0.5x` to `4.0x`).
</details>

<details>
<summary><b>📶 2. Software Active Noise Cancellation (FFT DSP Suppression)</b></summary>
<br/>

Applies real-time Fast Fourier Transform (`numpy.fft`) filtering to suppress background HVAC, fan hums (50Hz–250Hz), and high-frequency hiss from output audio.
* **Auto-Cutoff:** Automatically cuts off microphone passthrough when switching to ANC ON mode.
</details>

<details>
<summary><b>🎛️ 3. Windows WASAPI Per-App Audio & Master Mixer</b></summary>
<br/>

Powered by `pycaw`, control real Windows master volume and individual applications (Chrome, Spotify, Discord, Games) in real time.
* **Live Mute Buttons:** Click `🎙️ Active` to mute (`🚫 Muted`) with instant visual color updates.
</details>

<details>
<summary><b>🔋 4. Live Dynamic System Battery Telemetry</b></summary>
<br/>

Queries Windows PnP & WMI system endpoints dynamically with zero hardcoded fallbacks.
* Top status badges update Left (`L 90% 🟢`) and Right (`R 90% 🟢`) earbud telemetry live on every scan click.
</details>

<details>
<summary><b>🗣️ 5. Hindi (Tapori) & English Slang Voice Cues</b></summary>
<br/>

Custom recorded slang audio cues play directly inside your connected Bluetooth headphones:
* **ANC ON:** *"अबे शोर बंद! फुल शांति!"*
* **Transparency:** *"दुनिया की बात सुनने का है भइया!"*
* **ANC OFF:** *"नॉर्मल मोड चालू हो गया बॉस!"*
</details>

---

## 📦 Download & 1-Click Installation

### 💿 Method 1: 1-Click Windows Setup Installer (Recommended)
Download **[KaanShield_Setup_v1.0.exe](https://github.com/jayesh-RN/KaanShield/releases/tag/v1.0.0)** directly from **[Release v1.0.0 Page](https://github.com/jayesh-RN/KaanShield/releases/tag/v1.0.0)**.
* Standard Windows Setup Wizard (*Next -> Next -> Finish*).
* Automatically creates Desktop Icon, Start Menu Shortcut, and optional Windows Startup entry.

### 📂 Method 2: 1-Click Portable Zip Package
Download **[KaanShield_v1.0_Windows.zip](https://github.com/jayesh-RN/KaanShield/releases/tag/v1.0.0)**.
* Unzip to any folder and double-click **`KaanShield.exe`**.
* No installation required!

### 💻 Method 3: Run from Source (Developers)

```powershell
# Clone the repository
git clone https://github.com/jayesh-RN/KaanShield.git
cd KaanShield

# Install dependencies
pip install -r requirements.txt

# Launch KaanShield
python main.py
```

---

## ⌨️ Global Keyboard Hotkeys

| Shortcut | Action | Mode Target |
| :--- | :--- | :--- |
| `Ctrl` + `Alt` + `A` | **Toggle ANC On/Off** | `ANC_ON` / `ANC_OFF` |
| `Ctrl` + `Alt` + `T` | **Toggle Transparency On/Off** | `TRANSPARENCY` / `ANC_OFF` |
| `Ctrl` + `Alt` + `O` | **Turn All Off** | `ANC_OFF` |
| `Ctrl` + `Alt` + `M` | **Mute / Unmute Microphone** | Global Mic Mute |

---

## 📚 Deep-Dive Developer Documentation (`docs/`)

For developer deep-dives, read our comprehensive guides in the [`docs/`](docs/) folder:

1. 🧠 **[01. High-Level Architecture & System Design](docs/01_ARCHITECTURE_OVERVIEW.md)**
2. 🎙️ **[02. Audio Passthrough & Software ANC DSP](docs/02_AUDIO_PASSTHROUGH_AND_DSP.md)**
3. 🎛️ **[03. Windows Audio Session API (WASAPI) & Volume Mixer](docs/03_WINDOWS_AUDIO_MIXER_WASAPI.md)**
4. 🔋 **[04. Bluetooth Scanning & Dynamic Battery Telemetry](docs/04_BLUETOOTH_AND_BATTERY_TELEMETRY.md)**
5. 🗣️ **[05. PySide6 GUI & Voice Engine](docs/05_GUI_AND_VOICE_ENGINE.md)**

---

## 📜 License & Credits

Distributed under the MIT License. See `LICENSE` for details.  
Built with ❤️ by the KaanShield Engineering Team.
