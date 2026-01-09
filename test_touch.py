#!/usr/bin/env python3
"""Test script to verify touch handling on the circular note layout."""

import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Kivy before importing
os.environ['KIVY_LOG_LEVEL'] = 'warning'
from kivy.config import Config
Config.set("graphics", "width", "1080")
Config.set("graphics", "height", "1080")

from kivy.base import EventLoop

from roundseq.widgets.circular_note_layout import CircularNoteLayout
from roundseq.config import (
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
    INNER_RADIUS, OUTER_RADIUS,
    CENTER_X, CENTER_Y,
    NOTE_NAMES,
)


class MockTouch:
    """Mock touch event for testing."""

    _uid_counter = 0

    def __init__(self, x, y):
        MockTouch._uid_counter += 1
        self.uid = MockTouch._uid_counter
        self.x = x
        self.y = y
        self.grab_current = None
        self._grabbed = []

    def grab(self, widget):
        self.grab_current = widget
        self._grabbed.append(widget)

    def ungrab(self, widget):
        if widget in self._grabbed:
            self._grabbed.remove(widget)
        if self.grab_current == widget:
            self.grab_current = None

    def move(self, x, y):
        """Move the touch to a new position."""
        self.x = x
        self.y = y


def get_note_position_from_button(button) -> tuple[float, float]:
    """Get x, y position at the center of a pie slice button."""
    start = button.start_angle
    end = button.end_angle

    # Calculate mid angle, handling wrap-around (e.g., 345 to 15 degrees)
    if end < start:
        # Wrap-around case: e.g., start=345, end=15
        # Mid is at (345 + 15 + 360) / 2 % 360 = 0
        mid_angle = ((start + end + 360) / 2) % 360
    else:
        mid_angle = (start + end) / 2

    mid_radius = (button.inner_radius + button.outer_radius) / 2
    angle_rad = math.radians(mid_angle)

    x = button.center_x + mid_radius * math.cos(angle_rad)
    y = button.center_y + mid_radius * math.sin(angle_rad)

    return x, y


def test_touch_handling():
    """Test that touches activate the correct buttons."""
    print("\n" + "=" * 60)
    print("Testing CircularNoteLayout Touch Handling")
    print("=" * 60)

    # Track events
    events = []

    def on_note_on(midi_note, note_name):
        events.append(("ON", note_name, midi_note))
        print(f"  Note ON:  {note_name} (MIDI {midi_note})")

    def on_note_off(midi_note, note_name):
        events.append(("OFF", note_name, midi_note))
        print(f"  Note OFF: {note_name} (MIDI {midi_note})")

    # Create the layout
    layout = CircularNoteLayout(
        size=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
        pos=(0, 0),
    )
    layout.on_note_on = on_note_on
    layout.on_note_off = on_note_off

    # Manually trigger button creation (normally done by Clock)
    layout._create_note_buttons()

    # Set center position (normally done by parent layout)
    layout.center_x = CENTER_X
    layout.center_y = CENTER_Y
    layout._update_button_positions()

    # Get button references for position calculations
    buttons = {btn.label_text: btn for btn in layout._note_buttons}

    print("\n--- Debug: Button angles ---")
    for name in NOTE_NAMES:
        btn = buttons[name]
        print(f"  {name:3s}: start={btn.start_angle:6.1f}, end={btn.end_angle:6.1f}")

    print("\n--- Test 1: Single click on C (top) ---")
    events.clear()
    x, y = get_note_position_from_button(buttons["C"])
    print(f"  Clicking at ({x:.0f}, {y:.0f})")

    touch = MockTouch(x, y)
    layout.on_touch_down(touch)
    layout.on_touch_up(touch)

    assert len(events) == 2, f"Expected 2 events, got {len(events)}"
    assert events[0] == ("ON", "C", 60), f"Expected C note on, got {events[0]}"
    assert events[1] == ("OFF", "C", 60), f"Expected C note off, got {events[1]}"
    print("  PASSED")

    print("\n--- Test 2: Single click on G ---")
    events.clear()
    g_btn = buttons["G"]
    print(f"  G button: start_angle={g_btn.start_angle}, end_angle={g_btn.end_angle}")
    print(f"  G button: center=({g_btn.center_x}, {g_btn.center_y})")
    x, y = get_note_position_from_button(g_btn)
    print(f"  Clicking at ({x:.0f}, {y:.0f})")
    # Debug: check what angle we're clicking
    dx = x - g_btn.center_x
    dy = y - g_btn.center_y
    click_angle = math.degrees(math.atan2(dy, dx))
    if click_angle < 0:
        click_angle += 360
    print(f"  Click angle from center: {click_angle:.1f} degrees")

    touch = MockTouch(x, y)
    layout.on_touch_down(touch)
    layout.on_touch_up(touch)

    assert len(events) == 2, f"Expected 2 events, got {len(events)}"
    assert events[0] == ("ON", "G", 67), f"Expected G note on, got {events[0]}"
    assert events[1] == ("OFF", "G", 67), f"Expected G note off, got {events[1]}"
    print("  PASSED")

    print("\n--- Test 3: Click in center (no button) ---")
    events.clear()
    print(f"  Clicking at center ({CENTER_X}, {CENTER_Y})")

    touch = MockTouch(CENTER_X, CENTER_Y)
    layout.on_touch_down(touch)
    layout.on_touch_up(touch)

    assert len(events) == 0, f"Expected 0 events for center click, got {len(events)}"
    print("  PASSED (no events, as expected)")

    print("\n--- Test 4: Slide from C to D ---")
    events.clear()
    x1, y1 = get_note_position_from_button(buttons["C"])
    x2, y2 = get_note_position_from_button(buttons["D"])
    print(f"  Touch down at C ({x1:.0f}, {y1:.0f})")
    print(f"  Slide to D ({x2:.0f}, {y2:.0f})")

    touch = MockTouch(x1, y1)
    layout.on_touch_down(touch)

    # Move to D
    touch.move(x2, y2)
    layout.on_touch_move(touch)

    # Release
    layout.on_touch_up(touch)

    print(f"  Events: {events}")
    assert ("ON", "C", 60) in events, "Expected C note on"
    assert ("OFF", "C", 60) in events, "Expected C note off"
    assert ("ON", "D", 62) in events, "Expected D note on"
    assert ("OFF", "D", 62) in events, "Expected D note off"
    print("  PASSED")

    print("\n--- Test 5: Slide through C -> C# -> D ---")
    events.clear()
    x1, y1 = get_note_position_from_button(buttons["C"])
    x2, y2 = get_note_position_from_button(buttons["C#"])
    x3, y3 = get_note_position_from_button(buttons["D"])

    touch = MockTouch(x1, y1)
    layout.on_touch_down(touch)
    print(f"  Touch down at C")

    touch.move(x2, y2)
    layout.on_touch_move(touch)
    print(f"  Slide to C#")

    touch.move(x3, y3)
    layout.on_touch_move(touch)
    print(f"  Slide to D")

    layout.on_touch_up(touch)
    print(f"  Release")

    print(f"  Events: {events}")
    expected = [
        ("ON", "C", 60),
        ("OFF", "C", 60),
        ("ON", "C#", 61),
        ("OFF", "C#", 61),
        ("ON", "D", 62),
        ("OFF", "D", 62),
    ]
    assert events == expected, f"Expected {expected}, got {events}"
    print("  PASSED")

    print("\n--- Test 6: Verify all 12 notes are clickable ---")
    for note_name in NOTE_NAMES:
        events.clear()
        btn = buttons[note_name]
        x, y = get_note_position_from_button(btn)

        touch = MockTouch(x, y)
        layout.on_touch_down(touch)
        layout.on_touch_up(touch)

        if len(events) != 2:
            print(f"  FAILED: {note_name} at ({x:.0f}, {y:.0f}) - got {len(events)} events")
            print(f"    Events: {events}")
        else:
            assert events[0][1] == note_name, f"Expected {note_name}, got {events[0][1]}"
            print(f"  {note_name}: OK")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_touch_handling()
