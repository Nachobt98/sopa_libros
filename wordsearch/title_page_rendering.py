"""
Renderizado de la portada interior del libro temático.

Esta página no es la cubierta de KDP, sino una title page interior que aparece
antes del índice para dar al PDF una estructura más editorial.
"""

from __future__ import annotations

import os
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from wordsearch.constants_and_layout import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    PAGE_H_PX,
    PAGE_W_PX,
    wordlist_font_size as WORDLIST_FONT_SIZE,
    title_font_size as TITLE_FONT_SIZE,
)
from wordsearch.image_rendering import BACKGROUND_PATH


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _text_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> Tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current: List[str] = []

    for word in words:
        candidate = " ".join(current + [word]).strip()
        width, _ = _text_size(draw, candidate, font)
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def _draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    center_x: int,
    start_y: int,
    fill,
    *,
    line_spacing: float = 1.12,
    shadow_fill=None,
    shadow_offset: int = 0,
) -> int:
    y = start_y
    for line in lines:
        width, height = _text_size(draw, line, font)
        x = center_x - width // 2

        if shadow_fill is not None and shadow_offset:
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_fill)

        draw.text((x, y), line, font=font, fill=fill)
        y += int(height * line_spacing)

    return y


def _draw_soft_panel(draw: ImageDraw.ImageDraw, scale: int) -> None:
    margin_x = int(110 * scale)
    margin_y = int(170 * scale)
    radius = int(35 * scale)
    outline_width = max(1, int(3 * scale))

    draw.rounded_rectangle(
        (margin_x, margin_y, PAGE_W_PX * scale - margin_x, PAGE_H_PX * scale - margin_y),
        radius=radius,
        fill=(255, 255, 255, 145),
        outline=(0, 0, 0, 55),
        width=outline_width,
    )


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
    max_width = int(width_hi * 0.72)

    # Título principal: se reduce si el título es largo.
    title_size = int(TITLE_FONT_SIZE * 1.85) * scale
    min_title_size = int(TITLE_FONT_SIZE * 1.05) * scale
    title = book_title.strip() or "Word Search Book"

    while title_size > min_title_size:
        title_font = _load_font(FONT_TITLE, title_size)
        title_lines = _wrap_text(draw, title, title_font, max_width)
        widest = max((_text_size(draw, line, title_font)[0] for line in title_lines), default=0)
        if widest <= max_width and len(title_lines) <= 4:
            break
        title_size = int(title_size * 0.90)

    title_font = _load_font(FONT_TITLE, title_size)
    title_lines = _wrap_text(draw, title, title_font, max_width)

    subtitle_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 1.15) * scale)
    meta_font = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.72) * scale)

    title_block_height = sum(_text_size(draw, line, title_font)[1] for line in title_lines)
    title_block_height += int(title_size * 0.10) * max(0, len(title_lines) - 1)

    title_start_y = int(height_hi * 0.29) - title_block_height // 2
    shadow = (0, 0, 0, 75)
    black = (0, 0, 0, 255)

    y = _draw_centered_lines(
        draw,
        title_lines,
        title_font,
        center_x,
        title_start_y,
        black,
        line_spacing=1.05,
        shadow_fill=shadow,
        shadow_offset=int(3 * scale),
    )

    subtitle_lines = _wrap_text(draw, subtitle, subtitle_font, max_width)
    y += int(55 * scale)
    y = _draw_centered_lines(
        draw,
        subtitle_lines,
        subtitle_font,
        center_x,
        y,
        black,
        line_spacing=1.15,
    )

    # Separador ornamental sencillo.
    sep_y = y + int(85 * scale)
    sep_w = int(width_hi * 0.34)
    sep_x1 = center_x - sep_w // 2
    sep_x2 = center_x + sep_w // 2
    draw.line((sep_x1, sep_y, sep_x2, sep_y), fill=(0, 0, 0, 150), width=max(1, int(2 * scale)))
    dot_r = int(5 * scale)
    draw.ellipse((center_x - dot_r, sep_y - dot_r, center_x + dot_r, sep_y + dot_r), fill=(0, 0, 0, 180))

    footer_text = "Word Search Puzzle Book"
    footer_w, footer_h = _text_size(draw, footer_text, meta_font)
    footer_y = int(height_hi * 0.76)
    draw.text((center_x - footer_w // 2, footer_y), footer_text, font=meta_font, fill=(0, 0, 0, 210))

    if filename is None:
        filename = os.path.join("output_puzzles_kdp", "00_title_page.png")

    img_rgb = img.convert("RGB")
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), resample=Image.LANCZOS)
    img_final.save(filename, dpi=(300, 300))
    return filename
