$ErrorActionPreference = "Stop"

Write-Host "Building PortPilot for Windows..." -ForegroundColor Cyan

# Install PyInstaller and Pillow if not present
pip install pyinstaller Pillow

# Generate ICO from PNG (required for Windows executable icon)
python -c "from PIL import Image; import os; img = Image.open('resources/icons/tray_icon.png'); img.save('resources/icons/tray_icon.ico', format='ICO', sizes=[(256, 256)])"

# Build executable
pyinstaller `
    --name "PortPilot" `
    --onefile `
    --windowed `
    --icon "resources/icons/tray_icon.ico" `
    --add-data "src/ui/styles;src/ui/styles" `
    --add-data "resources;resources" `
    src/main.py

# Check if build was successful
if (-not (Test-Path "dist/PortPilot.exe")) {
    Write-Error "Build failed: dist/PortPilot.exe not found!"
    Get-ChildItem -Recurse dist
}

# Create installer using Inno Setup (if available AND config exists)
if ((Get-Command iscc -ErrorAction SilentlyContinue) -and (Test-Path "installer.iss")) {
    Write-Host "Creating installer with Inno Setup..." -ForegroundColor Cyan
    iscc installer.iss
} else {
    if (Get-Command iscc -ErrorAction SilentlyContinue) {
        Write-Host "Inno Setup found but 'installer.iss' missing. Skipping installer creation." -ForegroundColor Yellow
    } else {
        Write-Host "Inno Setup not found. Skipping installer creation." -ForegroundColor Yellow
    }
    
    # Rename executable for release
    if (Test-Path "dist/PortPilot.exe") {
        Copy-Item "dist/PortPilot.exe" "dist/PortPilot-Setup.exe" -Force
        Write-Host "Renamed PortPilot.exe to PortPilot-Setup.exe" -ForegroundColor Green
    }
}

# Verify final artifact
if (-not (Test-Path "dist/PortPilot-Setup.exe")) {
     Write-Error "Final artifact dist/PortPilot-Setup.exe not found!"
}

Write-Host "Build complete!" -ForegroundColor Green
Get-ChildItem dist
