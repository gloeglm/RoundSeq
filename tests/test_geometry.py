"""Unit tests for geometry module."""
from __future__ import annotations

import math
import pytest

from roundseq.geometry import (
    normalize_angle,
    angle_span,
    angle_contains,
    polar_to_cartesian,
    cartesian_to_polar,
    point_in_circle,
    point_in_ring,
    point_in_arc,
    arc_points,
    arc_sector_points,
)


class TestNormalizeAngle:
    def test_already_normalized(self):
        assert normalize_angle(45) == 45
        assert normalize_angle(0) == 0
        assert normalize_angle(359) == 359

    def test_negative_angles(self):
        assert normalize_angle(-90) == 270
        assert normalize_angle(-180) == 180
        assert normalize_angle(-360) == 0
        assert normalize_angle(-450) == 270  # -450 + 720 = 270

    def test_large_angles(self):
        assert normalize_angle(360) == 0
        assert normalize_angle(450) == 90
        assert normalize_angle(720) == 0


class TestAngleSpan:
    def test_simple_span(self):
        assert angle_span(0, 90) == 90
        assert angle_span(45, 135) == 90

    def test_wrap_around(self):
        # 345 to 15 should be 30 degrees (through 0)
        assert angle_span(345, 15) == 30
        # 350 to 10 should be 20 degrees
        assert angle_span(350, 10) == 20

    def test_full_circle(self):
        # Same angle = 0 span (not 360)
        assert angle_span(90, 90) == 0

    def test_near_full_circle(self):
        # 10 to 350 going the "long way" = 340 degrees
        assert angle_span(10, 350) == 340


class TestAngleContains:
    def test_simple_range(self):
        assert angle_contains(45, 0, 90) is True
        assert angle_contains(0, 0, 90) is True
        assert angle_contains(90, 0, 90) is True
        assert angle_contains(91, 0, 90) is False

    def test_wrap_around(self):
        # Range from 345 to 15 (through 0)
        assert angle_contains(350, 345, 15) is True
        assert angle_contains(0, 345, 15) is True
        assert angle_contains(10, 345, 15) is True
        assert angle_contains(344, 345, 15) is False
        assert angle_contains(16, 345, 15) is False

    def test_boundary_at_zero(self):
        assert angle_contains(0, 350, 10) is True
        assert angle_contains(360, 350, 10) is True  # 360 normalizes to 0


class TestPolarToCartesian:
    def test_cardinal_directions(self):
        cx, cy = 100, 100
        r = 50

        # 0 degrees = right
        x, y = polar_to_cartesian(cx, cy, r, 0)
        assert x == pytest.approx(150)
        assert y == pytest.approx(100)

        # 90 degrees = up
        x, y = polar_to_cartesian(cx, cy, r, 90)
        assert x == pytest.approx(100)
        assert y == pytest.approx(150)

        # 180 degrees = left
        x, y = polar_to_cartesian(cx, cy, r, 180)
        assert x == pytest.approx(50)
        assert y == pytest.approx(100)

        # 270 degrees = down
        x, y = polar_to_cartesian(cx, cy, r, 270)
        assert x == pytest.approx(100)
        assert y == pytest.approx(50)

    def test_diagonal(self):
        cx, cy = 0, 0
        r = math.sqrt(2)  # So x and y will be 1

        x, y = polar_to_cartesian(cx, cy, r, 45)
        assert x == pytest.approx(1)
        assert y == pytest.approx(1)


class TestCartesianToPolar:
    def test_cardinal_directions(self):
        cx, cy = 100, 100

        # Right
        dist, angle = cartesian_to_polar(cx, cy, 150, 100)
        assert dist == pytest.approx(50)
        assert angle == pytest.approx(0)

        # Up
        dist, angle = cartesian_to_polar(cx, cy, 100, 150)
        assert dist == pytest.approx(50)
        assert angle == pytest.approx(90)

        # Left
        dist, angle = cartesian_to_polar(cx, cy, 50, 100)
        assert dist == pytest.approx(50)
        assert angle == pytest.approx(180)

        # Down
        dist, angle = cartesian_to_polar(cx, cy, 100, 50)
        assert dist == pytest.approx(50)
        assert angle == pytest.approx(270)

    def test_at_center(self):
        dist, angle = cartesian_to_polar(100, 100, 100, 100)
        assert dist == 0


class TestPointInCircle:
    def test_inside(self):
        assert point_in_circle(100, 100, 100, 100, 50) is True  # Center
        assert point_in_circle(120, 120, 100, 100, 50) is True  # Inside

    def test_on_boundary(self):
        assert point_in_circle(150, 100, 100, 100, 50) is True

    def test_outside(self):
        assert point_in_circle(151, 100, 100, 100, 50) is False
        assert point_in_circle(200, 200, 100, 100, 50) is False


class TestPointInRing:
    def test_inside_ring(self):
        # Ring from r=30 to r=50
        assert point_in_ring(140, 100, 100, 100, 30, 50) is True  # At r=40

    def test_on_boundaries(self):
        assert point_in_ring(130, 100, 100, 100, 30, 50) is True  # At r=30
        assert point_in_ring(150, 100, 100, 100, 30, 50) is True  # At r=50

    def test_outside_ring(self):
        assert point_in_ring(100, 100, 100, 100, 30, 50) is False  # Center (r=0)
        assert point_in_ring(120, 100, 100, 100, 30, 50) is False  # r=20
        assert point_in_ring(160, 100, 100, 100, 30, 50) is False  # r=60


class TestPointInArc:
    def test_inside_arc(self):
        # Arc from 45 to 135 degrees, r=30 to r=50
        cx, cy = 100, 100

        # Point at 90 degrees, r=40
        x, y = polar_to_cartesian(cx, cy, 40, 90)
        assert point_in_arc(x, y, cx, cy, 30, 50, 45, 135) is True

    def test_wrong_angle(self):
        cx, cy = 100, 100
        # Point at 0 degrees (outside 45-135 range), r=40
        x, y = polar_to_cartesian(cx, cy, 40, 0)
        assert point_in_arc(x, y, cx, cy, 30, 50, 45, 135) is False

    def test_wrong_radius(self):
        cx, cy = 100, 100
        # Point at 90 degrees, r=20 (inside inner radius)
        x, y = polar_to_cartesian(cx, cy, 20, 90)
        assert point_in_arc(x, y, cx, cy, 30, 50, 45, 135) is False

    def test_wrap_around_arc(self):
        # Arc from 345 to 15 degrees (through 0)
        cx, cy = 100, 100

        # Point at 0 degrees, r=40 (should be inside)
        x, y = polar_to_cartesian(cx, cy, 40, 0)
        assert point_in_arc(x, y, cx, cy, 30, 50, 345, 15) is True

        # Point at 350 degrees (should be inside)
        x, y = polar_to_cartesian(cx, cy, 40, 350)
        assert point_in_arc(x, y, cx, cy, 30, 50, 345, 15) is True

        # Point at 90 degrees (should be outside)
        x, y = polar_to_cartesian(cx, cy, 40, 90)
        assert point_in_arc(x, y, cx, cy, 30, 50, 345, 15) is False


class TestArcPoints:
    def test_generates_points(self):
        points = arc_points(100, 100, 50, 0, 90, segments=4)
        assert len(points) == 5  # 4 segments = 5 points

    def test_first_and_last(self):
        points = arc_points(100, 100, 50, 0, 90, segments=4)

        # First point at 0 degrees
        assert points[0][0] == pytest.approx(150)
        assert points[0][1] == pytest.approx(100)

        # Last point at 90 degrees
        assert points[-1][0] == pytest.approx(100)
        assert points[-1][1] == pytest.approx(150)

    def test_auto_segments(self):
        # 90 degrees / 5 = 18 segments, but minimum is 8
        points = arc_points(100, 100, 50, 0, 90)
        assert len(points) >= 9  # At least 8 segments + 1


class TestArcSectorPoints:
    def test_generates_closed_path(self):
        points = arc_sector_points(100, 100, 30, 50, 0, 90, segments=4)
        # 5 outer points + 5 inner points = 10
        assert len(points) == 10

    def test_outer_then_inner_reversed(self):
        points = arc_sector_points(100, 100, 30, 50, 0, 90, segments=2)

        # First point: outer arc at 0 degrees
        assert points[0][0] == pytest.approx(150)  # cx + outer_r

        # Middle (3rd point): outer arc at 90 degrees
        assert points[2][1] == pytest.approx(150)  # cy + outer_r

        # 4th point: inner arc at 90 degrees (first of reversed inner)
        assert points[3][1] == pytest.approx(130)  # cy + inner_r

        # Last point: inner arc at 0 degrees
        assert points[-1][0] == pytest.approx(130)  # cx + inner_r
