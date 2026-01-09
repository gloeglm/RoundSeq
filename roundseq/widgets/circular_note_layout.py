"""Circular layout for note buttons."""

from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ListProperty,
)
from kivy.clock import Clock

from .pie_slice_button import PieSliceButton
from ..geometry import normalize_angle
from ..config import (
    NUM_NOTES,
    NOTE_NAMES,
    INNER_RADIUS,
    OUTER_RADIUS,
    CENTER_X,
    CENTER_Y,
    DEFAULT_OCTAVE,
)


class CircularNoteLayout(Widget):
    """Arranges 12 note buttons in a circular pattern."""

    inner_radius = NumericProperty(INNER_RADIUS)
    outer_radius = NumericProperty(OUTER_RADIUS)
    octave = NumericProperty(DEFAULT_OCTAVE)

    # Callback when a note is pressed/released
    on_note_on = ObjectProperty(None)
    on_note_off = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._note_buttons: list[PieSliceButton] = []
        # Track active button per touch (supports multitouch)
        self._active_buttons: dict = {}  # touch.uid -> button
        # Schedule creation after widget is ready
        Clock.schedule_once(self._create_note_buttons, 0)

    def _create_note_buttons(self, dt=None):
        """Create the 12 note buttons arranged in a circle."""
        self.clear_widgets()
        self._note_buttons = []

        # Each note gets 30 degrees (360 / 12)
        angle_per_note = 360 / NUM_NOTES

        for i in range(NUM_NOTES):
            note_name = NOTE_NAMES[i]
            is_sharp = "#" in note_name

            # Calculate center angle for this note
            # C is at top (90 degrees), going clockwise (decreasing angles)
            center_angle = 90 - (i * angle_per_note)

            # Slice spans half the angle on each side
            half_angle = angle_per_note / 2
            start_angle = center_angle - half_angle
            end_angle = center_angle + half_angle

            # Normalize to 0-360 range
            start_angle = normalize_angle(start_angle)
            end_angle = normalize_angle(end_angle)

            btn = PieSliceButton(
                inner_radius=self.inner_radius,
                outer_radius=self.outer_radius,
                start_angle=start_angle,
                end_angle=end_angle,
                label_text=note_name,
                is_sharp=is_sharp,
                size=self.size,
                pos=self.pos,
            )

            # Store note index for MIDI calculation
            btn.note_index = i

            # Don't use ButtonBehavior events - we handle touch ourselves
            # for proper slide-between-notes behavior

            self._note_buttons.append(btn)
            self.add_widget(btn)

        self._update_button_positions()

    def _update_button_positions(self, *args):
        """Update button center positions based on widget position."""
        if not hasattr(self, '_note_buttons'):
            return

        cx = self.center_x
        cy = self.center_y

        for btn in self._note_buttons:
            btn.center_x = cx
            btn.center_y = cy
            # Trigger redraw
            btn._update_graphics()

    def on_pos(self, *args):
        """Handle position changes."""
        self._update_button_positions()

    def on_size(self, *args):
        """Handle size changes."""
        self._update_button_positions()

    def _find_button_at(self, x, y):
        """Find which button contains the given point."""
        for btn in self._note_buttons:
            if btn.collide_point(x, y):
                return btn
        return None

    def _activate_button(self, button, touch_uid):
        """Activate a button (note on)."""
        button.is_pressed_state = True
        self._active_buttons[touch_uid] = button
        if self.on_note_on:
            midi_note = self._get_midi_note(button.note_index)
            self.on_note_on(midi_note, button.label_text)

    def _deactivate_button(self, button, touch_uid):
        """Deactivate a button (note off)."""
        button.is_pressed_state = False
        if touch_uid in self._active_buttons:
            del self._active_buttons[touch_uid]
        if self.on_note_off:
            midi_note = self._get_midi_note(button.note_index)
            self.on_note_off(midi_note, button.label_text)

    def on_touch_down(self, touch):
        """Handle touch/click down."""
        button = self._find_button_at(touch.x, touch.y)
        if button:
            touch.grab(self)
            self._activate_button(button, touch.uid)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Handle touch/drag movement - slide between notes."""
        if touch.grab_current is not self:
            return super().on_touch_move(touch)

        current_button = self._active_buttons.get(touch.uid)
        new_button = self._find_button_at(touch.x, touch.y)

        # If we've moved to a different button
        if new_button != current_button:
            # Deactivate old button
            if current_button:
                self._deactivate_button(current_button, touch.uid)
            # Activate new button
            if new_button:
                self._activate_button(new_button, touch.uid)

        return True

    def on_touch_up(self, touch):
        """Handle touch/click release."""
        if touch.grab_current is not self:
            return super().on_touch_up(touch)

        touch.ungrab(self)
        current_button = self._active_buttons.get(touch.uid)
        if current_button:
            self._deactivate_button(current_button, touch.uid)

        return True

    def _get_midi_note(self, note_index: int) -> int:
        """Convert note index and octave to MIDI note number.

        MIDI note 60 = C4 (middle C)
        """
        return (self.octave + 1) * 12 + note_index

    def set_octave(self, octave: int):
        """Set the current octave."""
        self.octave = max(0, min(8, octave))
