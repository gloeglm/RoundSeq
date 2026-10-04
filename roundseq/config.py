"""Configuration for RoundSeq."""
from __future__ import annotations

from .platform import is_raspberry_pi

# Display configuration
DISPLAY_WIDTH = 1080
DISPLAY_HEIGHT = 1080
DISPLAY_RADIUS = DISPLAY_WIDTH // 2  # 540
SAFE_RADIUS = int(DISPLAY_RADIUS * 0.9)  # ~486, margin from edge

# Circular layout
CENTER_X = DISPLAY_WIDTH // 2
CENTER_Y = DISPLAY_HEIGHT // 2

# Note layout
NUM_NOTES = 12
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
DEFAULT_OCTAVE = 4
MIN_OCTAVE = 0
MAX_OCTAVE = 8

# Scale definitions: key -> (display_name, intervals_tuple)
SCALES = {
    "chromatic": ("Chromatic", (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)),
    "major": ("Major", (0, 2, 4, 5, 7, 9, 11)),
    "minor": ("Minor", (0, 2, 3, 5, 7, 8, 10)),
    "pentatonic_major": ("Pent Maj", (0, 2, 4, 7, 9)),
    "pentatonic_minor": ("Pent Min", (0, 3, 5, 7, 10)),
    "blues": ("Blues", (0, 3, 5, 6, 7, 10)),
}
SCALE_ORDER = ["chromatic", "major", "minor", "pentatonic_major", "pentatonic_minor", "blues"]
DEFAULT_SCALE = "chromatic"
DEFAULT_ROOT = 0  # C

# MIDI configuration
DEFAULT_VELOCITY = 100
DEFAULT_CHANNEL = 0  # MIDI channels are 0-15

# Visual configuration
OUTER_RADIUS = int(DISPLAY_RADIUS * 0.95)  # Note buttons outer edge
INNER_RADIUS = int(DISPLAY_RADIUS * 0.55)  # Note buttons inner edge
CENTER_RADIUS = int(DISPLAY_RADIUS * 0.45)  # Center display area

# Colors (RGBA, 0-1 range for Kivy)
COLORS = {
    "background": (0.1, 0.1, 0.12, 1),
    "button_normal": (0.2, 0.25, 0.3, 1),
    "button_pressed": (0.4, 0.6, 0.8, 1),
    "button_sharp": (0.15, 0.18, 0.22, 1),  # Darker for sharps/flats
    "text": (0.9, 0.9, 0.9, 1),
    "text_dim": (0.5, 0.5, 0.5, 1),
    "accent": (0.3, 0.7, 0.9, 1),
}

# Platform-specific settings
def get_fullscreen() -> bool:
    """Return True if app should run fullscreen."""
    return is_raspberry_pi()


def get_window_size() -> tuple[int, int]:
    """Return window size for windowed mode."""
    return (DISPLAY_WIDTH, DISPLAY_HEIGHT)
