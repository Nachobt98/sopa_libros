"""
Renderizado de páginas preliminares del libro: índice e instrucciones.

Se mantiene separado de image_rendering.py para evitar seguir creciendo un
módulo que ya contiene el render principal de puzzles y soluciones.
"""

from __future__ import annotations

import math
import os
from typing import List, Optional, Sequence, Tuple

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


TocEntry = Tuple[str, int, bool]


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


def _rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int, int, int],
    radius: int,
    fill=None,
    outline=None,
    width: int = 1,
) -> None:
    try:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    except AttributeError:
        x1, y1, x2, y2 = xy
        draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)
        draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
        draw.pieslice((x1, y1, x1 + 2 * radius, y1 + 2 * radius), 180, 270, fill=fill)
        draw.pieslice((x2 - 2 * radius, y1, x2, y1 + 2 * radius), 270, 360, fill=fill)
        draw.pieslice((x1, y2 - 2 * radius, x1 + 2 * radius, y2), 90, 180, fill=fill)
        draw.pieslice((x2 - 2 * radius, y2 - 2 * radius, x2, y2), 0, 90, fill=fill)
        if outline:
            draw.rectangle(xy, outline=outline, width=width)


def _make_background(background_path: Optional[str], scale: int) -> Image.Image:
    width_hi = PAGE_W_PX * scale
    height_hi = PAGE_H_PX * scale
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((width_hi, height_hi), Image.LANCZOS)
        r, g, b, a = img.split()
        a = a.point(lambda value: int(value * 0.72))
        return Image.merge("RGBA", (r, g, b, a))

    return Image.new("RGBA", (width_hi, height_hi), (255, 255, 255, 255))


def _draw_main_panel(draw: ImageDraw.ImageDraw, scale: int) -> Tuple[int, int, int, int]:
    left = int(110 * scale)
    top = int(105 * scale)
    right = PAGE_W_PX * scale - int(110 * scale)
    bottom = PAGE_H_PX * scale - int(150 * scale)

    _rounded_rectangle(
        draw,
        (left, top, right, bottom),
        radius=int(26 * scale),
        fill=(255, 255, 255, 150),
        outline=(0, 0, 0, 55),
        width=max(1, int(2 * scale)),
    )
    return left, top, right, bottom


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    center_x: int,
    y: int,
    fill,
) -> int:
    width, height = _text_size(draw, text, font)
    draw.text((center_x - width // 2, y), text, font=font, fill=fill)
    return y + height


def _draw_page_number(draw: ImageDraw.ImageDraw, page_number: int, scale: int) -> None:
    font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.55) * scale)
    text = str(page_number)
    width, height = _text_size(draw, text, font)
    x = PAGE_W_PX * scale // 2 - width // 2
    y = PAGE_H_PX * scale - int(44 * scale)
    draw.text((x, y), text, font=font, fill=(0, 0, 0, 210))


def _save_page(img: Image.Image, filename: str) -> str:
    img_rgb = img.convert("RGB")
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), resample=Image.LANCZOS)
    img_final.save(filename, dpi=(300, 300))
    return filename


def render_table_of_contents(
    toc_entries: Sequence[TocEntry],
    output_dir: str,
    background_path: Optional[str] = None,
) -> List[str]:
    """
    Renderiza un índice editorial compacto.

    Mantiene la firma histórica para que main_thematic.py no tenga que conocer
    detalles de renderizado.
    """
    scale = 3
    img = _make_background(background_path, scale)
    draw = ImageDraw.Draw(img)
    panel_left, panel_top, panel_right, panel_bottom = _draw_main_panel(draw, scale)

    center_x = PAGE_W_PX * scale // 2
    title_font = _load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 1.15) * scale)
    section_font = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.72) * scale)
    entry_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.78) * scale)
    page_font = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.78) * scale)

    y = panel_top + int(64 * scale)
    y = _draw_centered_text(draw, "Table of Contents", title_font, center_x, y, (0, 0, 0, 255))

    subtitle = "Sections"
    y += int(36 * scale)
    y = _draw_centered_text(draw, subtitle.upper(), section_font, center_x, y, (0, 0, 0, 180))

    line_y = y + int(28 * scale)
    line_width = int((panel_right - panel_left) * 0.42)
    draw.line(
        (center_x - line_width // 2, line_y, center_x + line_width // 2, line_y),
        fill=(0, 0, 0, 95),
        width=max(1, int(1.5 * scale)),
    )

    y = line_y + int(58 * scale)
    content_left = panel_left + int(64 * scale)
    content_right = panel_right - int(64 * scale)
    row_gap = int(42 * scale)

    for idx, (label, page_number, _is_section) in enumerate(toc_entries):
        if idx == len(toc_entries) - 1 and label.lower() == "solutions":
            y += int(24 * scale)
            draw.line(
                (content_left, y, content_right, y),
                fill=(0, 0, 0, 65),
                width=max(1, int(1 * scale)),
            )
            y += int(34 * scale)

        label_width, label_height = _text_size(draw, label, entry_font)
        page_text = str(page_number)
        page_width, page_height = _text_size(draw, page_text, page_font)

        page_x = content_right - page_width
        label_x = content_left
        baseline_y = y

        draw.text((label_x, baseline_y), label, font=entry_font, fill=(0, 0, 0, 235))
        draw.text((page_x, baseline_y), page_text, font=page_font, fill=(0, 0, 0, 235))

        dot_start = label_x + label_width + int(16 * scale)
        dot_end = page_x - int(16 * scale)
        dot_y = baseline_y + label_height // 2 + int(2 * scale)
        if dot_end > dot_start:
            dash_w = int(10 * scale)
            gap_w = int(8 * scale)
            x = dot_start
            while x < dot_end:
                draw.line(
                    (x, dot_y, min(x + dash_w, dot_end), dot_y),
                    fill=(0, 0, 0, 75),
                    width=max(1, int(1 * scale)),
                )
                x += dash_w + gap_w

        y += max(label_height, page_height) + row_gap

    filename = os.path.join(output_dir, "01_table_of_contents.png")
    _draw_page_number(draw, 2, scale)
    return [_save_page(img, filename)]


def render_instructions_page(
    book_title: str,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
) -> str:
    """
    Renderiza una página de instrucciones más limpia y genérica.
    """
    scale = 3
    img = _make_background(background_path, scale)
    draw = ImageDraw.Draw(img)
    panel_left, panel_top, panel_right, panel_bottom = _draw_main_panel(draw, scale)

    center_x = PAGE_W_PX * scale // 2
    title_font = _load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 1.05) * scale)
    subtitle_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.9) * scale)
    number_font = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.82) * scale)
    body_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.70) * scale)

    y = panel_top + int(60 * scale)
    y = _draw_centered_text(draw, "Instructions", title_font, center_x, y, (0, 0, 0, 255))
    y += int(16 * scale)
    y = _draw_centered_text(draw, "How to enjoy this book", subtitle_font, center_x, y, (0, 0, 0, 220))

    y += int(70 * scale)

    instructions = [
        "Find each word from the list at the bottom of the puzzle page.",
        "Words may appear horizontally, vertically or diagonally.",
        "Depending on the difficulty, some words may also appear backwards.",
        "Circle or highlight each word as you find it in the grid.",
        "Use the fun facts to learn something new as you play.",
        "Check the solutions section at the back of the book if you get stuck.",
    ]

    content_left = panel_left + int(72 * scale)
    content_right = panel_right - int(72 * scale)
    text_left = content_left + int(58 * scale)
    max_text_width = content_right - text_left
    row_gap = int(34 * scale)

    for idx, instruction in enumerate(instructions, start=1):
        number_text = str(idx)
        circle_r = int(19 * scale)
        circle_cx = content_left + circle_r
        circle_cy = y + circle_r

        draw.ellipse(
            (
                circle_cx - circle_r,
                circle_cy - circle_r,
                circle_cx + circle_r,
                circle_cy + circle_r,
            ),
            fill=(0, 0, 0, 235),
        )

        num_w, num_h = _text_size(draw, number_text, number_font)
        draw.text(
            (circle_cx - num_w // 2, circle_cy - num_h // 2 - int(1 * scale)),
            number_text,
            font=number_font,
            fill=(255, 255, 255, 255),
        )

        lines = _wrap_text(draw, instruction, body_font, max_text_width)
        text_y = y - int(2 * scale)
        line_h = int(body_font.size * 1.18)
        for line in lines:
            draw.text((text_left, text_y), line, font=body_font, fill=(0, 0, 0, 235))
            text_y += line_h

        y = max(circle_cy + circle_r, text_y) + row_gap

    if filename is None:
        filename = os.path.join("output_puzzles_kdp", "02_instructions.png")

    _draw_page_number(draw, 3, scale)
    return _save_page(img, filename)
