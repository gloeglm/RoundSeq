"""Note play screen - main interface for playing notes."""

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Ellipse

from ..widgets.circular_note_layout import CircularNoteLayout
from ..widgets.center_display import CenterDisplay
from ..services import MidiService
from ..config import (
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    INNER_RADIUS,
    OUTER_RADIUS,
    CENTER_RADIUS,
    COLORS,
    DEFAULT_OCTAVE,
)


class NotePlayScreen(FloatLayout):
    """Main screen for playing notes via the circular interface."""

    midi_service = ObjectProperty(None, allownone=True)

    def __init__(self, midi_service: MidiService = None, **kwargs):
        super().__init__(**kwargs)
        self.midi_service = midi_service

        # Draw background
        with self.canvas.before:
            Color(*COLORS["background"])
            self._bg = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

        # Create the circular note layout
        self._note_layout = CircularNoteLayout(
            inner_radius=INNER_RADIUS,
            outer_radius=OUTER_RADIUS,
            octave=DEFAULT_OCTAVE,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self._note_layout.on_note_on = self._on_note_on
        self._note_layout.on_note_off = self._on_note_off
        self.add_widget(self._note_layout)

        # Create the center display
        self._center_display = CenterDisplay(
            radius=CENTER_RADIUS,
            octave=DEFAULT_OCTAVE,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self._center_display.on_octave_change = self._on_octave_change
        self.add_widget(self._center_display)

    def _update_bg(self, *args):
        """Update background size/position."""
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _on_note_on(self, midi_note: int, note_name: str):
        """Handle note on event."""
        # Update center display
        full_name = f"{note_name}{self._note_layout.octave}"
        self._center_display.show_note(full_name)

        # Send MIDI
        if self.midi_service:
            self.midi_service.note_on(midi_note)

    def _on_note_off(self, midi_note: int, note_name: str):
        """Handle note off event."""
        # Clear center display
        self._center_display.clear_note()

        # Send MIDI
        if self.midi_service:
            self.midi_service.note_off(midi_note)

    def _on_octave_change(self, octave: int):
        """Handle octave change from center display."""
        self._note_layout.set_octave(octave)

    def set_midi_service(self, midi_service: MidiService):
        """Set the MIDI service."""
        self.midi_service = midi_service
