"""
Auto-update functionality for PortPilot.
"""

import json
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError

from src.core.version import VERSION


GITHUB_API = "https://api.github.com/repos/logando-al/port_pilot/releases/latest"
GITHUB_RELEASES = "https://github.com/logando-al/port_pilot/releases"


class Updater:
    """
    Handles checking for and applying updates from GitHub releases.
    """
    
    def __init__(self):
        self.current_version = VERSION
        self.latest_version: Optional[str] = None
        self.download_url: Optional[str] = None
    
    def check_for_updates(self) -> Tuple[bool, str]:
        """
        Check GitHub for a newer version.
        
        Returns:
            Tuple of (update_available, message).
        """
        try:
            request = Request(
                GITHUB_API,
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            self.latest_version = data.get("tag_name", "").lstrip("v")
            
            if self._compare_versions(self.latest_version, self.current_version) > 0:
                # Find appropriate download URL for current platform
                self.download_url = self._find_download_url(data.get("assets", []))
                return (True, f"New version {self.latest_version} available!")
            
            return (False, "You're running the latest version.")
            
        except URLError as e:
            return (False, f"Could not check for updates: {e}")
        except Exception as e:
            return (False, f"Error checking for updates: {e}")
    
    def download_and_install(self) -> Tuple[bool, str]:
        """
        Download and install the latest update.
        
        Returns:
            Tuple of (success, message).
        """
        if not self.download_url:
            return (False, "No download URL available. Please update manually.")
        
        try:
            # Download to temp directory
            temp_dir = Path(tempfile.gettempdir()) / "portpilot_update"
            temp_dir.mkdir(exist_ok=True)
            
            filename = self.download_url.split("/")[-1]
            download_path = temp_dir / filename
            
            with urlopen(self.download_url, timeout=60) as response:
                with open(download_path, 'wb') as f:
                    f.write(response.read())
            
            # Platform-specific installation
            if sys.platform == 'win32':
                # Run installer
                subprocess.Popen([str(download_path)], shell=True)
            elif sys.platform == 'darwin':
                # Open DMG
                subprocess.Popen(['open', str(download_path)])
            else:
                # Linux AppImage - make executable and run
                download_path.chmod(0o755)
                subprocess.Popen([str(download_path)])
            
            return (True, "Update downloaded. Please restart the application.")
            
        except Exception as e:
            return (False, f"Failed to download update: {e}")
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.
        
        Returns:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2.
        """
        try:
            p1 = [int(x) for x in v1.split('.')]
            p2 = [int(x) for x in v2.split('.')]
            
            for i in range(max(len(p1), len(p2))):
                a = p1[i] if i < len(p1) else 0
                b = p2[i] if i < len(p2) else 0
                if a > b:
                    return 1
                elif a < b:
                    return -1
            return 0
        except ValueError:
            return 0
    
    def _find_download_url(self, assets: list) -> Optional[str]:
        """Find the appropriate download URL for the current platform."""
        platform_patterns = {
            'win32': ['.exe', 'windows', 'win64', 'win32'],
            'darwin': ['.dmg', 'macos', 'darwin', 'osx'],
            'linux': ['.AppImage', 'linux', 'ubuntu']
        }
        
        patterns = platform_patterns.get(sys.platform, [])
        
        for asset in assets:
            name = asset.get("name", "").lower()
            for pattern in patterns:
                if pattern.lower() in name:
                    return asset.get("browser_download_url")
        
        return None
