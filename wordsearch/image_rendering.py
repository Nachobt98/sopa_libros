"""
Renderizado de la sopa de letras y soluciones como imágenes (Pillow).
Incluye: render_page, estilos, resaltado, etc.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from wordsearch.constants_and_layout import (
    PAGE_W_PX, PAGE_H_PX, SAFE_LEFT, SAFE_RIGHT, SAFE_BOTTOM, FONT_PATH, FONT_PATH_BOLD, title_font_size as TITLE_FONT_SIZE, wordlist_font_size as WORDLIST_FONT_SIZE
)

def render_page(
    grid,
    words,
    idx,
    is_solution=False,
    solution_positions=None,  # se mantiene por compatibilidad, aunque ya no lo usamos
    filename=None,
    placed_words=None,        # lista de (word, (r, c, dr, dc))
):
    # ============================================================
    # SUPERSAMPLING – Dibujar a 3x y luego reducir (antialiasing)
    # ============================================================
    SCALE = 3

    PAGE_W_HI = PAGE_W_PX * SCALE
    PAGE_H_HI = PAGE_H_PX * SCALE

    # Márgenes / área segura escalados
    from wordsearch.constants_and_layout import TOP_PX, BOTTOM_PX
    TOP_PX_HI = TOP_PX * SCALE
    BOTTOM_PX_HI = BOTTOM_PX * SCALE
    SAFE_LEFT_HI = SAFE_LEFT * SCALE
    SAFE_RIGHT_HI = SAFE_RIGHT * SCALE
    SAFE_BOTTOM_HI = SAFE_BOTTOM * SCALE

    img = Image.new('RGBA', (PAGE_W_HI, PAGE_H_HI), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # -------------------
    # Fuentes (hi-res)
    # -------------------
    try:
        font_title = ImageFont.truetype(FONT_PATH_BOLD, TITLE_FONT_SIZE * SCALE)
        font_words = ImageFont.truetype(FONT_PATH, WORDLIST_FONT_SIZE * SCALE)
    except Exception:
        font_title = ImageFont.load_default()
        font_words = ImageFont.load_default()

    # -------------------
    # TÍTULO + LÍNEA DECORATIVA
    # -------------------
    title = f"Puzzle {idx}" if not is_solution else f"Solution {idx}"
    bbox_title = draw.textbbox((0, 0), title, font=font_title)
    tw_hi = bbox_title[2] - bbox_title[0]
    th_hi = bbox_title[3] - bbox_title[1]

    title_y_hi = TOP_PX_HI + 40 * SCALE
    title_x_hi = (PAGE_W_HI - tw_hi) // 2
    draw.text((title_x_hi, title_y_hi), title, fill="black", font=font_title)

    line_margin_side_hi = int(PAGE_W_HI * 0.15)
    # Aumentar la separación entre el título y la línea decorativa
    extra_space = 60 * SCALE  # puedes ajustar este valor para más o menos separación
    line_y_hi = title_y_hi + th_hi + extra_space
    draw.line(
        (line_margin_side_hi, line_y_hi, PAGE_W_HI - line_margin_side_hi, line_y_hi),
        fill="#777777",
        width=1 * SCALE
    )

    # -------------------
    # CÁLCULO DEL GRID (hi-res)
    # -------------------
    grid_rows = len(grid)
    grid_cols = len(grid[0])

    max_grid_height_hi = SAFE_BOTTOM_HI - (line_y_hi + 160 * SCALE)
    max_grid_width_hi = SAFE_RIGHT_HI - SAFE_LEFT_HI

    cell_size_hi = min(max_grid_width_hi // grid_cols, max_grid_height_hi // grid_rows)

    grid_total_w_hi = cell_size_hi * grid_cols
    grid_total_h_hi = cell_size_hi * grid_rows

    grid_left_hi = (PAGE_W_HI - grid_total_w_hi) // 2
    grid_top_hi = line_y_hi + 120 * SCALE

    # Fuente de letras del grid (normal + bold)
    try:
        letter_font_size_hi = int(cell_size_hi * 0.75)
        font_letter = ImageFont.truetype(FONT_PATH, letter_font_size_hi)
        font_letter_bold = ImageFont.truetype(FONT_PATH_BOLD, letter_font_size_hi)
    except Exception:
        font_letter = font_letter_bold = ImageFont.load_default()

    grid_line_width_hi = 1 * SCALE
    grid_line_color = "#444444"

    # Colores del resaltado
    highlight_fill = (230, 235, 240, 210)  # gris claro semitransparente
    border_color = (190, 195, 200, 255)    # borde algo más oscuro

    # -------------------
    # CAPA DE RESALTADO (solo soluciones)
    # -------------------
    overlay = Image.new('RGBA', (PAGE_W_HI, PAGE_H_HI), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    if is_solution and placed_words:
        # Para cada palabra: primero borde oscuro, luego interior claro
        for w, (r, c, dr, dc) in placed_words:
            wlen = len(w)
            if wlen < 2:
                continue
            centers = []
            rr, cc = r, c
            for _ in range(wlen):
                cx = grid_left_hi + cc * cell_size_hi + cell_size_hi / 2
                cy = grid_top_hi + rr * cell_size_hi + cell_size_hi / 2
                centers.append((cx, cy))
                rr += dr
                cc += dc
            if len(centers) < 2:
                continue
            inner_width = max(4 * SCALE, int(cell_size_hi * 0.8))
            border_thickness = max(2 * SCALE, int(cell_size_hi * 0.1))
            outer_width = inner_width + 3 * border_thickness
            # Borde oscuro
            try:
                odraw.line(centers, fill=border_color, width=outer_width, joint="curve")
            except TypeError:
                odraw.line(centers, fill=border_color, width=outer_width)
            (sx, sy) = centers[0]
            (ex, ey) = centers[-1]
            r_out = outer_width / 2.0
            for (cx, cy) in [(sx, sy), (ex, ey)]:
                odraw.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], fill=border_color)
            # Interior claro
            try:
                odraw.line(centers, fill=highlight_fill, width=inner_width, joint="curve")
            except TypeError:
                odraw.line(centers, fill=highlight_fill, width=inner_width)
            r_in = inner_width / 2.0
            for (cx, cy) in [(sx, sy), (ex, ey)]:
                odraw.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=highlight_fill)

    # Combinar overlay de resaltado con la imagen base
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # -------------------
    # POSICIONES DESTACADAS (para poner letras en negrita)
    # -------------------
    highlight_positions = set()
    if is_solution and placed_words:
        for w, (r, c, dr, dc) in placed_words:
            rr, cc = r, c
            for _ in range(len(w)):
                highlight_positions.add((rr, cc))
                rr += dr
                cc += dc

    # -------------------
    # DIBUJAR GRID + LETRAS
    # -------------------
    for r in range(grid_rows):
        for c in range(grid_cols):
            x0 = grid_left_hi + c * cell_size_hi
            y0 = grid_top_hi + r * cell_size_hi
            x1 = x0 + cell_size_hi
            y1 = y0 + cell_size_hi

            # borde celda
            draw.rectangle([x0, y0, x1, y1], outline=grid_line_color, width=grid_line_width_hi)

            # letra centrada (bold si está dentro de una palabra resaltada)
            letter = grid[r][c]
            cx = x0 + cell_size_hi / 2
            cy = y0 + cell_size_hi / 2

            chosen_font = font_letter_bold if (r, c) in highlight_positions else font_letter

            try:
                draw.text((cx, cy), letter, fill="black", font=chosen_font, anchor="mm")
            except TypeError:
                bbox = draw.textbbox((0, 0), letter, font=chosen_font)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                draw.text(
                    (cx - lw / 2, cy - lh / 2),
                    letter,
                    fill="black",
                    font=chosen_font
                )

    # -------------------
    # LISTA DE PALABRAS EN DOS COLUMNAS
    # -------------------
    words_upper = [w.upper() for w in words]
    half = (len(words_upper) + 1) // 2
    col1 = words_upper[:half]
    col2 = words_upper[half:]

    try:
        font_words = ImageFont.truetype(FONT_PATH, WORDLIST_FONT_SIZE * SCALE)
    except Exception:
        font_words = ImageFont.load_default()

    sample_bbox = draw.textbbox((0, 0), "AY", font=font_words)
    base_line_height_hi = sample_bbox[3] - sample_bbox[1]
    line_height_hi = base_line_height_hi + 20 * SCALE

    max_lines = max(len(col1), len(col2))
    block_height_hi = max_lines * line_height_hi

    top_area_hi = grid_top_hi + grid_total_h_hi + 80 * SCALE
    bottom_area_hi = PAGE_H_HI - (BOTTOM_PX_HI + 80 * SCALE)

    available_space_hi = bottom_area_hi - top_area_hi
    if available_space_hi < block_height_hi:
        start_y_hi = top_area_hi + 10 * SCALE
    else:
        start_y_hi = top_area_hi + (available_space_hi - block_height_hi) / 2

    def max_width_hi(word_list):
        if not word_list:
            return 0
        widths = []
        for w in word_list:
            bb = draw.textbbox((0, 0), w, font=font_words)
            widths.append(bb[2] - bb[0])
        return max(widths)

    max_w_col1_hi = max_width_hi(col1)
    max_w_col2_hi = max_width_hi(col2)

    center_x_hi = PAGE_W_HI / 2
    gap_hi = 180 * SCALE

    col1_center_x_hi = center_x_hi - (gap_hi / 2) - (max_w_col1_hi / 2)
    col2_center_x_hi = center_x_hi + (gap_hi / 2) + (max_w_col2_hi / 2)

    # Columna 1
    y_hi = start_y_hi
    for w in col1:
        try:
            draw.text((col1_center_x_hi, y_hi), w, fill="black", font=font_words, anchor="mm")
        except TypeError:
            bb = draw.textbbox((0, 0), w, font=font_words)
            ww = bb[2] - bb[0]
            hh = bb[3] - bb[1]
            draw.text(
                (col1_center_x_hi - ww / 2, y_hi - hh / 2),
                w,
                fill="black",
                font=font_words
            )
        y_hi += line_height_hi

    # Columna 2
    y_hi = start_y_hi
    for w in col2:
        try:
            draw.text((col2_center_x_hi, y_hi), w, fill="black", font=font_words, anchor="mm")
        except TypeError:
            bb = draw.textbbox((0, 0), w, font=font_words)
            ww = bb[2] - bb[0]
            hh = bb[3] - bb[1]
            draw.text(
                (col2_center_x_hi - ww / 2, y_hi - hh / 2),
                w,
                fill="black",
                font=font_words
            )
        y_hi += line_height_hi

    # -------------------
    # GUARDAR (reducido a tamaño final KDP)
    # -------------------
    if filename is None:
        filename = os.path.join("output_puzzles_kdp", f"puzzle_{idx}{'_sol' if is_solution else ''}.png")

    img_rgb = img.convert('RGB')
    img_final = img_rgb.resize((PAGE_W_PX, PAGE_H_PX), resample=Image.LANCZOS)
    img_final.save(filename, dpi=(300, 300))
    return filename
