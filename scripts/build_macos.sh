#!/bin/bash
# macOS Build Script for PortPilot

echo "Building PortPilot for macOS..."

# Install PyInstaller if not present
pip install pyinstaller

# Build executable
pyinstaller \
    --name "PortPilot" \
    --onefile \
    --windowed \
    --icon "resources/icons/tray_icon.icns" \
    --add-data "src/ui/styles:src/ui/styles" \
    --add-data "resources:resources" \
    src/main.py

# Create DMG
if command -v create-dmg &> /dev/null; then
    echo "Creating DMG..."
    create-dmg \
        --volname "PortPilot" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --app-drop-link 450 185 \
        "dist/PortPilot.dmg" \
        "dist/PortPilot.app"
else
    echo "create-dmg not found. Creating simple DMG..."
    hdiutil create -volname "PortPilot" -srcfolder "dist/PortPilot.app" -ov -format UDZO "dist/PortPilot.dmg"
fi

echo "Build complete!"
