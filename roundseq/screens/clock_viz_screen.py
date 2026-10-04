"""Clock visualization screen — concentric rings driven by incoming MIDI clock."""
from __future__ import annotations

from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Mesh
from kivy.graphics.instructions import InstructionGroup

from ..services import MidiInputService
from ..config import CENTER_X, CENTER_Y, DISPLAY_WIDTH, DISPLAY_HEIGHT, COLORS
from ..geometry import angle_span, polar_to_cartesian, arc_points

# MIDI clock is 24 pulses per quarter note.
CLOCKS_PER_BEAT = 24
BEATS_PER_MEASURE = 4
MEASURES_PER_PHRASE = 8
CLOCKS_PER_MEASURE = CLOCKS_PER_BEAT * BEATS_PER_MEASURE       # 96
CLOCKS_PER_PHRASE = CLOCKS_PER_MEASURE * MEASURES_PER_PHRASE   # 768

# Ring radii (px from center).
BEAT_RING_INNER = 310
BEAT_RING_OUTER = 405
MEASURE_RING_INNER = 420
MEASURE_RING_OUTER = 510

# Visual gap between adjacent segments, in degrees.
SEGMENT_GAP_DEG = 2.0

LIT_COLOR = (0.3, 0.8, 1.0, 1.0)
UNLIT_COLOR = (0.18, 0.20, 0.24, 1.0)

# Phrase-end indicator: when measure 8 starts, the measure-1 segment
# blinks three times to signal the phrase is about to loop.
BLINK_PERIOD = 0.15  # seconds per on or off phase
BLINK_COUNT = 3


def _segment_angles(num_segments: int, index: int) -> tuple[float, float]:
    """Return (start_angle, end_angle) for the i-th segment, clockwise from top.

    Angles are returned so that start < end after normalization can wrap;
    arc_points/angle_span handle the wrap.
    """
    step = 360.0 / num_segments
    half_gap = SEGMENT_GAP_DEG / 2.0
    # Segment occupies the wedge "centered" on its slot; clockwise from top means
    # decreasing angle as index increases. We swap start/end so arc rendering
    # (counter-clockwise) traces the same wedge correctly.
    start = (90.0 - step * (index + 1) + half_gap) % 360.0
    end = (90.0 - step * index - half_gap) % 360.0
    return start, end


class ClockVizScreen(FloatLayout):
    """Concentric-ring visualization of incoming MIDI clock.

    Inner ring: 4 segments, one lit per beat of the current measure.
    Outer ring: 8 segments, one lit per measure of the current 8-bar phrase.
    """

    def __init__(self, midi_input_service: MidiInputService = None, **kwargs):
        super().__init__(**kwargs)
        self.size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.size_hint = (None, None)

        self._midi = midi_input_service
        self._tick_count = 0
        self._running = False
        self._prev_measure_idx = -1
        self._blink_events: list = []
        self._measure1_blink_override: tuple | None = None

        # Background disk so corners outside the round display are clean.
        with self.canvas.before:
            Color(*COLORS["background"])
            self._bg = Ellipse(pos=(0, 0), size=self.size)

        # InstructionGroups holding the per-segment Color + Mesh.
        self._beat_segments: list[tuple[Color, InstructionGroup]] = []
        self._measure_segments: list[tuple[Color, InstructionGroup]] = []

        self._build_ring(
            BEATS_PER_MEASURE,
            BEAT_RING_INNER,
            BEAT_RING_OUTER,
            self._beat_segments,
        )
        self._build_ring(
            MEASURES_PER_PHRASE,
            MEASURE_RING_INNER,
            MEASURE_RING_OUTER,
            self._measure_segments,
        )

        # Center status label (BPM placeholder + running state).
        self._status = Label(
            text="--",
            font_size=48,
            color=COLORS["text"],
            size_hint=(None, None),
            size=(300, 120),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            halign="center",
            valign="middle",
        )
        self._status.bind(size=lambda *_: setattr(self._status, "text_size", self._status.size))
        self.add_widget(self._status)

        self._refresh_lights()

        if self._midi is not None:
            self._midi.subscribe(self._on_midi_message)

    def stop(self) -> None:
        """Unsubscribe from the MIDI input service."""
        self._cancel_blink()
        if self._midi is not None:
            self._midi.unsubscribe(self._on_midi_message)

    def _build_ring(self, num_segments, inner_radius, outer_radius, store):
        """Create Mesh instructions for one ring; appends (Color, group) tuples to store."""
        for i in range(num_segments):
            start, end = _segment_angles(num_segments, i)
            vertices, indices = self._slice_mesh(
                CENTER_X, CENTER_Y, inner_radius, outer_radius, start, end
            )
            group = InstructionGroup()
            color = Color(*UNLIT_COLOR)
            group.add(color)
            group.add(Mesh(vertices=vertices, indices=indices, mode="triangle_fan"))
            self.canvas.add(group)
            store.append((color, group))

    @staticmethod
    def _slice_mesh(cx, cy, inner_r, outer_r, start_angle, end_angle):
        """Build triangle-fan vertex/index lists for a ring segment."""
        span = angle_span(start_angle, end_angle)
        segments = max(8, int(span / 5))

        inner_pts = arc_points(cx, cy, inner_r, start_angle, end_angle, segments)
        outer_pts = arc_points(cx, cy, outer_r, start_angle, end_angle, segments)

        mid_angle = start_angle + span / 2
        mid_radius = (inner_r + outer_r) / 2
        fan_cx, fan_cy = polar_to_cartesian(cx, cy, mid_radius, mid_angle)

        vertices = [fan_cx, fan_cy, 0, 0]
        indices = [0]
        idx = 0
        for ox, oy in outer_pts:
            vertices.extend([ox, oy, 0, 0])
            idx += 1
            indices.append(idx)
        for ix, iy in reversed(inner_pts):
            vertices.extend([ix, iy, 0, 0])
            idx += 1
            indices.append(idx)
        indices.append(1)
        return vertices, indices

    def _on_midi_message(self, message) -> None:
        msg_type = getattr(message, "type", None)
        if msg_type == "clock":
            if self._running:
                self._tick_count += 1
                new_measure = (self._tick_count // CLOCKS_PER_MEASURE) % MEASURES_PER_PHRASE
                # Trigger the phrase-end blink on transition into the final measure.
                if new_measure == MEASURES_PER_PHRASE - 1 and self._prev_measure_idx != new_measure:
                    self._trigger_phrase_end_blink()
                self._prev_measure_idx = new_measure
                self._refresh_lights()
        elif msg_type == "start":
            self._tick_count = 0
            self._running = True
            self._prev_measure_idx = -1
            self._cancel_blink()
            self._refresh_lights()
        elif msg_type == "continue":
            self._running = True
        elif msg_type == "stop":
            self._running = False
            self._cancel_blink()
            self._refresh_lights()
        elif msg_type == "songpos":
            # songpos.pos counts 16th notes (6 clocks each).
            self._tick_count = int(getattr(message, "pos", 0)) * 6
            self._prev_measure_idx = (self._tick_count // CLOCKS_PER_MEASURE) % MEASURES_PER_PHRASE
            self._cancel_blink()
            self._refresh_lights()

    def _trigger_phrase_end_blink(self) -> None:
        """Blink the measure-1 segment three times as a phrase-loop heads-up."""
        self._cancel_blink()
        for i in range(BLINK_COUNT):
            on_t = i * (BLINK_PERIOD * 2)
            off_t = on_t + BLINK_PERIOD
            self._blink_events.append(Clock.schedule_once(self._blink_on, on_t))
            self._blink_events.append(Clock.schedule_once(self._blink_off, off_t))

    def _cancel_blink(self) -> None:
        for ev in self._blink_events:
            ev.cancel()
        self._blink_events = []
        self._measure1_blink_override = None

    def _blink_on(self, _dt) -> None:
        self._measure1_blink_override = LIT_COLOR
        self._refresh_lights()

    def _blink_off(self, _dt) -> None:
        self._measure1_blink_override = None
        self._refresh_lights()

    def _refresh_lights(self) -> None:
        beat_idx = (self._tick_count // CLOCKS_PER_BEAT) % BEATS_PER_MEASURE
        measure_idx = (self._tick_count // CLOCKS_PER_MEASURE) % MEASURES_PER_PHRASE

        for i, (color, _group) in enumerate(self._beat_segments):
            target = LIT_COLOR if (self._running and i == beat_idx) else UNLIT_COLOR
            color.rgba = target

        for i, (color, _group) in enumerate(self._measure_segments):
            if i == 0 and self._measure1_blink_override is not None:
                color.rgba = self._measure1_blink_override
            else:
                target = LIT_COLOR if (self._running and i == measure_idx) else UNLIT_COLOR
                color.rgba = target

        if self._running:
            self._status.text = f"{measure_idx + 1}.{beat_idx + 1}"
        else:
            self._status.text = "--"
