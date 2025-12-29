; Okul Zil Programı - Inno Setup Script
; Windows 10+ için profesyonel okul zil sistemi

#define MyAppName "Okul Zil Programı"
#define MyAppVersion "1.0"
#define MyAppPublisher "Okul Zil Ekibi"
#define MyAppURL "https://github.com/okulzil"
#define MyAppExeName "OkulZil.exe"

[Setup]
; Uygulama bilgileri
AppId={{8F3A2B1C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Çıktı dosyası
OutputDir=.
OutputBaseFilename=OkulZil_Setup_v{#MyAppVersion}
; Sıkıştırma
Compression=lzma
SolidCompression=yes
; Görünüm
WizardStyle=modern
; Dil
ShowLanguageDialog=no
; Admin yetkisi gerektirme
PrivilegesRequired=lowest
; Kaldırma bilgileri
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Windows başlangıcında otomatik başlat"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ana EXE dosyası
Source: "dist\OkulZil.exe"; DestDir: "{app}"; Flags: ignoreversion
; Data klasörü
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
; Sounds klasörü
Source: "sounds\*"; DestDir: "{app}\sounds"; Flags: ignoreversion recursesubdirs createallsubdirs
; Logs klasörü (boş)
Source: "logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Başlat menüsü
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Masaüstü ikonu (opsiyonel)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Başlangıç klasörü (opsiyonel)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; Kurulum sonrası programı çalıştır
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// Kurulum öncesi kontroller
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Windows 10+ kontrolü
  if not (GetWindowsVersion >= $0A000000) then
  begin
    MsgBox('Bu program Windows 10 veya üzeri sürümler için tasarlanmıştır.', mbError, MB_OK);
    Result := False;
  end;
end;


