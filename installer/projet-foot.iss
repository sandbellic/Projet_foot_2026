#ifndef MyAppVersion
#define MyAppVersion "0.0.0"
#endif

[Setup]
AppName=Projet mondial de foot
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\ProjetFoot
DefaultGroupName=Projet Foot

OutputDir=..\dist
OutputBaseFilename=ProjetFoot-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\projet-foot.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DProjet Foot"; Filename: "{app}\projet-foot.exe"
Name: "{autodesktop}\Projet Foot"; Filename: "{app}\projet-foot.exe"

[Run]
Filename: "{app}\projet-foot.exe"; Description: "Lancer Projet Foot"; Flags: nowait postinstall skipifsilent