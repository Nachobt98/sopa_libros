"""
Renderizado avanzado de la sopa de letras y soluciones como imágenes (Pillow).
Incluye: título (con wrap), caja FUN FACT, grid centrado, pastilla "Solution on page X"
y lista de palabras en columnas, manteniendo el resaltado elegante para soluciones.
"""

import os
import math
from typing import Iterable, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont
from wordsearch.constants_and_layout import (
    FONT_TITLE,
    PAGE_W_PX,
    PAGE_H_PX,
    SAFE_LEFT,
    SAFE_RIGHT,
    SAFE_BOTTOM,
    TOP_PX,
    BOTTOM_PX,
    FONT_PATH,
    FONT_PATH_BOLD,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)

BACKGROUND_PATH = "assets/afro_recargado_background.png"


# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

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


def _rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int, int, int],
    radius: int,
    fill=None,
    outline=None,
    width: int = 1,
) -> None:
    """
    Wrapper limpio que usa rounded_rectangle de Pillow si existe,
    y solo si no existe usa un fallback sencillo.
    """
    try:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    except AttributeError:
        x1, y1, x2, y2 = xy
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill, outline=None)
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill, outline=None)
        # Esquinas
        draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill, outline=None)
        draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill, outline=None)
        draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill, outline=None)
        draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill, outline=None)

        if outline is not None and width > 0:
            draw.rounded_rectangle(xy, radius=radius, outline=outline, fill=None, width=width)


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current: List[str] = []

    for w in words:
        test = (" ".join(current + [w])).strip()
        w_width, _ = _text_size(draw, test, font)
        if w_width <= max_width or not current:
            current.append(w)
        else:
            lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def _draw_wrapped_centered_title(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    start_y: int,
    area_left: int,
    area_right: int,
    line_spacing: float = 1.05,
) -> int:
    """
    Dibuja el título centrado con word-wrap si es muy largo.
    Devuelve la coordenada y justo debajo del bloque de título.
    """
    lines = _wrap_text(draw, text, font, max_width)
    y = start_y
    container_width = max(0, area_right - area_left)
    for line in lines:
        w, h = _text_size(draw, line, font)
        x = area_left + max(0, (container_width - w) // 2)
        draw.text((x, y), line, font=font, fill=(0, 0, 0, 255))
        y += int(h * line_spacing)
    return y


# ------------------------------------------------------------
# Render principal
# ------------------------------------------------------------

def render_page(
    grid: Sequence[Sequence[str]],
    words: Iterable[str],
    idx: int,
    is_solution: bool = False,
    solution_positions=None,  # compatibilidad con código viejo
    background_path: Optional[str] = None,
    filename: Optional[str] = None,
    placed_words: Optional[Sequence[Tuple[str, Tuple[int, int, int, int]]]] = None,
    puzzle_title: Optional[str] = None,
    fun_fact: Optional[str] = None,
    solution_page_number: Optional[int] = None,
) -> str:
    """
    Renderiza una página de puzzle o solución.
    """

    SCALE = 3
    PAGE_W_HI = PAGE_W_PX * SCALE
    PAGE_H_HI = PAGE_H_PX * SCALE

    SAFE_LEFT_HI = SAFE_LEFT * SCALE
    SAFE_RIGHT_HI = SAFE_RIGHT * SCALE
    SAFE_BOTTOM_HI = SAFE_BOTTOM * SCALE
    TOP_PX_HI = TOP_PX * SCALE

    # --- Fondo de página (PNG opcional) ---
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((PAGE_W_HI, PAGE_H_HI), Image.LANCZOS)

        if bg.mode == "RGBA":
            r, g, b, a = bg.split()
            a = a.point(lambda v: int(v * 0.7))  # 70% opacidad
            bg = Image.merge("RGBA", (r, g, b, a))

        img = bg
    else:
        img = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    # === PANEL BLANCO PRINCIPAL PARA TODO EL CONTENIDO ===
    panel_pad_x = int(30 * SCALE)
    panel_pad_top = int(40 * SCALE)
    panel_pad_bottom = int(40 * SCALE)

    panel_left = SAFE_LEFT_HI - panel_pad_x
    panel_right = SAFE_RIGHT_HI + panel_pad_x
    panel_top = TOP_PX_HI - panel_pad_top
    panel_bottom = SAFE_BOTTOM_HI + panel_pad_bottom

    # Altura máxima permitida para título + FUN FACT
    TITLE_FACT_AREA_HI = int(500 * SCALE)
    GRID_TOP_BASE = panel_top + TITLE_FACT_AREA_HI

    panel_left = max(0, panel_left)
    panel_top = max(0, panel_top)
    panel_right = min(PAGE_W_HI, panel_right)
    panel_bottom = min(PAGE_H_HI, panel_bottom)

    _rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(35 * SCALE),
        fill=(255, 255, 255, 100),
        outline=(0, 0, 0, 60),
        width=max(1, int(3 * SCALE)),
    )

    # Área común de contenido dentro del panel
    content_margin_x = int(40 * SCALE)
    CONTENT_LEFT_HI = panel_left + content_margin_x
    CONTENT_RIGHT_HI = panel_right - content_margin_x
    min_gap_hi = int(30 * SCALE)

    # Fuentes
    font_title = _load_font(FONT_TITLE, TITLE_FONT_SIZE * SCALE)
    font_words = _load_font(FONT_PATH, WORDLIST_FONT_SIZE * SCALE)
    font_words_bold = _load_font(FONT_PATH_BOLD, WORDLIST_FONT_SIZE * SCALE)

    text_color = (0, 0, 0, 255)

    # FUN FACT
    fact_bg = (245, 245, 245, 245)
    fact_border = (170, 170, 170, 255)
    fact_header_bg = (30, 30, 30, 255)
    fact_header_text = (255, 255, 255, 255)

    pill_bg = (230, 230, 230, 255)
    pill_border = (120, 120, 120, 255)

    # Resaltado soluciones
    highlight_fill = (243, 226, 200, 230)   # beige
    highlight_border = (0, 0, 0, 255)       # borde oscuro

    # --------------------------------------------------------
    # TÍTULO (con wrap)
    # --------------------------------------------------------
    if puzzle_title:
        if is_solution:
            title_text = f"Solution – {idx}. {puzzle_title}"
        else:
            title_text = f"{idx}. {puzzle_title}"
    else:
        title_text = f"Solution {idx}" if is_solution else f"Puzzle {idx}"

    title_max_width = int(CONTENT_RIGHT_HI - CONTENT_LEFT_HI)
    y_after_title = _draw_wrapped_centered_title(
        draw,
        title_text,
        font_title,
        max_width=title_max_width,
        start_y=panel_top + int(25 * SCALE),
        area_left=CONTENT_LEFT_HI,
        area_right=CONTENT_RIGHT_HI,
        line_spacing=1.05,
    )

    # Más separación título → fact
    y_cursor_hi = y_after_title + int(80 * SCALE)

    # --------------------------------------------------------
    # FUN FACT – tarjeta con cabecera
    # --------------------------------------------------------
    if (not is_solution) and fun_fact:
        fact_label_font = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.9) * SCALE)
        fact_text_font_size_hi = int(WORDLIST_FONT_SIZE * 0.5) * SCALE

        left_hi = CONTENT_LEFT_HI
        right_hi = CONTENT_RIGHT_HI

        inner_horizontal_pad = int(18 * SCALE)
        max_text_width_hi = int((right_hi - left_hi) - 2 * inner_horizontal_pad)

        fact_label = "FUN FACT"
        label_w, label_h = _text_size(draw, fact_label, fact_label_font)

        header_pad_v_hi = int(8 * SCALE)
        text_pad_v_hi = int(10 * SCALE)
        header_height_hi = label_h + 2 * header_pad_v_hi

        fact_text_font = _load_font(FONT_PATH, fact_text_font_size_hi)
        line_height_hi = int(fact_text_font.size * 1.10)

        min_fact_block_hi = header_height_hi + 2 * text_pad_v_hi + line_height_hi
        max_fact_height_hi = max(min_fact_block_hi, GRID_TOP_BASE - y_cursor_hi - min_gap_hi)

        fact_lines = _wrap_text(draw, fun_fact, fact_text_font, max_text_width_hi)

        available_text_h = max(0, max_fact_height_hi - header_height_hi - 2 * text_pad_v_hi)
        max_lines_fit = max(1, available_text_h // line_height_hi)
        if len(fact_lines) > max_lines_fit:
            fact_lines = fact_lines[:max_lines_fit]
            last_line = fact_lines[-1] if fact_lines else ""
            ellipsis = "..."
            while last_line and _text_size(draw, last_line + ellipsis, fact_text_font)[0] > max_text_width_hi:
                last_line = last_line[:-1].rstrip()
            if last_line:
                fact_lines[-1] = last_line + ellipsis
            else:
                fact_lines[-1] = ellipsis

        fact_text_height_hi = len(fact_lines) * line_height_hi
        box_height_hi = header_height_hi + text_pad_v_hi + fact_text_height_hi + text_pad_v_hi

        box_top_hi = y_cursor_hi
        box_bottom_hi = box_top_hi + box_height_hi

        card_radius = int(18 * SCALE)
        _rounded_rectangle(
            draw,
            (int(left_hi), int(box_top_hi), int(right_hi), int(box_bottom_hi)),
            radius=card_radius,
            fill=fact_bg,
            outline=fact_border,
            width=max(1, int(2 * SCALE)),
        )

        header_left_hi = left_hi
        header_right_hi = right_hi
        header_top_hi = box_top_hi
        header_bottom_hi = header_top_hi + header_height_hi

        header_radius = min(card_radius, header_height_hi // 2)
        _rounded_rectangle(
            draw,
            (int(header_left_hi), int(header_top_hi), int(header_right_hi), int(header_bottom_hi)),
            radius=header_radius,
            fill=fact_header_bg,
            outline=None,
            width=0,
        )
        draw.rectangle(
            (
                int(header_left_hi),
                int(header_top_hi + header_radius),
                int(header_right_hi),
                int(header_bottom_hi),
            ),
            fill=fact_header_bg,
            outline=None,
        )

        header_cx = (header_left_hi + header_right_hi) / 2
        header_cy = (header_top_hi + header_bottom_hi) / 2
        try:
            draw.text(
                (header_cx, header_cy),
                fact_label,
                font=fact_label_font,
                fill=fact_header_text,
                anchor="mm",
            )
        except TypeError:
            hx = header_cx - label_w / 2
            hy = header_cy - label_h / 2
            draw.text((hx, hy), fact_label, font=fact_label_font, fill=fact_header_text)

        text_x_hi = left_hi + inner_horizontal_pad
        text_y_hi = header_bottom_hi + text_pad_v_hi

        for line in fact_lines:
            draw.text((text_x_hi, text_y_hi), line, font=fact_text_font, fill=text_color)
            text_y_hi += line_height_hi

        y_cursor_hi = box_bottom_hi + int(50 * SCALE)

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    content_width_hi = CONTENT_RIGHT_HI - CONTENT_LEFT_HI
    grid_width_target_hi = int(content_width_hi * 0.85)
    cell_size_hi = int(grid_width_target_hi / max(cols, 1))

    grid_w_hi = cell_size_hi * cols
    grid_h_hi = cell_size_hi * rows

    grid_top_hi = GRID_TOP_BASE
    grid_left_hi = int((CONTENT_LEFT_HI + CONTENT_RIGHT_HI - grid_w_hi) // 2)

    letter_font_size_hi = max(int(cell_size_hi * 0.9), int(18 * SCALE))
    font_letter = _load_font(FONT_PATH, letter_font_size_hi)
    font_letter_bold = _load_font(FONT_PATH_BOLD, letter_font_size_hi)

    grid_line_width_hi = max(1, int(1.2 * SCALE))
    grid_line_color = "#444444"

    # --------------------------------------------------------
    # CAPA DE RESALTADO (solo soluciones, con cápsula)
    # --------------------------------------------------------
    highlight_positions = set()

    overlay_fill = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (0, 0, 0, 0))
    overlay_border = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (0, 0, 0, 0))
    odraw_fill = ImageDraw.Draw(overlay_fill)

    if is_solution and placed_words:
        for w, (r, c, dr, dc) in placed_words:
            wlen = len(w)
            if wlen < 2:
                continue

            centers: List[Tuple[float, float]] = []
            for i in range(wlen):
                rr = r + dr * i
                cc = c + dc * i
                if rr < 0 or rr >= rows or cc < 0 or cc >= cols:
                    break

                x0 = grid_left_hi + cc * cell_size_hi
                y0 = grid_top_hi + rr * cell_size_hi
                cx = x0 + cell_size_hi / 2
                cy = y0 + cell_size_hi / 2
                centers.append((cx, cy))
                highlight_positions.add((rr, cc))

            if len(centers) < 2:
                continue

            p0 = centers[0]
            p1 = centers[-1]

            thickness = cell_size_hi * 0.8
            radius = thickness / 2

            # 1) Relleno beige
            odraw_fill.line(
                centers,
                fill=highlight_fill,
                width=int(thickness),
                joint="curve",
            )
            for (cx, cy) in (p0, p1):
                odraw_fill.ellipse(
                    (cx - radius, cy - radius, cx + radius, cy + radius),
                    fill=highlight_fill,
                )

            # 2) Borde tipo anillo en capa temporal
            tmp_border = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (0, 0, 0, 0))
            bdraw = ImageDraw.Draw(tmp_border)

            outer_width = int(thickness + 8 * SCALE)
            inner_width = int(thickness)
            outer_radius = radius + 4 * SCALE
            inner_radius = radius

            # Exterior
            bdraw.line(
                centers,
                fill=highlight_border,
                width=outer_width,
                joint="curve",
            )
            for (cx, cy) in (p0, p1):
                bdraw.ellipse(
                    (
                        cx - outer_radius,
                        cy - outer_radius,
                        cx + outer_radius,
                        cy + outer_radius,
                    ),
                    fill=highlight_border,
                )

            # Vaciar interior con transparente
            transparent = (0, 0, 0, 0)
            bdraw.line(
                centers,
                fill=transparent,
                width=inner_width,
                joint="curve",
            )
            for (cx, cy) in (p0, p1):
                bdraw.ellipse(
                    (
                        cx - inner_radius,
                        cy - inner_radius,
                        cx + inner_radius,
                        cy + inner_radius,
                    ),
                    fill=transparent,
                )

            overlay_border.alpha_composite(tmp_border)

    # --------------------------------------------------------
    # GRID (líneas + letras normales)
    # --------------------------------------------------------
    for r in range(rows + 1):
        y = grid_top_hi + r * cell_size_hi
        draw.line(
            (grid_left_hi, y, grid_left_hi + grid_w_hi, y),
            fill=grid_line_color,
            width=grid_line_width_hi,
        )
    for c in range(cols + 1):
        x = grid_left_hi + c * cell_size_hi
        draw.line(
            (x, grid_top_hi, x, grid_top_hi + grid_h_hi),
            fill=grid_line_color,
            width=grid_line_width_hi,
        )

    for r in range(rows):
        for c in range(cols):
            x0 = grid_left_hi + c * cell_size_hi
            y0 = grid_top_hi + r * cell_size_hi
            cx = x0 + cell_size_hi / 2
            cy = y0 + cell_size_hi / 2
            letter = grid[r][c]

            try:
                draw.text(
                    (cx, cy),
                    letter,
                    fill="black",
                    font=font_letter,
                    anchor="mm",
                )
            except TypeError:
                lw, lh = _text_size(draw, letter, font_letter)
                draw.text(
                    (cx - lw / 2, cy - lh / 2),
                    letter,
                    fill="black",
                    font=font_letter,
                )

    # --------------------------------------------------------
    # Mezclar resaltado sobre el grid
    # --------------------------------------------------------
    overlay = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (0, 0, 0, 0))
    # Primero el relleno, luego el borde tipo “donut”
    overlay.alpha_composite(overlay_fill)
    overlay.alpha_composite(overlay_border)
    img.alpha_composite(overlay)

    # Redibujar letras de las posiciones resaltadas en negrita
    if is_solution and highlight_positions:
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in highlight_positions:
                    continue
                x0 = grid_left_hi + c * cell_size_hi
                y0 = grid_top_hi + r * cell_size_hi
                cx = x0 + cell_size_hi / 2
                cy = y0 + cell_size_hi / 2
                letter = grid[r][c]
                try:
                    draw.text(
                        (cx, cy),
                        letter,
                        fill="black",
                        font=font_letter_bold,
                        anchor="mm",
                    )
                except TypeError:
                    lw, lh = _text_size(draw, letter, font_letter_bold)
                    draw.text(
                        (cx - lw / 2, cy - lh / 2),
                        letter,
                        fill="black",
                        font=font_letter_bold,
                    )

    grid_bottom_hi = grid_top_hi + grid_h_hi

    # --------------------------------------------------------
    # ÁREA INFERIOR (pill + lista)
    # --------------------------------------------------------
    base_gap_hi = int(60 * SCALE)
    gap_pill_to_words_hi = int(70 * SCALE)
    words_area_height_hi = int(850 * SCALE)
    words_bottom_hi = SAFE_BOTTOM_HI - int(8 * SCALE)
    words_top_hi = max(0, words_bottom_hi - words_area_height_hi)

    # PASTILLA "Solution on page X"
    pill_box_h = 0
    pill_y = grid_bottom_hi + base_gap_hi
    if (not is_solution) and solution_page_number is not None:
        pill_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75) * SCALE)
        pill_text = f"Solution on page {solution_page_number}"
        tw_pill, th_pill = _text_size(draw, pill_text, pill_font)

        pad_h = int(16 * SCALE)
        pad_w = int(16 * SCALE)
        box_w = tw_pill + 2 * pad_w
        box_h = th_pill + 2 * pad_h
        pill_box_h = box_h

        pill_x = int((CONTENT_LEFT_HI + CONTENT_RIGHT_HI - box_w) // 2)
        target_pill_y = words_top_hi - gap_pill_to_words_hi - box_h
        min_pill_y = grid_bottom_hi + base_gap_hi
        pill_y = max(min_pill_y, target_pill_y)

        _rounded_rectangle(
            draw,
            (pill_x, pill_y, pill_x + box_w, pill_y + box_h),
            radius=box_h // 2,
            fill=pill_bg,
            outline=pill_border,
            width=max(1, int(2 * SCALE)),
        )

        tx = pill_x + box_w / 2
        ty = pill_y + box_h / 2
        try:
            draw.text((tx, ty), pill_text, font=pill_font, fill=text_color, anchor="mm")
        except TypeError:
            draw.text((tx - tw_pill / 2, ty - th_pill / 2), pill_text, font=pill_font, fill=text_color)

    desired_words_top_hi = pill_y + pill_box_h + gap_pill_to_words_hi
    if desired_words_top_hi > words_top_hi:
        words_top_hi = desired_words_top_hi
    if words_top_hi > words_bottom_hi:
        words_top_hi = words_bottom_hi
    words_height_hi = max(0, words_bottom_hi - words_top_hi)

    # LISTA DE PALABRAS
    words_upper = [str(w).upper() for w in words]
    if words_upper and words_height_hi > 0:
        words_inner_margin_hi = int(35 * SCALE)
        area_left_hi = CONTENT_LEFT_HI + words_inner_margin_hi
        area_right_hi = CONTENT_RIGHT_HI - words_inner_margin_hi
        total_w_hi = area_right_hi - area_left_hi

        font_words_real = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.6) * SCALE)
        line_h_hi = int(font_words_real.size * 1.12)

        max_lines_per_col = max(1, words_height_hi // line_h_hi)
        word_max_w = max(_text_size(draw, w, font_words_real)[0] for w in words_upper)

        best_layout = None
        for col_count in range(2, 6):
            if col_count * max_lines_per_col < len(words_upper):
                continue
            col_w_hi = total_w_hi / col_count
            if word_max_w <= col_w_hi * 0.92:
                best_layout = (col_count, col_w_hi)
                break

        if best_layout is None:
            col_count = max(2, min(5, math.ceil(len(words_upper) / max_lines_per_col)))
            col_w_hi = total_w_hi / col_count
            best_layout = (col_count, col_w_hi)

        col_count, col_w_hi = best_layout

        base_len = len(words_upper) // col_count
        remainder = len(words_upper) % col_count
        col_sizes = [base_len + (1 if i < remainder else 0) for i in range(col_count)]

        col_words: List[List[str]] = []
        idx_tmp = 0
        for size in col_sizes:
            col_words.append(words_upper[idx_tmp : idx_tmp + size])
            idx_tmp += size

        max_used_h = max(len(cw) * line_h_hi for cw in col_words) if col_words else 0
        group_y_start = words_top_hi + (words_height_hi - max_used_h) // 2

        for ci, cw in enumerate(col_words):
            if not cw:
                continue

            col_center_x = int(area_left_hi + (ci + 0.5) * col_w_hi)
            y_hi = int(group_y_start)

            for w_txt in cw:
                try:
                    draw.text(
                        (col_center_x, y_hi),
                        w_txt,
                        fill=text_color,
                        font=font_words_real,
                        anchor="mm",
                    )
                except TypeError:
                    ww, hh = _text_size(draw, w_txt, font_words_real)
                    draw.text(
                        (col_center_x - ww / 2, y_hi - hh / 2),
                        w_txt,
                        fill=text_color,
                        font=font_words_real,
                    )
                y_hi += line_h_hi

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------
    if filename is None:
        filename = os.path.join(
            "output_puzzles_kdp",
            f"puzzle_{idx}{'_sol' if is_solution else ''}.png",
        )

    img_rgb = img.convert("RGB")
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), resample=Image.LANCZOS)
    img_final.save(filename, dpi=(300, 300))
    return filename


# ------------------------------------------------------------
# Portada de bloque
# ------------------------------------------------------------

def render_block_cover(
    block_name: str,
    block_index: int,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
) -> str:
    """
    Genera una página de portada para un bloque temático.
    Fondo completo + título centrado + subtítulo de una línea.
    Sin panel blanco.
    """

    SCALE = 3
    PAGE_W_HI = PAGE_W_PX * SCALE
    PAGE_H_HI = PAGE_H_PX * SCALE

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((PAGE_W_HI, PAGE_H_HI), Image.LANCZOS)

        if img.mode == "RGBA":
            r, g, b, a = img.split()
            a = a.point(lambda v: int(v * 0.70))
            img = Image.merge("RGBA", (r, g, b, a))
    else:
        img = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    margin_x = int(PAGE_W_HI * 0.10)
    max_text_width = PAGE_W_HI - 2 * margin_x

    center_x = PAGE_W_HI // 2
    title_y = int(PAGE_H_HI * 0.33)
    subtitle_gap = int(40 * SCALE)

    small = img.resize((50, 50)).convert("L")
    avg_brightness = sum(small.getdata()) / (50 * 50)
    main_color = (255, 255, 255, 255) if avg_brightness < 128 else (0, 0, 0, 255)
    shadow_color = (0, 0, 0, 90) if main_color[0] == 255 else (255, 255, 255, 90)

    raw_title = block_name.strip() or f"Block {block_index}"

    base_size = int(TITLE_FONT_SIZE * 1.6) * SCALE
    min_size = int(TITLE_FONT_SIZE * 1.0) * SCALE

    font_size = base_size
    while font_size > min_size:
        font_title = _load_font(FONT_TITLE, font_size)
        title_lines = _wrap_text(draw, raw_title, font_title, max_text_width)
        widest = 0
        for line in title_lines:
            w, h = _text_size(draw, line, font_title)
            widest = max(widest, w)
        if widest <= max_text_width:
            break
        font_size = int(font_size * 0.9)

    font_title = _load_font(FONT_TITLE, font_size)
    title_lines = _wrap_text(draw, raw_title, font_title, max_text_width)
    line_heig = int(font_size * 1.1)
    total_title_h = len(title_lines) * line_heig

    first_line_y = title_y - total_title_h // 2
    shadow_offset = int(4 * SCALE)

    y = first_line_y
    for line in title_lines:
        w, h = _text_size(draw, line, font_title)
        try:
            draw.text(
                (center_x + shadow_offset, y + h / 2 + shadow_offset),
                line,
                font=font_title,
                fill=shadow_color,
                anchor="mm",
            )
            draw.text(
                (center_x, y + h / 2),
                line,
                font=font_title,
                fill=main_color,
                anchor="mm",
            )
        except TypeError:
            x = center_x - w / 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                line,
                font=font_title,
                fill=shadow_color,
            )
            draw.text((x, y), line, font=font_title, fill=main_color)
        y += line_heig

    subtitle = "A themed collection of word search puzzles"
    font_sub_size = int(WORDLIST_FONT_SIZE * 1.3) * SCALE
    font_sub = _load_font(FONT_PATH, font_sub_size)

    sub_w, sub_h = _text_size(draw, subtitle, font_sub)
    while sub_w > max_text_width and font_sub_size > int(WORDLIST_FONT_SIZE * 0.9) * SCALE:
        font_sub_size = int(font_sub_size * 0.9)
        font_sub = _load_font(FONT_PATH, font_sub_size)
        sub_w, sub_h = _text_size(draw, subtitle, font_sub)

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
        safe_name = "".join(c if c.isalnum() or c in " -_." else "_" for c in block_name)
        filename = os.path.join(
            "output_puzzles_kdp",
            f"block_{block_index}_{safe_name}.png",
        )

    img_rgb = img.convert("RGB")
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), Image.LANCZOS)
    img_final.save(filename, dpi=(300, 300))
    return filename


# ------------------------------------------------------------
# Tabla de contenidos (una o varias páginas, 1 columna)
# ------------------------------------------------------------

def render_table_of_contents(
    entries: List[Tuple[str, int, bool]],
    output_dir: str,
    background_path: Optional[str] = None,
) -> List[str]:
    """
    Genera UNA o VARIAS páginas de índice (Table of Contents) en UNA sola columna.

    entries: lista de tuplas (texto, page_number, is_block_header)
             is_block_header=True -> línea de sección (bloque temático).
    Devuelve: lista de rutas a las imágenes generadas, en orden.
    """
    SCALE = 3
    PAGE_W_HI = PAGE_W_PX * SCALE
    PAGE_H_HI = PAGE_H_PX * SCALE

    SAFE_LEFT_HI = SAFE_LEFT * SCALE
    SAFE_RIGHT_HI = SAFE_RIGHT * SCALE
    SAFE_BOTTOM_HI = SAFE_BOTTOM * SCALE
    TOP_PX_HI = TOP_PX * SCALE

    panel_pad_x = int(30 * SCALE)
    panel_pad_top = int(40 * SCALE)
    panel_pad_bottom = int(40 * SCALE)

    content_margin_x = int(40 * SCALE)

    font_title_size = int(TITLE_FONT_SIZE * 1.4) * SCALE
    font_section_size = int(WORDLIST_FONT_SIZE * 0.70) * SCALE
    font_item_size = int(WORDLIST_FONT_SIZE * 0.60) * SCALE

    font_title = _load_font(FONT_TITLE, font_title_size)
    font_section = _load_font(FONT_PATH_BOLD, font_section_size)
    font_item = _load_font(FONT_PATH, font_item_size)

    text_color = (0, 0, 0, 255)

    toc_images: List[str] = []
    page_index = 1

    def _new_page() -> Tuple[Image.Image, ImageDraw.ImageDraw, int, int, int, int]:
        bg_path_local = background_path or BACKGROUND_PATH
        if bg_path_local and os.path.exists(bg_path_local):
            img_local = Image.open(bg_path_local).convert("RGBA")
            img_local = img_local.resize((PAGE_W_HI, PAGE_H_HI), Image.LANCZOS)
            if img_local.mode == "RGBA":
                r, g, b, a = img_local.split()
                a = a.point(lambda v: int(v * 0.7))
                img_local = Image.merge("RGBA", (r, g, b, a))
        else:
            img_local = Image.new("RGBA", (255, 255, 255, 255))

        draw_local = ImageDraw.Draw(img_local)

        panel_left_local = SAFE_LEFT_HI - panel_pad_x
        panel_right_local = SAFE_RIGHT_HI + panel_pad_x
        panel_top_local = TOP_PX_HI - panel_pad_top
        panel_bottom_local = SAFE_BOTTOM_HI + panel_pad_bottom

        panel_left_local = max(0, panel_left_local)
        panel_top_local = max(0, panel_top_local)
        panel_right_local = min(PAGE_W_HI, panel_right_local)
        panel_bottom_local = min(PAGE_H_HI, panel_bottom_local)

        _rounded_rectangle(
            draw_local,
            (panel_left_local, panel_top_local, panel_right_local, panel_bottom_local),
            radius=int(35 * SCALE),
            fill=(255, 255, 255, 230),
            outline=(0, 0, 0, 60),
            width=max(1, int(3 * SCALE)),
        )

        return (
            img_local,
            draw_local,
            panel_left_local,
            panel_top_local,
            panel_right_local,
            panel_bottom_local,
        )

    (
        img,
        draw,
        panel_left,
        panel_top,
        panel_right,
        panel_bottom,
    ) = _new_page()

    CONTENT_LEFT_HI = panel_left + content_margin_x
    CONTENT_RIGHT_HI = panel_right - content_margin_x

    title_text = "Table of Contents"
    y_title = panel_top + int(70 * SCALE)
    title_max_w = CONTENT_RIGHT_HI - CONTENT_LEFT_HI
    y_after_title = _draw_wrapped_centered_title(
        draw,
        title_text,
        font_title,
        max_width=title_max_w,
        start_y=y_title,
        area_left=CONTENT_LEFT_HI,
        area_right=CONTENT_RIGHT_HI,
        line_spacing=1.05,
    )

    y_start_base = y_after_title + int(120 * SCALE)
    CONTENT_BOTTOM_HI = panel_bottom - int(60 * SCALE)

    line_h_item = int(font_item.size * 1.15)
    line_h_section = int(font_section.size * 1.20)
    line_h = max(line_h_item, line_h_section)

    y_cursor = y_start_base

    x_title_left = CONTENT_LEFT_HI
    x_page_right = CONTENT_RIGHT_HI
    x_line_left = CONTENT_LEFT_HI + int(10 * SCALE)
    x_line_right = CONTENT_RIGHT_HI - int(10 * SCALE)

    for text, page, is_block in entries:
        font = font_section if is_block else font_item

        page_str = str(page)
        page_w, _ = _text_size(draw, page_str, font_item)
        max_title_w = x_page_right - x_title_left - page_w - int(30 * SCALE)

        lines = _wrap_text(draw, text, font, max_title_w)
        needed_h = len(lines) * line_h
        if y_cursor + needed_h > CONTENT_BOTTOM_HI:
            img_rgb = img.convert("RGB")
            out_name = os.path.join(
                output_dir, f"00_table_of_contents_{page_index}.png"
            )
            img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), Image.LANCZOS)
            img_final.save(out_name, dpi=(300, 300))
            toc_images.append(out_name)

            page_index += 1
            (
                img,
                draw,
                panel_left,
                panel_top,
                panel_right,
                panel_bottom,
            ) = _new_page()

            CONTENT_LEFT_HI = panel_left + content_margin_x
            CONTENT_RIGHT_HI = panel_right - content_margin_x
            x_title_left = CONTENT_LEFT_HI
            x_page_right = CONTENT_RIGHT_HI
            x_line_left = CONTENT_LEFT_HI + int(10 * SCALE)
            x_line_right = CONTENT_RIGHT_HI - int(10 * SCALE)

            y_title = panel_top + int(70 * SCALE)
            y_after_title = _draw_wrapped_centered_title(
                draw,
                title_text,
                font_title,
                max_width=CONTENT_RIGHT_HI - CONTENT_LEFT_HI,
                start_y=y_title,
                area_left=CONTENT_LEFT_HI,
                area_right=CONTENT_RIGHT_HI,
                line_spacing=1.05,
            )
            y_start_base = y_after_title + int(120 * SCALE)
            CONTENT_BOTTOM_HI = panel_bottom - int(60 * SCALE)
            y_cursor = y_start_base

        for i, line in enumerate(lines):
            lw, lh = _text_size(draw, line, font)
            y_mid = y_cursor + line_h // 2

            try:
                draw.text(
                    (x_title_left, y_mid),
                    line,
                    font=font,
                    fill=text_color,
                    anchor="lm",
                )
            except TypeError:
                draw.text((x_title_left, y_cursor), line, font=font, fill=text_color)

            if i == len(lines) - 1:
                px = x_page_right - page_w
                try:
                    draw.text(
                        (px, y_mid),
                        page_str,
                        font=font_item,
                        fill=text_color,
                        anchor="lm",
                    )
                except TypeError:
                    draw.text((px, y_cursor), page_str, font=font_item, fill=text_color)

                end_line_x = px - int(10 * SCALE)
                start_line_x = x_line_left + lw + int(10 * SCALE)
                if end_line_x > start_line_x:
                    draw.line(
                        (start_line_x, y_mid, end_line_x, y_mid),
                        fill=text_color,
                        width=max(1, int(1 * SCALE)),
                    )

            y_cursor += line_h

    img_rgb = img.convert("RGB")
    out_name = os.path.join(
        output_dir, f"00_table_of_contents_{page_index}.png"
    )
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), Image.LANCZOS)
    img_final.save(out_name, dpi=(300, 300))
    toc_images.append(out_name)

    return toc_images


# ------------------------------------------------------------
# Página de instrucciones
# ------------------------------------------------------------

def render_instructions_page(
    book_title: str,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
) -> str:
    """
    Página de instrucciones del libro.
    """
    SCALE = 3
    PAGE_W_HI = PAGE_W_PX * SCALE
    PAGE_H_HI = PAGE_H_PX * SCALE

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((PAGE_W_HI, PAGE_H_HI), Image.LANCZOS)
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            a = a.point(lambda v: int(v * 0.75))
            img = Image.merge("RGBA", (r, g, b, a))
    else:
        img = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    SAFE_LEFT_HI = SAFE_LEFT * SCALE
    SAFE_RIGHT_HI = SAFE_RIGHT * SCALE
    SAFE_BOTTOM_HI = SAFE_BOTTOM * SCALE
    TOP_PX_HI = TOP_PX * SCALE

    panel_pad_x = int(30 * SCALE)
    panel_pad_top = int(40 * SCALE)
    panel_pad_bottom = int(40 * SCALE)

    panel_left = SAFE_LEFT_HI - panel_pad_x
    panel_right = SAFE_RIGHT_HI + panel_pad_x
    panel_top = TOP_PX_HI - panel_pad_top
    panel_bottom = SAFE_BOTTOM_HI + panel_pad_bottom

    panel_left = max(0, panel_left)
    panel_top = max(0, panel_top)
    panel_right = min(PAGE_W_HI, panel_right)
    panel_bottom = min(PAGE_H_HI, panel_bottom)

    _rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(35 * SCALE),
        fill=(255, 255, 255, 235),
        outline=(0, 0, 0, 60),
        width=max(1, int(3 * SCALE)),
    )

    content_margin_x = int(40 * SCALE)
    CONTENT_LEFT_HI = panel_left + content_margin_x
    CONTENT_RIGHT_HI = panel_right - content_margin_x

    font_title = _load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 1.4) * SCALE)
    font_subtitle = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.95) * SCALE)
    font_body = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.8) * SCALE)

    text_color = (0, 0, 0, 255)

    main_title = "Instructions"
    y = panel_top + int(90 * SCALE)
    title_max_w = CONTENT_RIGHT_HI - CONTENT_LEFT_HI
    y_after_title = _draw_wrapped_centered_title(
        draw,
        main_title,
        font_title,
        max_width=title_max_w,
        start_y=y,
        area_left=CONTENT_LEFT_HI,
        area_right=CONTENT_RIGHT_HI,
        line_spacing=1.05,
    )

    subtitle = f"How to enjoy {book_title}"
    y_sub = y_after_title + int(50 * SCALE)
    _draw_wrapped_centered_title(
        draw,
        subtitle,
        font_subtitle,
        max_width=title_max_w,
        start_y=y_sub,
        area_left=CONTENT_LEFT_HI,
        area_right=CONTENT_RIGHT_HI,
        line_spacing=1.1,
    )

    bullets = [
        "Each puzzle includes a themed word list at the bottom of the page.",
        "Words may appear horizontally, vertically or diagonally in the grid.",
        "Depending on the difficulty you chose, words can also appear backwards.",
        "Circle or highlight each word as you find it in the grid.",
        "Use the fun facts to learn more about Black history, culture and achievements.",
        "You can find the completed solutions in the Solutions section at the back of the book.",
    ]

    body_top = y_sub + int(150 * SCALE)
    body_left = CONTENT_LEFT_HI + int(40 * SCALE)
    body_right = CONTENT_RIGHT_HI - int(20 * SCALE)
    max_body_width = body_right - body_left
    line_h = int(font_body.size * 1.25)
    y_cursor = body_top
    bullet_prefix = "• "

    for bullet in bullets:
        lines = _wrap_text(draw, bullet_prefix + bullet, font_body, max_body_width)
        for line in lines:
            draw.text((body_left, y_cursor), line, font=font_body, fill=text_color)
            y_cursor += line_h
        y_cursor += int(0.5 * line_h)

    if filename is None:
        filename = os.path.join("output_puzzles_kdp", "instructions.png")

    img_rgb = img.convert("RGB")
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), Image.LANCZOS)
    img_final.save(filename, dpi=(300, 300))
    return filename
