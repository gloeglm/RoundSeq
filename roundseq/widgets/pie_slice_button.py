"""Pie slice button widget for circular note layout."""
from __future__ import annotations

import math

from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty,
    BooleanProperty,
)
from kivy.graphics import Color, Ellipse, Line, Triangle, Mesh
from kivy.graphics.instructions import InstructionGroup

from ..config import COLORS


class PieSliceButton(Widget):
    """A button shaped like a pie slice for circular layouts.

    The slice is defined by:
    - center_x, center_y: Center of the circle
    - inner_radius: Distance from center to inner arc
    - outer_radius: Distance from center to outer arc
    - start_angle: Starting angle in degrees (0 = right, 90 = up)
    - end_angle: Ending angle in degrees
    """

    inner_radius = NumericProperty(100)
    outer_radius = NumericProperty(200)
    start_angle = NumericProperty(0)
    end_angle = NumericProperty(30)
    label_text = StringProperty("")
    is_sharp = BooleanProperty(False)
    is_pressed_state = BooleanProperty(False)
    note_index = NumericProperty(0)  # For debug coloring

    background_color = ListProperty(COLORS["button_normal"])
    pressed_color = ListProperty(COLORS["button_pressed"])
    text_color = ListProperty(COLORS["text"])

    # Debug colors for each note (hue-based rainbow)
    DEBUG_COLORS = True  # Set to False to disable

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gfx = InstructionGroup()
        self.canvas.add(self._gfx)
        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics,
            inner_radius=self._update_graphics,
            outer_radius=self._update_graphics,
            start_angle=self._update_graphics,
            end_angle=self._update_graphics,
            is_pressed_state=self._update_graphics,
            is_sharp=self._update_graphics,
        )
        self._update_graphics()

    def _get_debug_color(self):
        """Get a unique color for this note based on index."""
        import colorsys
        hue = self.note_index / 12.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.8)
        return (r, g, b, 1)

    def _update_graphics(self, *args):
        """Redraw the pie slice."""
        self._gfx.clear()

        # Determine color based on state
        if self.is_pressed_state:
            color = self.pressed_color
        elif self.DEBUG_COLORS:
            color = self._get_debug_color()
        elif self.is_sharp:
            color = COLORS["button_sharp"]
        else:
            color = self.background_color

        self._gfx.add(Color(*color))

        # Generate vertices for the pie slice
        vertices, indices = self._generate_slice_mesh()
        if vertices and indices:
            self._gfx.add(
                Mesh(vertices=vertices, indices=indices, mode="triangle_fan")
            )

        # Draw outline
        self._gfx.add(Color(0.3, 0.3, 0.35, 1))
        outline_points = self._generate_outline_points()
        if len(outline_points) >= 4:
            self._gfx.add(Line(points=outline_points, width=1.2, close=True))

    def _get_angle_span(self):
        """Get the angular span, handling wrap-around."""
        if self.end_angle >= self.start_angle:
            return self.end_angle - self.start_angle
        else:
            # Wrap-around case (e.g., 345 to 15 = 30 degrees through 0)
            return (360 - self.start_angle) + self.end_angle

    def _generate_slice_mesh(self) -> tuple[list, list]:
        """Generate mesh vertices for the pie slice."""
        cx = self.center_x
        cy = self.center_y

        # Calculate angle span handling wrap-around
        angle_span = self._get_angle_span()
        segments = max(8, int(angle_span / 5))

        vertices = []
        indices = []

        # Generate points along inner and outer arcs
        inner_points = []
        outer_points = []

        for i in range(segments + 1):
            t = i / segments
            # Interpolate angle, handling wrap-around
            angle_deg = self.start_angle + t * angle_span
            angle = math.radians(angle_deg)

            # Inner arc point
            ix = cx + self.inner_radius * math.cos(angle)
            iy = cy + self.inner_radius * math.sin(angle)
            inner_points.append((ix, iy))

            # Outer arc point
            ox = cx + self.outer_radius * math.cos(angle)
            oy = cy + self.outer_radius * math.sin(angle)
            outer_points.append((ox, oy))

        # Build triangle fan from center of slice
        # Calculate center point of the slice for the fan
        mid_angle_deg = self.start_angle + angle_span / 2
        mid_angle = math.radians(mid_angle_deg)
        mid_radius = (self.inner_radius + self.outer_radius) / 2
        fan_cx = cx + mid_radius * math.cos(mid_angle)
        fan_cy = cy + mid_radius * math.sin(mid_angle)

        # Add center vertex (texture coords 0, 0)
        vertices.extend([fan_cx, fan_cy, 0, 0])
        idx = 0

        # Add outer arc vertices
        for ox, oy in outer_points:
            vertices.extend([ox, oy, 0, 0])
            idx += 1
            indices.append(idx)

        # Add inner arc vertices (in reverse for proper winding)
        for ix, iy in reversed(inner_points):
            vertices.extend([ix, iy, 0, 0])
            idx += 1
            indices.append(idx)

        # Close the fan
        indices.append(1)

        # Prepend center index
        indices = [0] + indices

        return vertices, indices

    def _generate_outline_points(self) -> list:
        """Generate points for the outline."""
        cx = self.center_x
        cy = self.center_y
        points = []

        angle_span = self._get_angle_span()
        segments = max(8, int(angle_span / 5))

        # Outer arc (start to end)
        for i in range(segments + 1):
            t = i / segments
            angle_deg = self.start_angle + t * angle_span
            angle = math.radians(angle_deg)
            x = cx + self.outer_radius * math.cos(angle)
            y = cy + self.outer_radius * math.sin(angle)
            points.extend([x, y])

        # Inner arc (end to start)
        for i in range(segments + 1):
            t = i / segments
            angle_deg = self.start_angle + angle_span - t * angle_span
            angle = math.radians(angle_deg)
            x = cx + self.inner_radius * math.cos(angle)
            y = cy + self.inner_radius * math.sin(angle)
            points.extend([x, y])

        return points

    def collide_point(self, x, y):
        """Check if point is within the pie slice."""
        dx = x - self.center_x
        dy = y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        # Check radius bounds
        if not (self.inner_radius <= distance <= self.outer_radius):
            return False

        # Check angle bounds
        angle = math.degrees(math.atan2(dy, dx))
        # Normalize angle to 0-360
        if angle < 0:
            angle += 360

        start = self.start_angle % 360
        end = self.end_angle % 360

        # Handle wrap-around case
        if start <= end:
            return start <= angle <= end
        else:
            return angle >= start or angle <= end
