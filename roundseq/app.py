"""Main Kivy application for RoundSeq."""

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config

from .screens.note_play_screen import NotePlayScreen
from .screens.clock_viz_screen import ClockVizScreen
from .services import get_midi_service, get_midi_input_service
from .platform import get_platform_name, is_raspberry_pi
from .config import DISPLAY_WIDTH, DISPLAY_HEIGHT, COLORS


class RoundSeqApp(App):
    """Main application class for RoundSeq."""

    def __init__(self, mode: str = "play", **kwargs):
        super().__init__(**kwargs)
        self._mode = mode
        self._midi_service = None
        self._midi_input_service = None
        self._screen = None

    def build(self):
        """Build the application UI."""
        self._configure_window()
        print(f"[RoundSeq] Running on {get_platform_name()} (mode={self._mode})")

        if self._mode == "clock":
            self._midi_input_service = get_midi_input_service()
            self._midi_input_service.connect()
            print(f"[RoundSeq] MIDI input ports: {self._midi_input_service.list_ports()}")
            self._screen = ClockVizScreen(midi_input_service=self._midi_input_service)
        else:
            self._midi_service = get_midi_service()
            self._midi_service.connect()
            print(f"[RoundSeq] MIDI ports: {self._midi_service.list_ports()}")
            self._screen = NotePlayScreen(midi_service=self._midi_service)

        return self._screen

    def _configure_window(self):
        """Configure the window based on platform."""
        Window.clearcolor = COLORS["background"]

        if not is_raspberry_pi():
            Window.fullscreen = False
            Window.size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
            Window.left = 100
            Window.top = 100

    def on_stop(self):
        """Clean up when app closes."""
        if self._screen is not None and hasattr(self._screen, "stop"):
            self._screen.stop()
        if self._midi_service:
            self._midi_service.disconnect()
        if self._midi_input_service:
            self._midi_input_service.disconnect()
        print("[RoundSeq] Goodbye!")


def run(mode: str = "play"):
    """Run the application."""
    Config.set("graphics", "width", str(DISPLAY_WIDTH))
    Config.set("graphics", "height", str(DISPLAY_HEIGHT))
    Config.set("graphics", "resizable", "0")

    Config.set("input", "mouse", "mouse,multitouch_on_demand")

    if is_raspberry_pi():
        Config.set("graphics", "fullscreen", "0")
        Config.set("graphics", "borderless", "1")

    app = RoundSeqApp(mode=mode)
    app.run()
