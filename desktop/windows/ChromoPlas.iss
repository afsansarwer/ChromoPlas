#define AppVersion "0.1.0"
[Setup]
AppId={{96177DF9-C4F6-4C4E-949B-A6E432DE37ED}
AppName=ChromoPlas Desktop Preview
AppVersion={#AppVersion}
AppPublisher=Afsan Sarwer
AppPublisherURL=https://github.com/afsansarwer/ChromoPlas
DefaultDirName={localappdata}\Programs\ChromoPlas
DefaultGroupName=ChromoPlas
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19045
OutputDir=..\..\dist\desktop
OutputBaseFilename=ChromoPlas-Setup-{#AppVersion}-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\..\LICENSE
UninstallDisplayIcon={app}\ChromoPlas.exe
CloseApplications=yes

[Files]
Source: "..\..\dist\desktop\ChromoPlas.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\docs\windows-desktop.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Icons]
Name: "{group}\ChromoPlas"; Filename: "{app}\ChromoPlas.exe"
Name: "{autodesktop}\ChromoPlas"; Filename: "{app}\ChromoPlas.exe"; Tasks: desktopicon
Name: "{group}\Uninstall ChromoPlas"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\ChromoPlas.exe"; Description: "Open ChromoPlas and set up the analysis engine"; Flags: nowait postinstall skipifsilent

; Uninstall removes only the Windows application. It deliberately preserves
; the WSL engine, databases, setup logs and the user's result folders.
