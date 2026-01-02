# Windows Build Script for PortPilot

Write-Host "Building PortPilot for Windows..." -ForegroundColor Cyan

# Install PyInstaller if not present
pip install pyinstaller

# Build executable
pyinstaller `
    --name "PortPilot" `
    --onefile `
    --windowed `
    --icon "resources/icons/tray_icon.ico" `
    --add-data "src/ui/styles;src/ui/styles" `
    --add-data "resources;resources" `
    src/main.py

# Create installer using Inno Setup (if available)
if (Get-Command iscc -ErrorAction SilentlyContinue) {
    Write-Host "Creating installer with Inno Setup..." -ForegroundColor Cyan
    # iscc installer.iss
} else {
    Write-Host "Inno Setup not found. Skipping installer creation." -ForegroundColor Yellow
    # Rename executable for release
    if (Test-Path "dist/PortPilot.exe") {
        Copy-Item "dist/PortPilot.exe" "dist/PortPilot-Setup.exe"
    }
}

Write-Host "Build complete!" -ForegroundColor Green
