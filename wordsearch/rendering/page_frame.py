"""Shared page frame helpers for puzzle-like renderers."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from wordsearch.config.design import DEFAULT_LAYOUT, DEFAULT_THEME, ThemeConfig
from wordsearch.rendering.backgrounds import BACKGROUND_PATH
from wordsearch.rendering.common import rounded_rectangle, text_size, wrap_text


@dataclass(frozen=True)
class PageFrame:
    scale: int
    page_w_hi: int
    page_h_hi: int
    safe_bottom_hi: int
    panel_left: int
    panel_top: int
    panel_right: int
    panel_bottom: int
    content_left_hi: int
    content_right_hi: int
    grid_top_base: int


def create_page_canvas(
    background_path: str | None,
    scale: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
) -> Image.Image:
    """Create a high-resolution page canvas with optional translucent background."""
    page_w_hi = DEFAULT_LAYOUT.page_width_px * scale
    page_h_hi = DEFAULT_LAYOUT.page_height_px * scale
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((page_w_hi, page_h_hi), Image.LANCZOS)

        if bg.mode == "RGBA":
            red, green, blue, alpha = bg.split()
            alpha = alpha.point(lambda value: int(value * theme.background_opacity))
            bg = Image.merge("RGBA", (red, green, blue, alpha))

        return bg

    return Image.new("RGBA", (page_w_hi, page_h_hi), theme.page_background_fill)


def draw_page_frame(
    *,
    draw: ImageDraw.ImageDraw,
    scale: int,
    title_area_hi: int | None = None,
    theme: ThemeConfig = DEFAULT_THEME,
) -> PageFrame:
    """Draw the shared white content panel and return its layout bounds."""
    page_w_hi = DEFAULT_LAYOUT.page_width_px * scale
    page_h_hi = DEFAULT_LAYOUT.page_height_px * scale
    safe_left_hi = DEFAULT_LAYOUT.safe_left_px * scale
    safe_right_hi = DEFAULT_LAYOUT.safe_right_px * scale
    safe_bottom_hi = DEFAULT_LAYOUT.safe_bottom_px * scale
    top_px_hi = DEFAULT_LAYOUT.top_px * scale

    panel_pad_x = int(DEFAULT_LAYOUT.panel_pad_x_px * scale)
    panel_pad_top = int(DEFAULT_LAYOUT.panel_pad_top_px * scale)
    panel_pad_bottom = int(DEFAULT_LAYOUT.panel_pad_bottom_px * scale)

    panel_left = max(0, safe_left_hi - panel_pad_x)
    panel_top = max(0, top_px_hi - panel_pad_top)
    panel_right = min(page_w_hi, safe_right_hi + panel_pad_x)
    panel_bottom = min(page_h_hi, safe_bottom_hi + panel_pad_bottom)

    rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(theme.panel_radius_px * scale),
        fill=theme.panel_fill,
        outline=theme.panel_border,
        width=max(1, int(theme.panel_border_width_px * scale)),
    )

    content_margin_x = int(DEFAULT_LAYOUT.content_margin_x_px * scale)
    title_area_hi = (
        title_area_hi
        if title_area_hi is not None
        else int(DEFAULT_LAYOUT.default_title_area_px * scale)
    )

    return PageFrame(
        scale=scale,
        page_w_hi=page_w_hi,
        page_h_hi=page_h_hi,
        safe_bottom_hi=safe_bottom_hi,
        panel_left=panel_left,
        panel_top=panel_top,
        panel_right=panel_right,
        panel_bottom=panel_bottom,
        content_left_hi=panel_left + content_margin_x,
        content_right_hi=panel_right - content_margin_x,
        grid_top_base=panel_top + title_area_hi,
    )


def draw_wrapped_centered_title(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    start_y: int,
    area_left: int,
    area_right: int,
    line_spacing: float = 1.05,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
) -> int:
    """Draw a centered wrapped title and return the y coordinate after it."""
    lines = wrap_text(draw, text, font, max_width)
    y = start_y
    container_width = max(0, area_right - area_left)
    for line in lines:
        width, height = text_size(draw, line, font)
        x = area_left + max(0, (container_width - width) // 2)
        draw.text((x, y), line, font=font, fill=theme.title_color)
        y += int(height * line_spacing)
    return y
