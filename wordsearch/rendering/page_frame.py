"""Shared page frame helpers for puzzle-like renderers."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from wordsearch.config.layout import (
    PAGE_H_PX,
    PAGE_W_PX,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    TOP_PX,
)
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


def create_page_canvas(background_path: str | None, scale: int) -> Image.Image:
    """Create a high-resolution page canvas with optional translucent background."""
    page_w_hi = PAGE_W_PX * scale
    page_h_hi = PAGE_H_PX * scale
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((page_w_hi, page_h_hi), Image.LANCZOS)

        if bg.mode == "RGBA":
            red, green, blue, alpha = bg.split()
            alpha = alpha.point(lambda value: int(value * 0.7))
            bg = Image.merge("RGBA", (red, green, blue, alpha))

        return bg

    return Image.new("RGBA", (page_w_hi, page_h_hi), (255, 255, 255, 255))


def draw_page_frame(
    *,
    draw: ImageDraw.ImageDraw,
    scale: int,
    title_area_hi: int | None = None,
) -> PageFrame:
    """Draw the shared white content panel and return its layout bounds."""
    page_w_hi = PAGE_W_PX * scale
    page_h_hi = PAGE_H_PX * scale
    safe_left_hi = SAFE_LEFT * scale
    safe_right_hi = SAFE_RIGHT * scale
    safe_bottom_hi = SAFE_BOTTOM * scale
    top_px_hi = TOP_PX * scale

    panel_pad_x = int(30 * scale)
    panel_pad_top = int(40 * scale)
    panel_pad_bottom = int(40 * scale)

    panel_left = max(0, safe_left_hi - panel_pad_x)
    panel_top = max(0, top_px_hi - panel_pad_top)
    panel_right = min(page_w_hi, safe_right_hi + panel_pad_x)
    panel_bottom = min(page_h_hi, safe_bottom_hi + panel_pad_bottom)

    rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(35 * scale),
        fill=(255, 255, 255, 150),
        outline=(0, 0, 0, 60),
        width=max(1, int(3 * scale)),
    )

    content_margin_x = int(40 * scale)
    title_area_hi = title_area_hi if title_area_hi is not None else int(600 * scale)

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
) -> int:
    """Draw a centered wrapped title and return the y coordinate after it."""
    lines = wrap_text(draw, text, font, max_width)
    y = start_y
    container_width = max(0, area_right - area_left)
    for line in lines:
        width, height = text_size(draw, line, font)
        x = area_left + max(0, (container_width - width) // 2)
        draw.text((x, y), line, font=font, fill=(0, 0, 0, 255))
        y += int(height * line_spacing)
    return y
