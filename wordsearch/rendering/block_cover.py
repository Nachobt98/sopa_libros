"""Block cover page renderer."""

from __future__ import annotations

import os
from typing import Optional

from PIL import Image, ImageDraw

from wordsearch.constants_and_layout import (
    FONT_PATH,
    FONT_TITLE,
    PAGE_H_PX,
    PAGE_W_PX,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.image_rendering import BACKGROUND_PATH
from wordsearch.rendering.common import load_font, save_page, text_size, wrap_text


def render_block_cover(
    block_name: str,
    block_index: int,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
) -> str:
    """
    Genera una página de portada para un bloque temático.

    Fondo completo + título centrado + subtítulo de una línea. Sin panel blanco.
    """
    scale = 3
    page_w_hi = PAGE_W_PX * scale
    page_h_hi = PAGE_H_PX * scale

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((page_w_hi, page_h_hi), Image.LANCZOS)

        if img.mode == "RGBA":
            r, g, b, a = img.split()
            a = a.point(lambda value: int(value * 0.70))
            img = Image.merge("RGBA", (r, g, b, a))
    else:
        img = Image.new("RGBA", (page_w_hi, page_h_hi), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    margin_x = int(page_w_hi * 0.10)
    max_text_width = page_w_hi - 2 * margin_x

    center_x = page_w_hi // 2
    title_y = int(page_h_hi * 0.33)
    subtitle_gap = int(40 * scale)

    small = img.resize((50, 50)).convert("L")
    avg_brightness = sum(small.getdata()) / (50 * 50)
    main_color = (255, 255, 255, 255) if avg_brightness < 128 else (0, 0, 0, 255)
    shadow_color = (0, 0, 0, 90) if main_color[0] == 255 else (255, 255, 255, 90)

    raw_title = block_name.strip() or f"Block {block_index}"

    base_size = int(TITLE_FONT_SIZE * 1.6) * scale
    min_size = int(TITLE_FONT_SIZE * 1.0) * scale

    font_size = base_size
    while font_size > min_size:
        font_title = load_font(FONT_TITLE, font_size)
        title_lines = wrap_text(draw, raw_title, font_title, max_text_width)
        widest = max((text_size(draw, line, font_title)[0] for line in title_lines), default=0)
        if widest <= max_text_width:
            break
        font_size = int(font_size * 0.9)

    font_title = load_font(FONT_TITLE, font_size)
    title_lines = wrap_text(draw, raw_title, font_title, max_text_width)
    line_height = int(font_size * 1.1)
    total_title_h = len(title_lines) * line_height

    first_line_y = title_y - total_title_h // 2
    shadow_offset = int(4 * scale)

    y = first_line_y
    for line in title_lines:
        width, height = text_size(draw, line, font_title)
        try:
            draw.text(
                (center_x + shadow_offset, y + height / 2 + shadow_offset),
                line,
                font=font_title,
                fill=shadow_color,
                anchor="mm",
            )
            draw.text(
                (center_x, y + height / 2),
                line,
                font=font_title,
                fill=main_color,
                anchor="mm",
            )
        except TypeError:
            x = center_x - width / 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                line,
                font=font_title,
                fill=shadow_color,
            )
            draw.text((x, y), line, font=font_title, fill=main_color)
        y += line_height

    subtitle = "A themed collection of word search puzzles"
    font_sub_size = int(WORDLIST_FONT_SIZE * 1.3) * scale
    font_sub = load_font(FONT_PATH, font_sub_size)

    sub_w, sub_h = text_size(draw, subtitle, font_sub)
    while sub_w > max_text_width and font_sub_size > int(WORDLIST_FONT_SIZE * 0.9) * scale:
        font_sub_size = int(font_sub_size * 0.9)
        font_sub = load_font(FONT_PATH, font_sub_size)
        sub_w, sub_h = text_size(draw, subtitle, font_sub)

    subtitle_y = y + subtitle_gap

    try:
        draw.text(
            (center_x + shadow_offset, subtitle_y + sub_h / 2 + shadow_offset),
            subtitle,
            font=font_sub,
            fill=shadow_color,
            anchor="mm",
        )
        draw.text(
            (center_x, subtitle_y + sub_h / 2),
            subtitle,
            font=font_sub,
            fill=main_color,
            anchor="mm",
        )
    except TypeError:
        sx = center_x - sub_w / 2
        sy = subtitle_y
        draw.text(
            (sx + shadow_offset, sy + shadow_offset),
            subtitle,
            font=font_sub,
            fill=shadow_color,
        )
        draw.text((sx, sy), subtitle, font=font_sub, fill=main_color)

    if filename is None:
        filename = os.path.join("output_puzzles_kdp", f"block_{block_index}.png")

    return save_page(img, filename)
