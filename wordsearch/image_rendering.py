"""
Renderizado avanzado de la sopa de letras y soluciones como imágenes (Pillow).
Incluye: título (con wrap), caja FUN FACT, grid centrado, pastilla "Solution on page X"
y lista de palabras en columnas, manteniendo el resaltado elegante para soluciones.
"""

import os
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


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
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
    Así evitamos artefactos en las esquinas.
    """
    try:
        # Pillow >= 5 tiene rounded_rectangle
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    except AttributeError:
        # Fallback muy simple sin dibujar el borde varias veces
        x1, y1, x2, y2 = xy
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill, outline=None)
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill, outline=None)
        # esquinas
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
    page_width: int,
    line_spacing: float = 1.05,
) -> int:
    """
    Dibuja el título centrado con word-wrap si es muy largo.
    Devuelve la coordenada y justo debajo del bloque de título.
    """
    lines = _wrap_text(draw, text, font, max_width)
    y = start_y
    for line in lines:
        w, h = _text_size(draw, line, font)
        x = (page_width - w) // 2
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
    if os.path.exists(BACKGROUND_PATH):
        bg = Image.open(BACKGROUND_PATH).convert("RGBA")
        # Redimensionamos el fondo al tamaño hi-res de la página
        bg = bg.resize((PAGE_W_HI, PAGE_H_HI), Image.LANCZOS)

        # Si quieres aclarar un poco el fondo para que no moleste al texto:
        # (baja alfa a ~70%)
        if bg.mode == "RGBA":
            r, g, b, a = bg.split()
            a = a.point(lambda v: int(v * 0.7))  # 70% de opacidad del PNG original
            bg = Image.merge("RGBA", (r, g, b, a))

        img = bg
    else:
        # Fondo blanco por defecto
        img = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    # === PANEL BLANCO PRINCIPAL PARA TODO EL CONTENIDO ===
    panel_pad_x = int(30 * SCALE)   # margen horizontal hacia dentro del borde
    panel_pad_top = int(40 * SCALE)
    panel_pad_bottom = int(40 * SCALE)

    panel_left = SAFE_LEFT_HI - panel_pad_x
    panel_right = SAFE_RIGHT_HI + panel_pad_x
    panel_top = TOP_PX_HI - panel_pad_top
    panel_bottom = SAFE_BOTTOM_HI + panel_pad_bottom

    # Nos aseguramos de no salirnos de la página
    panel_left = max(0, panel_left)
    panel_top = max(0, panel_top)
    panel_right = min(PAGE_W_HI, panel_right)
    panel_bottom = min(PAGE_H_HI, panel_bottom)

    _rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(35 * SCALE),
        fill=(255, 255, 255, 100),         # blanco casi opaco
        outline=(0, 0, 0, 60),             # borde muy suave
        width=max(1, int(3 * SCALE)),
    )


    # Fuentes
    font_title = _load_font(FONT_TITLE, TITLE_FONT_SIZE * SCALE)
    font_words = _load_font(FONT_PATH, WORDLIST_FONT_SIZE * SCALE)
    font_words_bold = _load_font(FONT_PATH_BOLD, WORDLIST_FONT_SIZE * SCALE)

    text_color = (0, 0, 0, 255)
    # FUN FACT
    fact_bg = (245, 245, 245, 245)          # fondo de la tarjeta
    fact_border = (170, 170, 170, 255)      # borde suave
    fact_header_bg = (30, 30, 30, 255)      # cabecera casi negra
    fact_header_text = (255, 255, 255, 255) # texto "FUN FACT"
    pill_bg = (230, 230, 230, 255)
    pill_border = (120, 120, 120, 255)

    # Resaltado soluciones
    highlight_fill = (243, 226, 200, 230)   # relleno
    highlight_border = (70, 80, 100, 255)   # borde más oscuro

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

    title_max_width = int(SAFE_RIGHT_HI - SAFE_LEFT_HI)
    y_after_title = _draw_wrapped_centered_title(
        draw,
        title_text,
        font_title,
        max_width=title_max_width,
        start_y=TOP_PX_HI,
        page_width=PAGE_W_HI,
        line_spacing=1.05,
    )

    # Más separación título → fact
    y_cursor_hi = y_after_title + int(80 * SCALE)

    # --------------------------------------------------------
    # FUN FACT – tarjeta con cabecera
    # --------------------------------------------------------
    if (not is_solution) and fun_fact:
        # Tipos de letra
        fact_label_font = _load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.9) * SCALE)
        fact_text_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75) * SCALE)

        # La tarjeta vive dentro del panel, con margen interior
        left_hi = panel_left + int(40 * SCALE)
        right_hi = panel_right - int(40 * SCALE)

        # Anchura disponible para texto dentro de la tarjeta
        inner_horizontal_pad = int(18 * SCALE)
        max_text_width_hi = int((right_hi - left_hi) - 2 * inner_horizontal_pad)

        # Etiqueta de cabecera
        fact_label = "FUN FACT"
        label_w, label_h = _text_size(draw, fact_label, fact_label_font)

        # Texto envuelto
        line_height_hi = int(fact_text_font.size * 1.10)
        fact_lines = _wrap_text(draw, fun_fact, fact_text_font, max_text_width_hi)

        # Medidas tarjeta
        header_pad_v_hi = int(8 * SCALE)    # padding vertical cabecera
        text_pad_v_hi = int(10 * SCALE)     # padding vertical del bloque de texto

        header_height_hi = label_h + 2 * header_pad_v_hi
        fact_text_height_hi = len(fact_lines) * line_height_hi

        box_top_hi = y_cursor_hi
        box_bottom_hi = (
            box_top_hi
            + header_height_hi
            + text_pad_v_hi            # espacio entre cabecera y texto
            + fact_text_height_hi
            + text_pad_v_hi            # padding inferior
        )

        # Tarjeta principal
        _rounded_rectangle(
            draw,
            (int(left_hi), int(box_top_hi), int(right_hi), int(box_bottom_hi)),
            radius=int(18 * SCALE),
            fill=fact_bg,
            outline=fact_border,
            width=max(1, int(2 * SCALE)),
        )

        # Cabecera oscura pegada a la parte superior de la tarjeta
        header_left_hi = left_hi
        header_right_hi = right_hi
        header_top_hi = box_top_hi
        header_bottom_hi = header_top_hi + header_height_hi

        _rounded_rectangle(
            draw,
            (int(header_left_hi), int(header_top_hi), int(header_right_hi), int(header_bottom_hi)),
            radius=int(18 * SCALE),
            fill=fact_header_bg,
            outline=None,
            width=0,
        )

        # Texto "FUN FACT" centrado en la cabecera
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

        # Texto del fact, alineado a la izquierda dentro de la tarjeta
        text_x_hi = left_hi + inner_horizontal_pad
        text_y_hi = header_bottom_hi + text_pad_v_hi

        for line in fact_lines:
            draw.text((text_x_hi, text_y_hi), line, font=fact_text_font, fill=text_color)
            text_y_hi += line_height_hi

        # Más separación FUN FACT → GRID
        y_cursor_hi = box_bottom_hi + int(50 * SCALE)


    # --------------------------------------------------------
    # GRID (protagonista)
    # --------------------------------------------------------
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Reservamos ~22% para wordlist
    words_block_height_hi = int(PAGE_H_HI * 0.22)
    max_grid_bottom_hi = SAFE_BOTTOM_HI - words_block_height_hi
    max_grid_height_hi = max_grid_bottom_hi - y_cursor_hi - int(25 * SCALE)
    max_grid_width_hi = SAFE_RIGHT_HI - SAFE_LEFT_HI

    cell_size_hi = min(
        max_grid_width_hi / max(cols, 1),
        max_grid_height_hi / max(rows, 1),
    )
    cell_size_hi = int(cell_size_hi)

    grid_w_hi = cell_size_hi * cols
    grid_h_hi = cell_size_hi * rows

    grid_left_hi = int((PAGE_W_HI - grid_w_hi) // 2)
    grid_top_hi = int(y_cursor_hi)

    letter_font_size_hi = max(int(cell_size_hi * 0.9), int(18 * SCALE))
    font_letter = _load_font(FONT_PATH, letter_font_size_hi)
    font_letter_bold = _load_font(FONT_PATH_BOLD, letter_font_size_hi)

    grid_line_width_hi = max(1, int(1.2 * SCALE))
    grid_line_color = "#444444"

    # --------------------------------------------------------
    # CAPA DE RESALTADO (solo soluciones, con cápsula)
    # --------------------------------------------------------
    overlay = Image.new("RGBA", (PAGE_W_HI, PAGE_H_HI), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    highlight_positions = set()

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

            thickness = cell_size_hi * 0.8
            radius = thickness / 2

            p0 = centers[0]
            p1 = centers[-1]

            # borde exterior
            odraw.line(
                centers,
                fill=highlight_border,
                width=int(thickness + 4 * SCALE),
                joint="curve",
            )
            for (cx, cy) in (p0, p1):
                odraw.ellipse(
                    (
                        cx - (radius + 2 * SCALE),
                        cy - (radius + 2 * SCALE),
                        cx + (radius + 2 * SCALE),
                        cy + (radius + 2 * SCALE),
                    ),
                    fill=highlight_border,
                )

            # relleno interior
            odraw.line(
                centers,
                fill=highlight_fill,
                width=int(thickness),
                joint="curve",
            )
            for (cx, cy) in (p0, p1):
                odraw.ellipse(
                    (cx - radius, cy - radius, cx + radius, cy + radius),
                    fill=highlight_fill,
                )

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

            chosen_font = font_letter  # primero todas normales

            try:
                draw.text(
                    (cx, cy),
                    letter,
                    fill="black",
                    font=chosen_font,
                    anchor="mm",
                )
            except TypeError:
                lw, lh = _text_size(draw, letter, chosen_font)
                draw.text(
                    (cx - lw / 2, cy - lh / 2),
                    letter,
                    fill="black",
                    font=chosen_font,
                )

    # Combinamos overlay
    img.alpha_composite(overlay)

    # Redibujar letras de palabras resaltadas ENCIMA del overlay y en negrita
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
                chosen_font = font_letter_bold
                try:
                    draw.text(
                        (cx, cy),
                        letter,
                        fill="black",
                        font=chosen_font,
                        anchor="mm",
                    )
                except TypeError:
                    lw, lh = _text_size(draw, letter, chosen_font)
                    draw.text(
                        (cx - lw / 2, cy - lh / 2),
                        letter,
                        fill="black",
                        font=chosen_font,
                    )

    grid_bottom_hi = grid_top_hi + grid_h_hi

    # --------------------------------------------------------
    # ÁREA INFERIOR (pill + lista)
    # --------------------------------------------------------
    # Primero definimos un margen fijo desde el grid hacia abajo
    base_gap_hi = int(60 * SCALE)
    temp_words_top_hi = grid_bottom_hi + base_gap_hi
    words_bottom_hi = SAFE_BOTTOM_HI - int(8 * SCALE)

    # --------------------------------------------------------
    # PASTILLA "Solution on page X" entre grid y palabras
    # --------------------------------------------------------
    pill_box_h = 0
    pill_y = temp_words_top_hi
    if (not is_solution) and solution_page_number is not None:
        pill_font = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75) * SCALE)
        pill_text = f"Solution on page {solution_page_number}"
        tw_pill, th_pill = _text_size(draw, pill_text, pill_font)

        pad_h = int(16 * SCALE)
        pad_w = int(16 * SCALE)
        box_w = tw_pill + 2 * pad_w
        box_h = th_pill + 2 * pad_h
        pill_box_h = box_h

        pill_x = int((panel_left + panel_right - box_w) // 2)
        pill_y = temp_words_top_hi  # justo después del hueco desde el grid

        _rounded_rectangle(
            draw,
            (pill_x, pill_y, pill_x + box_w, pill_y + box_h),
            radius=box_h // 2,
            fill=pill_bg,
            outline=pill_border,
            width=max(1, int(2 * SCALE)),
        )

        # Centrar texto dentro de la pastilla usando el tamaño medido
        tx = pill_x + box_w / 2
        ty = pill_y + box_h / 2
        try:
            draw.text((tx, ty), pill_text, font=pill_font, fill=text_color, anchor="mm")
        except TypeError:
            draw.text((tx - tw_pill / 2, ty - th_pill / 2), pill_text, font=pill_font, fill=text_color)

    # Ahora sí, área de palabras empieza un poco POR DEBAJO de la pill
    words_top_hi = pill_y + pill_box_h + int(30 * SCALE)
    if words_top_hi > words_bottom_hi:
        words_top_hi = words_bottom_hi
    words_height_hi = max(0, words_bottom_hi - words_top_hi)

    # --------------------------------------------------------
    # LISTA DE PALABRAS (pequeñas, pegadas al final)
    # --------------------------------------------------------
    words_upper = [str(w).upper() for w in words]
    if words_upper and words_height_hi > 0:
        col_count = 3 if len(words_upper) >= 18 else 2
        area_left_hi = SAFE_LEFT_HI
        area_right_hi = SAFE_RIGHT_HI
        total_w_hi = area_right_hi - area_left_hi
        col_w_hi = total_w_hi / col_count

        col_words: List[List[str]] = [[] for _ in range(col_count)]
        for i, w in enumerate(words_upper):
            col_idx = i % col_count
            col_words[col_idx].append(w)

        # aún más pequeñas para ganar aire
        font_words_real = _load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.6) * SCALE)
        line_h_hi = int(font_words_real.size * 1.12)

        for ci in range(col_count):
            cw = col_words[ci]
            if not cw:
                continue

            col_center_x = int(area_left_hi + (ci + 0.5) * col_w_hi)

            used_h = len(cw) * line_h_hi
            y_start = words_bottom_hi - used_h
            if y_start < words_top_hi:
                y_start = words_top_hi

            y_hi = int(y_start)
            for w in cw:
                if y_hi + line_h_hi > words_bottom_hi:
                    break
                try:
                    draw.text(
                        (col_center_x, y_hi),
                        w,
                        fill=text_color,
                        font=font_words_real,
                        anchor="mm",
                    )
                except TypeError:
                    ww, hh = _text_size(draw, w, font_words_real)
                    draw.text(
                        (col_center_x - ww / 2, y_hi - hh / 2),
                        w,
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
