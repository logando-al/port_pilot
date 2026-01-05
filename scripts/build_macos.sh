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
    --paths "." \
    --hidden-import "src.core" \
    --hidden-import "src.core.port_scanner" \
    --hidden-import "src.core.process_killer" \
    --hidden-import "src.core.tunnel_manager" \
    --hidden-import "src.core.version" \
    --hidden-import "src.ui" \
    --hidden-import "src.ui.tray_icon" \
    --hidden-import "src.ui.dashboard" \
    --hidden-import "src.ui.widgets" \
    --hidden-import "src.ui.widgets.port_table" \
    --hidden-import "src.ui.widgets.tunnel_list" \
    --hidden-import "src.utils" \
    --hidden-import "src.utils.config" \
    --hidden-import "src.utils.platform_utils" \
    --hidden-import "src.utils.updater" \
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
