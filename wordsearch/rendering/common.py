"""Common rendering helpers shared by page renderers."""

from __future__ import annotations

from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

from wordsearch.config.layout import DPI, PAGE_H_PX, PAGE_W_PX


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType font, falling back to Pillow's default font."""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> Tuple[int, int]:
    """Return text width and height using Pillow's textbbox API."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> List[str]:
    """Wrap text into lines that fit within max_width."""
    words = text.split()
    lines: List[str] = []
    current: List[str] = []

    for word in words:
        candidate = " ".join(current + [word]).strip()
        width, _ = text_size(draw, candidate, font)
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int, int, int],
    radius: int,
    fill=None,
    outline=None,
    width: int = 1,
) -> None:
    """Draw a rounded rectangle with fallback for older Pillow versions."""
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


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    center_x: int,
    y: int,
    fill,
) -> int:
    """Draw text centered on center_x and return the next y position."""
    width, height = text_size(draw, text, font)
    draw.text((center_x - width // 2, y), text, font=font, fill=fill)
    return y + height


def draw_centered_lines(
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
    """Draw multiple centered lines and return the next y position."""
    y = start_y
    for line in lines:
        width, height = text_size(draw, line, font)
        x = center_x - width // 2

        if shadow_fill is not None and shadow_offset:
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_fill)

        draw.text((x, y), line, font=font, fill=fill)
        y += int(height * line_spacing)

    return y


def save_page(
    img: Image.Image,
    filename: str,
    *,
    output_width_px: int = PAGE_W_PX,
    output_height_px: int = PAGE_H_PX,
    dpi: int = DPI,
) -> str:
    """Save a high-resolution RGBA/RGB page image at the selected KDP size."""
    img_rgb = img.convert("RGB")
    img_final = img_rgb.resize((output_width_px, output_height_px), resample=Image.LANCZOS)
    img_final.save(filename, dpi=(dpi, dpi))
    return filename
