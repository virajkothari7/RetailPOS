; Inno Setup script - wraps the PyInstaller dist\RetailPOS\ folder into a
; proper Windows installer (Start Menu shortcut, uninstaller, Program Files
; install). Optional, but this is what you hand a client instead of a raw
; folder or a zip.
;
; Requires: Inno Setup (https://jrsoftware.org/isinfo.php), free.
; Build dist\RetailPOS\ first (packaging\build_windows.ps1), THEN compile
; this script with the Inno Setup Compiler (or `iscc RetailPOS_installer.iss`).

#define MyAppName "RetailPOS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "RetailPOS.exe"

[Setup]
AppId={{B6B2B6A0-6C7C-4C9B-9F1A-RETAILPOS001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Each client install keeps its own data/ folder (sales, inventory, shift
; history) inside the install directory - do NOT let the uninstaller nuke it.
OutputBaseFilename=RetailPOS_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
; Pulls in everything PyInstaller produced in dist\RetailPOS\
Source: "..\dist\RetailPOS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Leave {app}\data, {app}\logsKivy, {app}\variable.txt alone on uninstall so a
; reinstall/upgrade doesn't wipe the till's sales history. If the client
; explicitly wants a clean wipe, delete those by hand after uninstalling.
