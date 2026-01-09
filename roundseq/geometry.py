"""Pure functions for radial/circular geometry calculations."""
from __future__ import annotations

import math


def normalize_angle(degrees: float) -> float:
    """Normalize angle to 0-360 range.

    Args:
        degrees: Angle in degrees (can be negative or > 360)

    Returns:
        Angle normalized to [0, 360)
    """
    return degrees % 360


def angle_span(start: float, end: float) -> float:
    """Get angular span between two angles, handling wrap-around.

    Args:
        start: Start angle in degrees
        end: End angle in degrees

    Returns:
        Positive span in degrees (e.g., 345 to 15 = 30)
    """
    start = normalize_angle(start)
    end = normalize_angle(end)
    if end >= start:
        return end - start
    else:
        return (360 - start) + end


def angle_contains(angle: float, start: float, end: float) -> bool:
    """Check if angle is within range, handling wrap-around.

    Args:
        angle: Angle to check (degrees)
        start: Start of range (degrees)
        end: End of range (degrees)

    Returns:
        True if angle is within [start, end], handling wrap-around
    """
    angle = normalize_angle(angle)
    start = normalize_angle(start)
    end = normalize_angle(end)

    if start <= end:
        return start <= angle <= end
    else:
        # Wrap-around case (e.g., 345 to 15)
        return angle >= start or angle <= end


def polar_to_cartesian(cx: float, cy: float, radius: float, angle_deg: float) -> tuple[float, float]:
    """Convert polar coordinates to cartesian.

    Args:
        cx: Center x coordinate
        cy: Center y coordinate
        radius: Distance from center
        angle_deg: Angle in degrees (0 = right, 90 = up)

    Returns:
        (x, y) cartesian coordinates
    """
    angle_rad = math.radians(angle_deg)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return (x, y)


def cartesian_to_polar(cx: float, cy: float, x: float, y: float) -> tuple[float, float]:
    """Convert cartesian coordinates to polar.

    Args:
        cx: Center x coordinate
        cy: Center y coordinate
        x: Point x coordinate
        y: Point y coordinate

    Returns:
        (distance, angle_deg) where angle is in [0, 360)
    """
    dx = x - cx
    dy = y - cy
    distance = math.sqrt(dx * dx + dy * dy)
    angle_deg = math.degrees(math.atan2(dy, dx))
    return (distance, normalize_angle(angle_deg))


def point_in_circle(x: float, y: float, cx: float, cy: float, radius: float) -> bool:
    """Check if point is inside a circle.

    Uses squared distance to avoid sqrt overhead.

    Args:
        x, y: Point coordinates
        cx, cy: Circle center
        radius: Circle radius

    Returns:
        True if point is inside or on the circle
    """
    dx = x - cx
    dy = y - cy
    return (dx * dx + dy * dy) <= (radius * radius)


def point_in_ring(x: float, y: float, cx: float, cy: float,
                  inner_radius: float, outer_radius: float) -> bool:
    """Check if point is inside a ring/annulus.

    Uses squared distance to avoid sqrt overhead.

    Args:
        x, y: Point coordinates
        cx, cy: Ring center
        inner_radius: Inner radius of ring
        outer_radius: Outer radius of ring

    Returns:
        True if point is within the ring
    """
    dx = x - cx
    dy = y - cy
    dist_sq = dx * dx + dy * dy
    return (inner_radius * inner_radius) <= dist_sq <= (outer_radius * outer_radius)


def point_in_arc(x: float, y: float, cx: float, cy: float,
                 inner_radius: float, outer_radius: float,
                 start_angle: float, end_angle: float) -> bool:
    """Check if point is inside a pie slice / arc sector.

    Args:
        x, y: Point coordinates
        cx, cy: Arc center
        inner_radius: Inner radius
        outer_radius: Outer radius
        start_angle: Start angle in degrees
        end_angle: End angle in degrees

    Returns:
        True if point is within the arc sector
    """
    # First check radius bounds (fast rejection)
    if not point_in_ring(x, y, cx, cy, inner_radius, outer_radius):
        return False

    # Then check angle bounds
    _, angle = cartesian_to_polar(cx, cy, x, y)
    return angle_contains(angle, start_angle, end_angle)


def arc_points(cx: float, cy: float, radius: float,
               start_angle: float, end_angle: float,
               segments: int = None) -> list[tuple[float, float]]:
    """Generate points along an arc for rendering.

    Args:
        cx, cy: Arc center
        radius: Arc radius
        start_angle: Start angle in degrees
        end_angle: End angle in degrees
        segments: Number of segments (auto-calculated if None)

    Returns:
        List of (x, y) points along the arc
    """
    span = angle_span(start_angle, end_angle)

    if segments is None:
        # Auto-calculate: roughly one segment per 5 degrees, minimum 8
        segments = max(8, int(span / 5))

    points = []
    for i in range(segments + 1):
        t = i / segments
        angle = start_angle + t * span
        points.append(polar_to_cartesian(cx, cy, radius, angle))

    return points


def arc_sector_points(cx: float, cy: float,
                      inner_radius: float, outer_radius: float,
                      start_angle: float, end_angle: float,
                      segments: int = None) -> list[tuple[float, float]]:
    """Generate points for a pie slice / arc sector outline.

    Points are ordered: outer arc (start to end), inner arc (end to start).
    Suitable for creating a closed polygon.

    Args:
        cx, cy: Center coordinates
        inner_radius: Inner radius
        outer_radius: Outer radius
        start_angle: Start angle in degrees
        end_angle: End angle in degrees
        segments: Number of segments per arc (auto-calculated if None)

    Returns:
        List of (x, y) points forming the sector outline
    """
    outer_pts = arc_points(cx, cy, outer_radius, start_angle, end_angle, segments)
    inner_pts = arc_points(cx, cy, inner_radius, start_angle, end_angle, segments)

    # Outer arc forward, then inner arc backward to close the shape
    return outer_pts + list(reversed(inner_pts))
