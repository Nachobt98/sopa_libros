"""Reusable monochrome editorial line-art motifs."""

from __future__ import annotations

from math import ceil, cos, floor, pi, radians, sin
from typing import Callable, Sequence

from PIL import Image, ImageDraw

from wordsearch.config.design import DecorationConfig, DecorationPlacement, LayoutConfig, PageType

Point = tuple[float, float]
Bounds = tuple[int, int, int, int]
MotifPainter = Callable[[ImageDraw.ImageDraw, Point, float, float, int, tuple[int, int, int, int]], None]


def _transform(
    point: Point,
    center: Point,
    size: float,
    rotation_degrees: float,
) -> tuple[float, float]:
    local_x = (point[0] - 50) * size / 100
    local_y = (point[1] - 50) * size / 100
    angle = radians(rotation_degrees)
    return (
        center[0] + local_x * cos(angle) - local_y * sin(angle),
        center[1] + local_x * sin(angle) + local_y * cos(angle),
    )


def _path(
    draw: ImageDraw.ImageDraw,
    points: Sequence[Point],
    center: Point,
    size: float,
    rotation_degrees: float,
    color: tuple[int, int, int, int],
    stroke: int,
    *,
    close: bool = False,
) -> None:
    if close and points:
        points = (*points, points[0])
    draw.line(
        [_transform(point, center, size, rotation_degrees) for point in points],
        fill=color,
        width=stroke,
        joint="curve",
    )


def _ellipse(
    draw: ImageDraw.ImageDraw,
    center_local: Point,
    radius_x: float,
    radius_y: float,
    center: Point,
    size: float,
    rotation_degrees: float,
    color: tuple[int, int, int, int],
    stroke: int,
) -> None:
    points = tuple(
        (
            center_local[0] + radius_x * cos(2 * pi * step / 40),
            center_local[1] + radius_y * sin(2 * pi * step / 40),
        )
        for step in range(41)
    )
    _path(draw, points, center, size, rotation_degrees, color, stroke)


def _arc(
    draw: ImageDraw.ImageDraw,
    center_local: Point,
    radius_x: float,
    radius_y: float,
    start_degrees: float,
    end_degrees: float,
    center: Point,
    size: float,
    rotation_degrees: float,
    color: tuple[int, int, int, int],
    stroke: int,
) -> None:
    count = max(8, int(abs(end_degrees - start_degrees) / 5))
    points = tuple(
        (
            center_local[0] + radius_x * cos(radians(start_degrees + (end_degrees - start_degrees) * step / count)),
            center_local[1] + radius_y * sin(radians(start_degrees + (end_degrees - start_degrees) * step / count)),
        )
        for step in range(count + 1)
    )
    _path(draw, points, center, size, rotation_degrees, color, stroke)


def _quadratic(start: Point, control: Point, end: Point, steps: int = 12) -> tuple[Point, ...]:
    return tuple(
        (
            (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0],
            (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1],
        )
        for t in (step / steps for step in range(steps + 1))
    )


def _leaf(
    draw: ImageDraw.ImageDraw,
    start: Point,
    end: Point,
    width: float,
    center: Point,
    size: float,
    rotation_degrees: float,
    color: tuple[int, int, int, int],
    stroke: int,
) -> None:
    direction_x = end[0] - start[0]
    direction_y = end[1] - start[1]
    length = max((direction_x**2 + direction_y**2) ** 0.5, 1)
    normal = (-direction_y / length, direction_x / length)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    upper = (midpoint[0] + normal[0] * width, midpoint[1] + normal[1] * width)
    lower = (midpoint[0] - normal[0] * width, midpoint[1] - normal[1] * width)
    points = (*_quadratic(start, upper, end), *_quadratic(end, lower, start)[1:])
    _path(draw, points, center, size, rotation_degrees, color, stroke)


def _star_points(points: int = 5, outer: float = 47, inner: float = 21) -> tuple[Point, ...]:
    return tuple(
        (
            50 + (outer if step % 2 == 0 else inner) * cos(-pi / 2 + step * pi / points),
            50 + (outer if step % 2 == 0 else inner) * sin(-pi / 2 + step * pi / points),
        )
        for step in range(points * 2)
    )


def _draw_star(draw, center, size, rotation, stroke, color):
    _path(draw, _star_points(), center, size, rotation, color, stroke, close=True)
    _ellipse(draw, (50, 50), 3, 3, center, size, rotation, color, stroke)


def _draw_snowflake(draw, center, size, rotation, stroke, color):
    for angle in (0, 60, 120):
        direction = (cos(radians(angle)), sin(radians(angle)))
        normal = (-direction[1], direction[0])
        _path(draw, ((50 - direction[0] * 45, 50 - direction[1] * 45), (50 + direction[0] * 45, 50 + direction[1] * 45)), center, size, rotation, color, stroke)
        for sign in (-1, 1):
            point = (50 + direction[0] * 29 * sign, 50 + direction[1] * 29 * sign)
            for branch in (-1, 1):
                end = (
                    point[0] - direction[0] * 13 * sign + normal[0] * 13 * branch,
                    point[1] - direction[1] * 13 * sign + normal[1] * 13 * branch,
                )
                _path(draw, (point, end), center, size, rotation, color, stroke)


def _draw_evergreen_tree(draw, center, size, rotation, stroke, color):
    _path(draw, ((50, 16), (27, 44), (38, 44), (22, 62), (36, 62), (17, 81), (83, 81), (64, 62), (78, 62), (62, 44), (73, 44), (50, 16)), center, size, rotation, color, stroke)
    _path(draw, ((50, 81), (50, 94)), center, size, rotation, color, stroke)
    _path(draw, ((40, 94), (60, 94)), center, size, rotation, color, stroke)


def _draw_bell(draw, center, size, rotation, stroke, color):
    _path(draw, ((37, 29), (40, 22), (46, 18), (54, 18), (60, 22), (63, 29), (67, 55), (77, 65), (23, 65), (33, 55), (37, 29)), center, size, rotation, color, stroke)
    _path(draw, ((20, 67), (80, 67)), center, size, rotation, color, stroke)
    _path(draw, ((44, 75), (50, 81), (56, 75)), center, size, rotation, color, stroke)
    _ellipse(draw, (50, 84), 4, 4, center, size, rotation, color, stroke)


def _draw_botanical_branch(draw, center, size, rotation, stroke, color):
    _path(draw, ((18, 83), (34, 69), (48, 54), (64, 39), (82, 18)), center, size, rotation, color, stroke)
    leaves = (
        ((32, 70), (18, 55)),
        ((42, 59), (58, 60)),
        ((53, 49), (39, 34)),
        ((64, 39), (80, 43)),
        ((72, 30), (62, 17)),
    )
    for base, tip in leaves:
        _leaf(draw, base, tip, 11, center, size, rotation, color, stroke)


def _draw_holly(draw, center, size, rotation, stroke, color):
    _path(draw, ((17, 59), (42, 53), (64, 48), (83, 39)), center, size, rotation, color, stroke)
    for start, end in (((31, 55), (19, 30)), ((47, 51), (58, 25)), ((63, 48), (81, 26))):
        _leaf(draw, start, end, 16, center, size, rotation, color, stroke)
        _path(draw, (start, end), center, size, rotation, color, max(1, stroke // 2))
    for point in ((75, 58), (84, 55), (80, 66)):
        _ellipse(draw, point, 4, 4, center, size, rotation, color, stroke)


def _draw_lantern(draw, center, size, rotation, stroke, color):
    _arc(draw, (50, 25), 17, 18, 200, 340, center, size, rotation, color, stroke)
    _path(draw, ((39, 35), (32, 42), (32, 72), (39, 81), (61, 81), (68, 72), (68, 42), (61, 35), (39, 35)), center, size, rotation, color, stroke)
    _path(draw, ((28, 43), (72, 43)), center, size, rotation, color, stroke)
    _path(draw, ((28, 72), (72, 72)), center, size, rotation, color, stroke)
    _path(draw, ((50, 44), (50, 70)), center, size, rotation, color, stroke)
    _path(draw, ((39, 84), (61, 84)), center, size, rotation, color, stroke)


def _draw_candle(draw, center, size, rotation, stroke, color):
    _path(draw, ((50, 9), (61, 25), (58, 39), (50, 45), (42, 39), (39, 25), (50, 9)), center, size, rotation, color, stroke)
    _path(draw, ((50, 45), (50, 52)), center, size, rotation, color, stroke)
    _path(draw, ((38, 49), (38, 81), (43, 88), (57, 88), (62, 81), (62, 49)), center, size, rotation, color, stroke)
    _arc(draw, (50, 49), 12, 4, 180, 360, center, size, rotation, color, stroke)
    _path(draw, ((38, 88), (62, 88)), center, size, rotation, color, stroke)


def _draw_gift(draw, center, size, rotation, stroke, color):
    _path(draw, ((22, 41), (78, 41), (78, 83), (22, 83), (22, 41)), center, size, rotation, color, stroke)
    _path(draw, ((17, 33), (83, 33), (83, 44), (17, 44), (17, 33)), center, size, rotation, color, stroke)
    _path(draw, ((50, 34), (50, 83)), center, size, rotation, color, stroke)
    _path(draw, ((17, 84), (83, 84)), center, size, rotation, color, stroke)
    _ellipse(draw, (39, 22), 11, 8, center, size, rotation, color, stroke)
    _ellipse(draw, (61, 22), 11, 8, center, size, rotation, color, stroke)
    _path(draw, ((50, 29), (50, 34)), center, size, rotation, color, stroke)


def _draw_ornament(draw, center, size, rotation, stroke, color):
    _ellipse(draw, (50, 56), 30, 30, center, size, rotation, color, stroke)
    _path(draw, ((43, 24), (43, 17), (57, 17), (57, 24)), center, size, rotation, color, stroke)
    _arc(draw, (50, 14), 7, 7, 180, 360, center, size, rotation, color, stroke)
    _arc(draw, (50, 56), 27, 11, 200, 340, center, size, rotation, color, stroke)
    _arc(draw, (50, 56), 27, 11, 20, 160, center, size, rotation, color, stroke)


def _draw_flower(draw, center, size, rotation, stroke, color):
    for angle in range(0, 360, 45):
        endpoint = (50 + 34 * cos(radians(angle)), 50 + 34 * sin(radians(angle)))
        _leaf(draw, (50, 50), endpoint, 14, center, size, rotation, color, stroke)
    _ellipse(draw, (50, 50), 12, 12, center, size, rotation, color, stroke)
    _path(draw, ((50, 62), (50, 90)), center, size, rotation, color, stroke)
    _leaf(draw, (50, 76), (31, 66), 8, center, size, rotation, color, stroke)
    _leaf(draw, (50, 82), (69, 72), 8, center, size, rotation, color, stroke)


def _draw_house(draw, center, size, rotation, stroke, color):
    _path(draw, ((18, 48), (50, 18), (82, 48), (75, 48), (75, 83), (25, 83), (25, 48), (18, 48)), center, size, rotation, color, stroke)
    _path(draw, ((43, 83), (43, 62), (57, 62), (57, 83)), center, size, rotation, color, stroke)
    _path(draw, ((31, 52), (40, 52), (40, 61), (31, 61), (31, 52)), center, size, rotation, color, stroke)
    _path(draw, ((60, 52), (69, 52), (69, 61), (60, 61), (60, 52)), center, size, rotation, color, stroke)
    _path(draw, ((67, 35), (67, 25), (74, 25), (74, 42)), center, size, rotation, color, stroke)


def _draw_star_lantern(draw, center, size, rotation, stroke, color):
    _path(draw, ((50, 7), (57, 36), (84, 20), (68, 47), (96, 54), (68, 61), (84, 88), (57, 72), (50, 99), (43, 72), (16, 88), (32, 61), (4, 54), (32, 47), (16, 20), (43, 36), (50, 7)), center, size, rotation, color, stroke)
    _path(draw, ((50, 0), (50, 7)), center, size, rotation, color, stroke)
    _path(draw, ((50, 23), (50, 85)), center, size, rotation, color, stroke)
    _path(draw, ((32, 54), (68, 54)), center, size, rotation, color, stroke)


def _draw_globe(draw, center, size, rotation, stroke, color):
    _ellipse(draw, (50, 48), 37, 37, center, size, rotation, color, stroke)
    _ellipse(draw, (50, 48), 16, 37, center, size, rotation, color, stroke)
    _arc(draw, (50, 48), 35, 17, 0, 180, center, size, rotation, color, stroke)
    _arc(draw, (50, 48), 35, 17, 180, 360, center, size, rotation, color, stroke)
    _path(draw, ((50, 85), (50, 91), (36, 91), (64, 91)), center, size, rotation, color, stroke)


def _draw_compass(draw, center, size, rotation, stroke, color):
    _ellipse(draw, (50, 52), 39, 39, center, size, rotation, color, stroke)
    _path(draw, ((50, 13), (55, 48), (50, 52), (45, 48), (50, 13)), center, size, rotation, color, stroke)
    _path(draw, ((50, 91), (45, 56), (50, 52), (55, 56), (50, 91)), center, size, rotation, color, stroke)
    _path(draw, ((11, 52), (46, 47), (50, 52), (46, 57), (11, 52)), center, size, rotation, color, stroke)
    _path(draw, ((89, 52), (54, 57), (50, 52), (54, 47), (89, 52)), center, size, rotation, color, stroke)
    _ellipse(draw, (50, 52), 4, 4, center, size, rotation, color, stroke)


def _draw_geometric_ornament(draw, center, size, rotation, stroke, color):
    octagon = tuple(
        (50 + 39 * cos(radians(-22.5 + step * 45)), 50 + 39 * sin(radians(-22.5 + step * 45)))
        for step in range(8)
    )
    _path(draw, octagon, center, size, rotation, color, stroke, close=True)
    _path(draw, ((50, 13), (76, 50), (50, 87), (24, 50), (50, 13)), center, size, rotation, color, stroke)
    _path(draw, ((24, 50), (76, 50)), center, size, rotation, color, stroke)
    _path(draw, ((50, 13), (50, 87)), center, size, rotation, color, stroke)


def _draw_garland(draw, center, size, rotation, stroke, color):
    points = tuple((5 + step * 90 / 48, 34 + 15 * sin(step * 2 * pi / 48)) for step in range(49))
    _path(draw, points, center, size, rotation, color, stroke)
    for x, y in ((18, 41), (36, 48), (54, 48), (72, 41)):
        _leaf(draw, (x, y), (x + 5, y + 14), 5, center, size, rotation, color, stroke)
    for x, y in ((26, 43), (46, 49), (66, 45)):
        _ellipse(draw, (x, y), 2, 2, center, size, rotation, color, stroke)


_MOTIF_DRAWERS: dict[str, MotifPainter] = {
    "star": _draw_star,
    "snowflake": _draw_snowflake,
    "evergreen_tree": _draw_evergreen_tree,
    "bell": _draw_bell,
    "botanical_branch": _draw_botanical_branch,
    "holly": _draw_holly,
    "lantern": _draw_lantern,
    "candle": _draw_candle,
    "gift": _draw_gift,
    "ornament": _draw_ornament,
    "flower": _draw_flower,
    "house": _draw_house,
    "star_lantern": _draw_star_lantern,
    "globe": _draw_globe,
    "compass": _draw_compass,
    "geometric_ornament": _draw_geometric_ornament,
    "garland": _draw_garland,
}


def draw_page_decorations(
    image: Image.Image,
    config: DecorationConfig,
    page_type: PageType,
    layout: LayoutConfig,
    *,
    scale: int = 1,
    region_bounds: Bounds | None = None,
) -> tuple[Bounds, ...]:
    """Draw configured motifs and return their safe bounding boxes."""
    page_config = config.for_page(page_type)
    if page_config is None:
        return ()
    if image.mode != "RGBA":
        raise ValueError("Decorations require an RGBA page canvas.")
    if scale <= 0 or image.size != (layout.page_width_px * scale, layout.page_height_px * scale):
        raise ValueError("Decoration canvas size must match the layout and scale.")

    safe_bounds = (
        layout.safe_left_px * scale,
        layout.safe_top_px * scale,
        layout.safe_right_px * scale,
        layout.safe_bottom_px * scale,
    )
    if page_config.region == "separator":
        if region_bounds is None:
            raise ValueError("The separator region requires explicit bounds.")
        draw_bounds = region_bounds
    else:
        draw_bounds = safe_bounds

    if not (
        safe_bounds[0] <= draw_bounds[0] < draw_bounds[2] <= safe_bounds[2]
        and safe_bounds[1] <= draw_bounds[1] < draw_bounds[3] <= safe_bounds[3]
    ):
        raise ValueError("Decoration region must remain inside the layout safe area.")

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    boxes = []
    for placement in page_config.placements:
        box = _draw_placement(
            draw,
            placement,
            draw_bounds,
            safe_bounds,
            layout,
            scale,
        )
        boxes.append(box)
    image.alpha_composite(overlay)
    return tuple(boxes)


def _draw_placement(
    draw: ImageDraw.ImageDraw,
    placement: DecorationPlacement,
    region: Bounds,
    safe_bounds: Bounds,
    layout: LayoutConfig,
    scale: int,
) -> Bounds:
    left, top, right, bottom = region
    center = (left + placement.x * (right - left), top + placement.y * (bottom - top))
    size = min(layout.page_width_px, layout.page_height_px) * scale * placement.size_ratio
    stroke = max(1, round(size * placement.stroke_width_ratio))
    radius = size / 2 + stroke / 2
    box = (
        floor(center[0] - radius),
        floor(center[1] - radius),
        ceil(center[0] + radius),
        ceil(center[1] + radius),
    )
    if not (
        safe_bounds[0] <= box[0] <= box[2] <= safe_bounds[2]
        and safe_bounds[1] <= box[1] <= box[3] <= safe_bounds[3]
        and left <= box[0] <= box[2] <= right
        and top <= box[1] <= box[3] <= bottom
    ):
        raise ValueError(f"Decoration motif '{placement.motif}' exceeds its reserved safe area.")

    alpha = round(255 * placement.opacity)
    color = (placement.color, placement.color, placement.color, alpha)
    _MOTIF_DRAWERS[placement.motif](
        draw,
        center,
        size,
        placement.rotation_degrees,
        stroke,
        color,
    )
    return box
