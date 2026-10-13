$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
if (-not [Environment]::Is64BitOperatingSystem) { throw 'Este necesar Windows x64.' }
$root = Join-Path $env:LOCALAPPDATA 'APK-Lens-Builder'
New-Item -ItemType Directory -Force $root | Out-Null
Set-Location $root

function Download($url, $path) {
    Write-Host "Descarc: $url"
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $path
}
function Check($action) {
    if ($LASTEXITCODE -ne 0) { throw "$action a esuat (cod $LASTEXITCODE)." }
}

# Codul sursa al aplicatiei, inclus in script ca arhiva ZIP Base64.
$source = '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'
[IO.File]::WriteAllBytes((Join-Path $root 'source.zip'), [Convert]::FromBase64String($source))
Expand-Archive -Force 'source.zip' 'src'

# Foloseste Python x64 cu Tkinter, daca exista deja.
$python = $null
if ($env:pythonLocation) { $python = Join-Path $env:pythonLocation 'python.exe' }
if (-not $python -and (Get-Command py -ErrorAction SilentlyContinue)) {
    $candidate = & py -3 -c 'import tkinter,struct,sys; assert struct.calcsize(chr(80))==8; print(sys.executable)' 2>$null
    if ($LASTEXITCODE -eq 0) { $python = ($candidate | Select-Object -Last 1) }
}
if (-not $python -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $candidate = & python -c 'import tkinter,struct,sys; assert struct.calcsize(chr(80))==8; print(sys.executable)' 2>$null
    if ($LASTEXITCODE -eq 0) { $python = ($candidate | Select-Object -Last 1) }
}
if (-not $python) {
    Download 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' 'python-setup.exe'
    $signature = Get-AuthenticodeSignature '.\python-setup.exe'
    if ($signature.Status -ne 'Valid') { throw 'Semnatura installerului Python nu este valida.' }
    Write-Host 'Instalez Python pentru construirea aplicatiei...'
    $target = Join-Path $root 'python'
    $proc = Start-Process '.\python-setup.exe' -ArgumentList "/quiet InstallAllUsers=0 TargetDir=`"$target`" Include_launcher=0 Include_tcltk=1 Include_pip=1 Include_test=0 AssociateFiles=0 Shortcuts=0 PrependPath=0" -PassThru -Wait
    if ($proc.ExitCode -notin @(0,3010)) { throw "Python setup: $($proc.ExitCode)" }
    $python = Join-Path $target 'python.exe'
    if (-not (Test-Path $python)) { throw 'Python nu este disponibil. Instaleaza Python x64 cu Tkinter si reincearca.' }
}
& $python -m venv (Join-Path $root 'venv')
Check 'Crearea mediului Python'
$buildPython = Join-Path $root 'venv\Scripts\python.exe'
& $buildPython -m pip install 'pyinstaller==6.16.0'
Check 'Instalarea PyInstaller'

Download 'https://github.com/skylot/jadx/releases/download/v1.5.6/jadx-1.5.6.zip' 'jadx.zip'
$tools = Join-Path $root 'src\tools'
New-Item -ItemType Directory -Force $tools | Out-Null
Expand-Archive -Force 'jadx.zip' (Join-Path $tools 'jadx')
$releases = Invoke-RestMethod 'https://api.adoptium.net/v3/assets/latest/17/hotspot?architecture=x64&image_type=jre&os=windows'
$java = @($releases)[0].binary.package
Download $java.link 'java.zip'
if ((Get-FileHash 'java.zip' -Algorithm SHA256).Hash -ne $java.checksum) { throw 'Checksum Java invalid.' }
$javaTemp = Join-Path $root 'java-unpack'
if (Test-Path $javaTemp) { Remove-Item -Recurse -Force $javaTemp }
Expand-Archive 'java.zip' $javaTemp
$javaFolder = Get-ChildItem $javaTemp -Directory | Select-Object -First 1
$javaTarget = Join-Path $tools 'java'
if (Test-Path $javaTarget) { Remove-Item -Recurse -Force $javaTarget }
Move-Item $javaFolder.FullName $javaTarget

& $buildPython -m PyInstaller --noconfirm --clean --onedir --windowed --name APK-Lens --add-data "$tools;tools" 'src\launch.pyw'
Check 'Construirea APK-Lens.exe'

$compilerPath = Join-Path ${env:ProgramFiles(x86)} 'NSIS\makensis.exe'
if (-not (Test-Path $compilerPath)) {
    Download 'https://downloads.sourceforge.net/project/nsis/NSIS%203/3.11/nsis-3.11.zip' 'nsis.zip'
    Expand-Archive -Force 'nsis.zip' 'nsis'
    $compiler = Get-ChildItem 'nsis' -Filter makensis.exe -Recurse | Select-Object -First 1
    if (-not $compiler) { throw 'Compilatorul NSIS nu a fost gasit.' }
    $compilerPath = $compiler.FullName
}

$nsi = @'
Unicode true
!include "MUI2.nsh"
!include "x64.nsh"
Name "APK Lens"
OutFile "APK-Lens-Setup-x64.exe"
InstallDir "$LOCALAPPDATA\Programs\APK Lens"
RequestExecutionLevel user
SetCompressor /SOLID lzma
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Romanian"
Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "Este necesar Windows x64."
    Abort
  ${EndIf}
FunctionEnd
Section
  SetOutPath "$INSTDIR"
  File /r "dist\APK-Lens\*"
  CreateDirectory "$SMPROGRAMS\APK Lens"
  CreateShortcut "$SMPROGRAMS\APK Lens\APK Lens.lnk" "$INSTDIR\APK-Lens.exe"
  CreateShortcut "$DESKTOP\APK Lens.lnk" "$INSTDIR\APK-Lens.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\APK Lens" "DisplayName" "APK Lens"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\APK Lens" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\APK Lens" "DisplayVersion" "0.1.0"
SectionEnd
Section "Uninstall"
  Delete "$DESKTOP\APK Lens.lnk"
  RMDir /r "$SMPROGRAMS\APK Lens"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\APK Lens"
  RMDir /r "$INSTDIR"
SectionEnd
'@
[IO.File]::WriteAllText((Join-Path $root 'setup.nsi'), $nsi, (New-Object Text.UTF8Encoding($true)))
& $compilerPath 'setup.nsi'
Check 'Construirea installerului'
$desktop = [Environment]::GetFolderPath('Desktop')
$result = Join-Path $desktop 'APK-Lens-Setup-x64.exe'
Copy-Item -Force 'APK-Lens-Setup-x64.exe' $result
Write-Host "GATA: $result" -ForegroundColor Green
Write-Host 'Installerul include aplicatia, Java si JADX. Nu este semnat digital.'
