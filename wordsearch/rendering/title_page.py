"""
Renderizado de la portada interior del libro temático.

Esta página no es la cubierta de KDP, sino una title page interior que aparece
antes del índice para dar al PDF una estructura más editorial.
"""

from __future__ import annotations

import os
from typing import Optional

from PIL import Image, ImageDraw

from wordsearch.constants_and_layout import (
    FONT_PATH,
    FONT_TITLE,
    PAGE_H_PX,
    PAGE_W_PX,
    wordlist_font_size as WORDLIST_FONT_SIZE,
    title_font_size as TITLE_FONT_SIZE,
)
from wordsearch.image_rendering import BACKGROUND_PATH
from wordsearch.rendering.common import (
    draw_centered_lines,
    load_font,
    save_page,
    text_size,
    wrap_text,
)


def _draw_soft_panel(draw: ImageDraw.ImageDraw, scale: int) -> None:
    """Draw a compact editorial panel, leaving visible textured background."""
    margin_x = int(135 * scale)
    margin_top = int(210 * scale)
    margin_bottom = int(760 * scale)
    radius = int(30 * scale)
    outline_width = max(1, int(2 * scale))

    draw.rounded_rectangle(
        (
            margin_x,
            margin_top,
            PAGE_W_PX * scale - margin_x,
            PAGE_H_PX * scale - margin_bottom,
        ),
        radius=radius,
        fill=(255, 255, 255, 125),
        outline=(0, 0, 0, 45),
        width=outline_width,
    )


def _draw_ornamental_separator(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    y: int,
    width: int,
    scale: int,
) -> None:
    """Draw a small centered separator used in the title page."""
    line_color = (0, 0, 0, 145)
    dot_color = (0, 0, 0, 170)
    gap = int(18 * scale)
    dot_r = int(5 * scale)
    line_w = max(1, int(2 * scale))

    left_outer = center_x - width // 2
    left_inner = center_x - gap
    right_inner = center_x + gap
    right_outer = center_x + width // 2

    draw.line((left_outer, y, left_inner, y), fill=line_color, width=line_w)
    draw.line((right_inner, y, right_outer, y), fill=line_color, width=line_w)
    draw.ellipse((center_x - dot_r, y - dot_r, center_x + dot_r, y + dot_r), fill=dot_color)


def render_title_page(
    book_title: str,
    *,
    subtitle: str = "A themed collection of word search puzzles",
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
) -> str:
    """
    Renderiza una portada interior para el libro.

    Devuelve la ruta del PNG generado.
    """
    scale = 3
    width_hi = PAGE_W_PX * scale
    height_hi = PAGE_H_PX * scale

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((width_hi, height_hi), Image.LANCZOS)
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            a = a.point(lambda value: int(value * 0.72))
            img = Image.merge("RGBA", (r, g, b, a))
    else:
        img = Image.new("RGBA", (width_hi, height_hi), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    _draw_soft_panel(draw, scale)

    center_x = width_hi // 2
    max_width = int(width_hi * 0.70)

    # Título principal: se reduce si el título es largo.
    title_size = int(TITLE_FONT_SIZE * 1.70) * scale
    min_title_size = int(TITLE_FONT_SIZE * 0.98) * scale
    title = book_title.strip() or "Word Search Book"

    while title_size > min_title_size:
        title_font = load_font(FONT_TITLE, title_size)
        title_lines = wrap_text(draw, title, title_font, max_width)
        widest = max((text_size(draw, line, title_font)[0] for line in title_lines), default=0)
        if widest <= max_width and len(title_lines) <= 4:
            break
        title_size = int(title_size * 0.90)

    title_font = load_font(FONT_TITLE, title_size)
    title_lines = wrap_text(draw, title, title_font, max_width)

    subtitle_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 1.03) * scale)

    title_block_height = sum(text_size(draw, line, title_font)[1] for line in title_lines)
    title_block_height += int(title_size * 0.12) * max(0, len(title_lines) - 1)

    title_start_y = int(height_hi * 0.265) - title_block_height // 2
    shadow = (0, 0, 0, 60)
    black = (0, 0, 0, 255)

    y = draw_centered_lines(
        draw,
        title_lines,
        title_font,
        center_x,
        title_start_y,
        black,
        line_spacing=1.07,
        shadow_fill=shadow,
        shadow_offset=int(2 * scale),
    )

    sep_y = y + int(120 * scale)
    sep_w = int(width_hi * 0.38)
    _draw_ornamental_separator(draw, center_x, sep_y, sep_w, scale)

    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_width)
    subtitle_y = sep_y + int(95 * scale)
    draw_centered_lines(
        draw,
        subtitle_lines,
        subtitle_font,
        center_x,
        subtitle_y,
        (0, 0, 0, 225),
        line_spacing=1.18,
    )

    if filename is None:
        filename = os.path.join("output_puzzles_kdp", "00_title_page.png")

    return save_page(img, filename)
