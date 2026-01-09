"""Center display widget for octave control and status."""

import math

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock

from ..config import (
    CENTER_RADIUS,
    COLORS,
    DEFAULT_OCTAVE,
    MIN_OCTAVE,
    MAX_OCTAVE,
)


class CircleButton(ButtonBehavior, Widget):
    """A simple circular button."""

    radius = NumericProperty(30)
    text = StringProperty("")
    is_pressed_state = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._label = None
        self.bind(pos=self._update, size=self._update, is_pressed_state=self._update)
        Clock.schedule_once(self._setup, 0)

    def _setup(self, dt):
        self._update()

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_pressed_state:
                Color(*COLORS["button_pressed"])
            else:
                Color(*COLORS["button_normal"])
            Ellipse(
                pos=(self.center_x - self.radius, self.center_y - self.radius),
                size=(self.radius * 2, self.radius * 2),
            )
            Color(0.4, 0.4, 0.45, 1)
            Line(
                ellipse=(
                    self.center_x - self.radius,
                    self.center_y - self.radius,
                    self.radius * 2,
                    self.radius * 2,
                ),
                width=1.2,
            )

    def collide_point(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)

    def on_press(self):
        self.is_pressed_state = True

    def on_release(self):
        self.is_pressed_state = False


class CenterDisplay(Widget):
    """Central display showing octave and providing +/- controls."""

    radius = NumericProperty(CENTER_RADIUS)
    octave = NumericProperty(DEFAULT_OCTAVE)
    last_note = StringProperty("")

    # Callbacks
    on_octave_change = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._octave_label = None
        self._note_label = None
        self._btn_up = None
        self._btn_down = None
        self._btn_up_label = None
        self._btn_down_label = None
        self._bg_ellipse = None
        self._setup_done = False

        Clock.schedule_once(self._setup, 0)
        self.bind(pos=self._update_positions, size=self._update_positions)

    def _setup(self, dt):
        """Set up child widgets."""
        self._draw_background()
        self._create_labels()
        self._create_buttons()
        self._setup_done = True
        self._update_positions()

    def _draw_background(self):
        """Draw the circular background."""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS["background"])
            self._bg_ellipse = Ellipse(
                pos=(self.center_x - self.radius, self.center_y - self.radius),
                size=(self.radius * 2, self.radius * 2),
            )

    def _create_labels(self):
        """Create the octave and note labels."""
        self._octave_label = Label(
            text=f"OCT {self.octave}",
            font_size="32sp",
            color=COLORS["text"],
            bold=True,
        )
        self.add_widget(self._octave_label)

        self._note_label = Label(
            text="",
            font_size="24sp",
            color=COLORS["text_dim"],
        )
        self.add_widget(self._note_label)

    def _create_buttons(self):
        """Create octave up/down buttons."""
        btn_radius = 35

        self._btn_up = CircleButton(radius=btn_radius, text="+")
        self._btn_up.bind(on_release=self._on_octave_up)
        self.add_widget(self._btn_up)

        # Add label for up button
        self._btn_up_label = Label(
            text="+",
            font_size="28sp",
            color=COLORS["text"],
            bold=True,
        )
        self.add_widget(self._btn_up_label)

        self._btn_down = CircleButton(radius=btn_radius, text="-")
        self._btn_down.bind(on_release=self._on_octave_down)
        self.add_widget(self._btn_down)

        # Add label for down button
        self._btn_down_label = Label(
            text="-",
            font_size="32sp",
            color=COLORS["text"],
            bold=True,
        )
        self.add_widget(self._btn_down_label)

    def _update_positions(self, *args):
        """Update positions of all elements."""
        if not self._setup_done:
            return

        cx, cy = self.center_x, self.center_y

        # Update background
        if self._bg_ellipse:
            self._bg_ellipse.pos = (cx - self.radius, cy - self.radius)
            self._bg_ellipse.size = (self.radius * 2, self.radius * 2)

        # Position labels
        if self._octave_label:
            self._octave_label.center_x = cx
            self._octave_label.center_y = cy + 20

        if self._note_label:
            self._note_label.center_x = cx
            self._note_label.center_y = cy - 20

        # Position buttons (left and right of center)
        btn_offset = self.radius * 0.55
        if self._btn_up:
            self._btn_up.center_x = cx + btn_offset
            self._btn_up.center_y = cy
            self._btn_up._update()

        if self._btn_up_label:
            self._btn_up_label.center_x = cx + btn_offset
            self._btn_up_label.center_y = cy

        if self._btn_down:
            self._btn_down.center_x = cx - btn_offset
            self._btn_down.center_y = cy
            self._btn_down._update()

        if self._btn_down_label:
            self._btn_down_label.center_x = cx - btn_offset
            self._btn_down_label.center_y = cy

    def _on_octave_up(self, *args):
        """Increase octave."""
        if self.octave < MAX_OCTAVE:
            self.octave += 1
            self._update_octave_display()
            if self.on_octave_change:
                self.on_octave_change(self.octave)

    def _on_octave_down(self, *args):
        """Decrease octave."""
        if self.octave > MIN_OCTAVE:
            self.octave -= 1
            self._update_octave_display()
            if self.on_octave_change:
                self.on_octave_change(self.octave)

    def _update_octave_display(self):
        """Update the octave label."""
        if self._octave_label:
            self._octave_label.text = f"OCT {self.octave}"

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
