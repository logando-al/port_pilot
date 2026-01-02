"""
Platform-specific utilities for PortPilot.
"""

import os
import subprocess
import sys


def get_platform() -> str:
    """Get normalized platform name."""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'


def is_admin() -> bool:
    """Check if running with admin/root privileges."""
    if sys.platform == 'win32':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return os.geteuid() == 0


def request_admin_privileges(script_path: str | None = None) -> tuple[bool, str]:
    """
    Request elevated privileges.

    Args:
        script_path: Path to script to run with elevated privileges.

    Returns:
        Tuple of (success, message).
    """
    if is_admin():
        return (True, "Already running with admin privileges.")

    if sys.platform == 'win32':
        try:
            import ctypes
            # Build the full command with python and script
            python_exe = sys.executable
            # Get the script being run (sys.argv[0] is the script path)
            script_args = " ".join(f'"{arg}"' for arg in sys.argv)

            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", python_exe, script_args, None, 1
            )
            if result > 32:
                # Exit current (non-admin) instance
                sys.exit(0)
            else:
                return (False, "User denied admin privileges.")
        except Exception as e:
            return (False, f"Failed to request admin privileges: {e}")

    elif sys.platform == 'darwin':
        try:
            python_exe = sys.executable
            script_args = " ".join(f'"{arg}"' for arg in sys.argv)
            subprocess.run([
                'osascript', '-e',
                f'do shell script "{python_exe} {script_args}" with administrator privileges'
            ])
            sys.exit(0)
        except Exception as e:
            return (False, f"Failed to request admin privileges: {e}")

    else:  # Linux
        try:
            python_exe = sys.executable
            if os.environ.get('DISPLAY'):
                # Try graphical sudo
                subprocess.Popen(['pkexec', python_exe] + sys.argv)
            else:
                # Terminal sudo
                subprocess.Popen(['sudo', python_exe] + sys.argv)
            sys.exit(0)
        except Exception as e:
            return (False, f"Failed to request admin privileges: {e}")


def get_autostart_path() -> str:
    """Get the path for autostart entry."""
    if sys.platform == 'win32':
        return os.path.join(
            os.environ.get('APPDATA', ''),
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/LaunchAgents')
    else:
        return os.path.expanduser('~/.config/autostart')


def set_autostart(enabled: bool) -> tuple[bool, str]:
    """Enable or disable autostart."""
    try:
        if sys.platform == 'win32':
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            if enabled:
                winreg.SetValueEx(key, "PortPilot", 0, winreg.REG_SZ, sys.executable)
            else:
                try:
                    winreg.DeleteValue(key, "PortPilot")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)

        elif sys.platform == 'darwin':
            plist_path = os.path.expanduser('~/Library/LaunchAgents/com.portpilot.app.plist')
            if enabled:
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.portpilot.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
            else:
                if os.path.exists(plist_path):
                    os.remove(plist_path)

        else:  # Linux
            desktop_path = os.path.expanduser('~/.config/autostart/portpilot.desktop')
            os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
            if enabled:
                desktop_content = f'''[Desktop Entry]
Type=Application
Name=PortPilot
Exec={sys.executable}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
                with open(desktop_path, 'w') as f:
                    f.write(desktop_content)
            else:
                if os.path.exists(desktop_path):
                    os.remove(desktop_path)

        return (True, f"Autostart {'enabled' if enabled else 'disabled'}.")
    except Exception as e:
        return (False, f"Failed to set autostart: {e}")
