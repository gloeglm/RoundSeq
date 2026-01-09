"""Pie slice button widget for circular note layout."""
from __future__ import annotations

from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty,
    BooleanProperty,
)
from kivy.graphics import Color, Line, Mesh
from kivy.graphics.instructions import InstructionGroup

from ..config import COLORS
from ..geometry import (
    angle_span,
    polar_to_cartesian,
    point_in_arc,
    arc_points,
)


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

    def _generate_slice_mesh(self) -> tuple[list, list]:
        """Generate mesh vertices for the pie slice."""
        cx = self.center_x
        cy = self.center_y

        span = angle_span(self.start_angle, self.end_angle)
        segments = max(8, int(span / 5))

        # Generate arc points using geometry module
        inner_pts = arc_points(cx, cy, self.inner_radius,
                               self.start_angle, self.end_angle, segments)
        outer_pts = arc_points(cx, cy, self.outer_radius,
                               self.start_angle, self.end_angle, segments)

        # Build triangle fan from center of slice
        mid_angle = self.start_angle + span / 2
        mid_radius = (self.inner_radius + self.outer_radius) / 2
        fan_cx, fan_cy = polar_to_cartesian(cx, cy, mid_radius, mid_angle)

        vertices = []
        indices = []

        # Add center vertex (texture coords 0, 0)
        vertices.extend([fan_cx, fan_cy, 0, 0])
        idx = 0

        # Add outer arc vertices
        for ox, oy in outer_pts:
            vertices.extend([ox, oy, 0, 0])
            idx += 1
            indices.append(idx)

        # Add inner arc vertices (in reverse for proper winding)
        for ix, iy in reversed(inner_pts):
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

        span = angle_span(self.start_angle, self.end_angle)
        segments = max(8, int(span / 5))

        # Get arc points
        outer_pts = arc_points(cx, cy, self.outer_radius,
                               self.start_angle, self.end_angle, segments)
        inner_pts = arc_points(cx, cy, self.inner_radius,
                               self.start_angle, self.end_angle, segments)

        # Flatten to list: outer arc forward, inner arc backward
        points = []
        for x, y in outer_pts:
            points.extend([x, y])
        for x, y in reversed(inner_pts):
            points.extend([x, y])

        return points

    def collide_point(self, x, y):
        """Check if point is within the pie slice."""
        return point_in_arc(
            x, y,
            self.center_x, self.center_y,
            self.inner_radius, self.outer_radius,
            self.start_angle, self.end_angle
        )
