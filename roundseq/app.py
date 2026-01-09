"""Main Kivy application for RoundSeq."""

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config

from .screens.note_play_screen import NotePlayScreen
from .services import get_midi_service
from .platform import get_platform_name, is_raspberry_pi
from .config import DISPLAY_WIDTH, DISPLAY_HEIGHT, COLORS


class RoundSeqApp(App):
    """Main application class for RoundSeq."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._midi_service = None
        self._note_screen = None

    def build(self):
        """Build the application UI."""
        # Configure window
        self._configure_window()

        # Initialize MIDI service
        self._midi_service = get_midi_service()
        self._midi_service.connect()

        print(f"[RoundSeq] Running on {get_platform_name()}")
        print(f"[RoundSeq] MIDI ports: {self._midi_service.list_ports()}")

        # Create main screen
        self._note_screen = NotePlayScreen(midi_service=self._midi_service)

        return self._note_screen

    def _configure_window(self):
        """Configure the window based on platform."""
        # Set background color
        Window.clearcolor = COLORS["background"]

        if is_raspberry_pi():
            # Fullscreen on Pi
            Window.fullscreen = "auto"
        else:
            # Windowed on desktop
            Window.fullscreen = False
            Window.size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
            # Center the window
            Window.left = 100
            Window.top = 100

    def on_stop(self):
        """Clean up when app closes."""
        if self._midi_service:
            self._midi_service.disconnect()
        print("[RoundSeq] Goodbye!")


def run():
    """Run the application."""
    # Pre-configure Kivy before importing other modules
    Config.set("graphics", "width", str(DISPLAY_WIDTH))
    Config.set("graphics", "height", str(DISPLAY_HEIGHT))
    Config.set("graphics", "resizable", "0")

    # Disable multitouch emulation (red dots on right-click)
    Config.set("input", "mouse", "mouse,multitouch_on_demand")

    app = RoundSeqApp()
    app.run()
