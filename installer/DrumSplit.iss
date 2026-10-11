#define MyAppName "DrumSplit"
#define MyAppVersion "0.2.2"
#define MyAppPublisher "Sufyan Nasser Ali"
#define MyAppExeName "DrumSplit.exe"

[Setup]
AppId={{C9805A92-2C3F-4B45-9B65-9B6195CF7C71}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DrumSplit
DefaultGroupName=DrumSplit
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=DrumSplit-Setup-0.2.2-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\DrumSplit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\DrumSplit"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DrumSplit"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch DrumSplit"; Flags: nowait postinstall skipifsilent
