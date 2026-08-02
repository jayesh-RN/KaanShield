; Inno Setup Script for KaanShield — Nuke the Noise. Protect the Vibe.
; Compiles dist/KaanShield into a professional 1-Click KaanShield_Setup.exe Installer.

#define MyAppName "KaanShield"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "KaanShield Dev Team"
#define MyAppURL "https://github.com/your-username/KaanShield"
#define MyAppExeName "KaanShield.exe"

[Setup]
AppId={{D37E8F9A-4B2C-4E1D-9F8A-6C5B4A3D2E1F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=KaanShield_Setup_v1.0
SetupIconFile=assets\icons\app_logo.ico
UninstallDisplayIcon={app}\assets\icons\app_logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Launch KaanShield automatically on Windows Startup"; GroupDescription: "Windows Startup Options:"

[Files]
Source: "dist\KaanShield\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\app_logo.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\app_logo.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\app_logo.ico"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
