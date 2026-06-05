$ErrorActionPreference = "Stop"

$LauncherDir = $PSScriptRoot
$ProjectRoot = Split-Path $LauncherDir -Parent
$TargetExe = Join-Path $LauncherDir "target\release\statz_gui.exe"
$OutputExe = Join-Path $ProjectRoot "statz_gui.exe"
$IconPath = Join-Path $ProjectRoot "icon\icon.ico"
$Rcedit = Join-Path $LauncherDir "tools\rcedit-x64.exe"
$RceditUrl = "https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe"

if (-not (Test-Path $IconPath)) {
    $JpgPath = Join-Path $ProjectRoot "icon\icon.jpg"
    if (-not (Test-Path $JpgPath)) {
        throw "Icon not found: expected icon\icon.ico or icon\icon.jpg"
    }

    python -c "from PIL import Image; img=Image.open(r'$JpgPath').convert('RGBA'); img.save(r'$IconPath', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
}

Write-Host "Building statz_gui..."
Push-Location $LauncherDir
cargo build --release --target-dir ./target
Pop-Location

if (-not (Test-Path $TargetExe)) {
    throw "Build failed: $TargetExe not found"
}

if (-not (Test-Path $Rcedit)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $Rcedit -Parent) | Out-Null
    Write-Host "Downloading rcedit..."
    Invoke-WebRequest -Uri $RceditUrl -OutFile $Rcedit
}

Write-Host "Applying icon..."
& $Rcedit $TargetExe --set-icon $IconPath

Copy-Item $TargetExe $OutputExe -Force
Write-Host "Done: $OutputExe"
