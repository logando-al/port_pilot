"""
Centralized version management for PortPilot.
"""

VERSION = "0.1.0"
VERSION_TUPLE = (0, 1, 0)

def get_version() -> str:
    """Return the current version string."""
    return VERSION

def get_version_info() -> dict:
    """Return detailed version information."""
    return {
        "version": VERSION,
        "major": VERSION_TUPLE[0],
        "minor": VERSION_TUPLE[1],
        "patch": VERSION_TUPLE[2],
    }
