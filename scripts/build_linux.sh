#!/bin/bash
# Linux Build Script for PortPilot

echo "Building PortPilot for Linux..."

# Install PyInstaller if not present
pip install pyinstaller

# Build executable
pyinstaller \
    --name "PortPilot" \
    --onefile \
    --windowed \
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

# Create AppImage
if command -v appimagetool &> /dev/null; then
    echo "Creating AppImage..."
    
    # Create AppDir structure
    mkdir -p AppDir/usr/bin
    mkdir -p AppDir/usr/share/applications
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
    
    cp dist/PortPilot AppDir/usr/bin/
    
    # Create desktop file
    cat > AppDir/portpilot.desktop << EOF
[Desktop Entry]
Type=Application
Name=PortPilot
Exec=PortPilot
Icon=portpilot
Categories=Development;Utility;
EOF
    
    cp AppDir/portpilot.desktop AppDir/usr/share/applications/
    
    # Create AppRun
    cat > AppDir/AppRun << EOF
#!/bin/bash
exec \$APPDIR/usr/bin/PortPilot "\$@"
EOF
    chmod +x AppDir/AppRun
    
    # Build AppImage
    appimagetool AppDir dist/PortPilot.AppImage
else
    echo "appimagetool not found. Renaming executable..."
    cp dist/PortPilot dist/PortPilot.AppImage
fi

echo "Build complete!"
