"""Platform detection for RoundSeq."""

import sys
import os


def is_raspberry_pi() -> bool:
    """Detect if running on a Raspberry Pi."""
    if sys.platform != "linux":
        return False

    try:
        with open("/proc/device-tree/model", "r") as f:
            model = f.read().lower()
            return "raspberry pi" in model
    except FileNotFoundError:
        return False


def is_macos() -> bool:
    """Detect if running on macOS."""
    return sys.platform == "darwin"


def get_platform_name() -> str:
    """Get human-readable platform name."""
    if is_raspberry_pi():
        return "Raspberry Pi"
    elif is_macos():
        return "macOS"
    elif sys.platform == "linux":
        return "Linux"
    elif sys.platform == "win32":
        return "Windows"
    return "Unknown"
