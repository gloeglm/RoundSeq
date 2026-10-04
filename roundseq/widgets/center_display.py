"""Center display widget for octave control and status."""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock

from ..config import (
    CENTER_RADIUS,
    COLORS,
    DEFAULT_OCTAVE,
    MIN_OCTAVE,
    MAX_OCTAVE,
    SCALES,
    SCALE_ORDER,
    DEFAULT_SCALE,
    DEFAULT_ROOT,
    NOTE_NAMES,
)


class CenterDisplay(Widget):
    """Central display showing octave, scale selection, and controls."""

    radius = NumericProperty(CENTER_RADIUS)
    octave = NumericProperty(DEFAULT_OCTAVE)
    last_note = StringProperty("")
    scale_key = StringProperty(DEFAULT_SCALE)
    root_note = NumericProperty(DEFAULT_ROOT)

    # Callbacks
    on_octave_change = ObjectProperty(None)
    on_scale_change = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bg_ellipse = None
        self._layout = None
        self._root_label = None
        self._scale_label = None
        self._octave_label = None
        self._note_label = None
        self._setup_done = False

        Clock.schedule_once(self._setup, 0)
        self.bind(pos=self._update_layout, size=self._update_layout)

    def _setup(self, dt):
        """Set up child widgets."""
        self._draw_background()
        self._create_layout()
        self._setup_done = True
        self._update_layout()

    def _draw_background(self):
        """Draw the circular background."""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS["background"])
            self._bg_ellipse = Ellipse(
                pos=(self.center_x - self.radius, self.center_y - self.radius),
                size=(self.radius * 2, self.radius * 2),
            )

    def _make_btn(self, text, callback, width=50):
        """Create a styled button."""
        btn = Button(
            text=text,
            size_hint=(None, 1),
            width=width,
            background_color=COLORS["button_normal"],
            color=COLORS["text"],
            font_size="18sp",
            bold=True,
        )
        btn.bind(on_release=callback)
        return btn

    def _make_label(self, text, color=None, font_size="20sp"):
        """Create a styled label."""
        return Label(
            text=text,
            color=color or COLORS["text"],
            font_size=font_size,
            bold=True,
            size_hint=(1, 1),
            halign="center",
            valign="middle",
        )

    def _create_layout(self):
        """Create the main layout with all controls."""
        # Main vertical layout
        self._layout = BoxLayout(
            orientation='vertical',
            spacing=5,
            padding=[10, 15, 10, 15],
        )

        # Row 1: Root note < C >
        row1 = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=5)
        row1.add_widget(self._make_btn("<", self._on_root_prev))
        self._root_label = self._make_label(NOTE_NAMES[self.root_note], COLORS["accent"])
        row1.add_widget(self._root_label)
        row1.add_widget(self._make_btn(">", self._on_root_next))
        self._layout.add_widget(row1)

        # Row 2: Scale < Chromatic >
        row2 = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=5)
        row2.add_widget(self._make_btn("<", self._on_scale_prev))
        self._scale_label = self._make_label(SCALES[self.scale_key][0], COLORS["accent"])
        row2.add_widget(self._scale_label)
        row2.add_widget(self._make_btn(">", self._on_scale_next))
        self._layout.add_widget(row2)

        # Row 3: Octave - OCT 4 +
        row3 = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=5)
        row3.add_widget(self._make_btn("-", self._on_octave_down))
        self._octave_label = self._make_label(f"OCT {self.octave}", COLORS["text"])
        row3.add_widget(self._octave_label)
        row3.add_widget(self._make_btn("+", self._on_octave_up))
        self._layout.add_widget(row3)

        # Row 4: Note display
        self._note_label = self._make_label("", COLORS["text_dim"], "18sp")
        self._layout.add_widget(self._note_label)

        self.add_widget(self._layout)

    def _update_layout(self, *args):
        """Update layout position and size."""
        if not self._setup_done or not self._layout:
            return

        cx, cy = self.center_x, self.center_y

        # Update background
        if self._bg_ellipse:
            self._bg_ellipse.pos = (cx - self.radius, cy - self.radius)
            self._bg_ellipse.size = (self.radius * 2, self.radius * 2)

        # Position layout in center, sized to fit within circle
        layout_size = self.radius * 1.4  # Use ~70% of diameter
        self._layout.size = (layout_size, layout_size)
        self._layout.center = (cx, cy)

    # Root note controls
    def _on_root_prev(self, *args):
        self.root_note = (self.root_note - 1) % 12
        self._root_label.text = NOTE_NAMES[self.root_note]
        if self.on_scale_change:
            self.on_scale_change(self.scale_key, self.root_note)

    def _on_root_next(self, *args):
        self.root_note = (self.root_note + 1) % 12
        self._root_label.text = NOTE_NAMES[self.root_note]
        if self.on_scale_change:
            self.on_scale_change(self.scale_key, self.root_note)

    # Scale type controls
    def _on_scale_prev(self, *args):
        current_index = SCALE_ORDER.index(self.scale_key)
        prev_index = (current_index - 1) % len(SCALE_ORDER)
        self.scale_key = SCALE_ORDER[prev_index]
        self._scale_label.text = SCALES[self.scale_key][0]
        if self.on_scale_change:
            self.on_scale_change(self.scale_key, self.root_note)

    def _on_scale_next(self, *args):
        current_index = SCALE_ORDER.index(self.scale_key)
        next_index = (current_index + 1) % len(SCALE_ORDER)
        self.scale_key = SCALE_ORDER[next_index]
        self._scale_label.text = SCALES[self.scale_key][0]
        if self.on_scale_change:
            self.on_scale_change(self.scale_key, self.root_note)

    # Octave controls
    def _on_octave_up(self, *args):
        if self.octave < MAX_OCTAVE:
            self.octave += 1
            self._octave_label.text = f"OCT {self.octave}"
            if self.on_octave_change:
                self.on_octave_change(self.octave)

    def _on_octave_down(self, *args):
        if self.octave > MIN_OCTAVE:
            self.octave -= 1
            self._octave_label.text = f"OCT {self.octave}"
            if self.on_octave_change:
                self.on_octave_change(self.octave)

    # Note display
    def show_note(self, note_name: str):
        """Display the last played note."""
        self.last_note = note_name
        if self._note_label:
            self._note_label.text = note_name

    def clear_note(self):
        """Clear the note display."""
        self.last_note = ""
        if self._note_label:
            self._note_label.text = ""

    def set_scale(self, scale_key: str, root_note: int):
        """Set the scale and root note externally."""
        self.scale_key = scale_key
        self.root_note = root_note
        if self._root_label:
            self._root_label.text = NOTE_NAMES[self.root_note]
        if self._scale_label:
            self._scale_label.text = SCALES[self.scale_key][0]
