import random
import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# =========================================================
# CONFIGURACIÓN PRINCIPAL
# =========================================================

OUTPUT_DIR = "output_puzzles_kdp"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Tamaño libro KDP: 6x9 pulgadas a 300 DPI
TRIM_W_IN, TRIM_H_IN = 6.0, 9.0
DPI = 300
PAGE_W_PX = int(TRIM_W_IN * DPI)      # 1800 px
PAGE_H_PX = int(TRIM_H_IN * DPI)      # 2700 px

# Márgenes seguros KDP
GUTTER_IN = 0.375
OUTSIDE_IN = 0.25
TOP_IN = 0.25
BOTTOM_IN = 0.25

# Conversión a píxeles
GUTTER_PX = int(GUTTER_IN * DPI)
OUTSIDE_PX = int(OUTSIDE_IN * DPI)
TOP_PX = int(TOP_IN * DPI)
BOTTOM_PX = int(BOTTOM_IN * DPI)

SAFE_LEFT = GUTTER_PX + 50
SAFE_RIGHT = PAGE_W_PX - OUTSIDE_PX - 50
SAFE_TOP = TOP_PX + 120
SAFE_BOTTOM = PAGE_H_PX - BOTTOM_PX - 220

# ---------------------------------------------------------
# FUENTE: AJUSTA ESTA RUTA A TU SISTEMA
# ---------------------------------------------------------

FONT_PATH = "C:/Users/nacho/Documents/Fonts/MONTSERRAT/static/Montserrat-Regular.ttf"

FONT_PATH_BOLD = "C:/Users/nacho/Documents/Fonts/MONTSERRAT/static/Montserrat-Medium.ttf"

# Tamaños base (el de letras del grid se recalcula dinámicamente)
TITLE_FONT_SIZE = 130
WORDLIST_FONT_SIZE = 80

# Grid
GRID_SIZE = 12
DIRECTIONS = [
    (0, 1), (1, 0), (0, -1), (-1, 0),
    (1, 1), (1, -1), (-1, 1), (-1, -1)
]


# =========================================================
# FUNCIÓN PARA COLOCAR PALABRAS EN EL GRID
# =========================================================
def place_words_on_grid(words, size=GRID_SIZE, max_attempts=500):
    grid = [['' for _ in range(size)] for _ in range(size)]
    placed = []
    words_sorted = sorted(words, key=lambda w: -len(w))
    attempts = 0

    for w in words_sorted:
        w = w.upper()
        candidates = []
        for r in range(size):
            for c in range(size):
                for dr, dc in DIRECTIONS:
                    candidates.append((r, c, dr, dc))

        random.shuffle(candidates)
        placed_flag = False

        for (r, c, dr, dc) in candidates:
            rr, cc = r, c
            fits = True

            for ch in w:
                if not (0 <= rr < size and 0 <= cc < size):
                    fits = False
                    break
                if grid[rr][cc] not in ('', ch):
                    fits = False
                    break
                rr += dr
                cc += dc

            if not fits:
                continue

            rr, cc = r, c
            for ch in w:
                grid[rr][cc] = ch
                rr += dr
                cc += dc

            placed.append((w, (r, c, dr, dc)))
            placed_flag = True
            break

        if not placed_flag:
            attempts += 1
            if attempts > max_attempts:
                return None
            return None

    for r in range(size):
        for c in range(size):
            if grid[r][c] == '':
                grid[r][c] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return grid, placed


# =========================================================
# FUNCIÓN PARA RENDERIZAR UNA PÁGINA COMPLETA (PUZZLE O SOLUCIÓN)
# =========================================================
def render_page(grid, words, idx, is_solution=False, solution_positions=None, filename=None):
    img = Image.new('RGB', (PAGE_W_PX, PAGE_H_PX), 'white')
    draw = ImageDraw.Draw(img)

    # -------------------
    # Fuentes: título (bold) y lista de palabras (regular)
    # -------------------
    # Si tienes dos rutas (regular / bold), puedes separarlas:
    # FONT_PATH = r"...Montserrat-Regular.ttf"
    # FONT_PATH_BOLD = r"...Montserrat-SemiBold.ttf"
    FONT_PATH_BOLD = FONT_PATH  # si de momento solo tienes una

    try:
        font_title = ImageFont.truetype(FONT_PATH_BOLD, TITLE_FONT_SIZE)
        font_words = ImageFont.truetype(FONT_PATH, WORDLIST_FONT_SIZE)
    except Exception:
        font_title = ImageFont.load_default()
        font_words = ImageFont.load_default()

    # -------------------
    # TÍTULO CENTRADO ARRIBA
    # -------------------
    title = f"Puzzle #{idx}" if not is_solution else f"Solution #{idx}"
    bbox_title = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox_title[2] - bbox_title[0]
    th = bbox_title[3] - bbox_title[1]

    title_x = (PAGE_W_PX - tw) // 2
    title_y = TOP_PX + 40
    draw.text((title_x, title_y), title, fill="black", font=font_title)

    # -------------------
    # CÁLCULO DEL GRID (centrado)
    # -------------------
    grid_rows = len(grid)
    grid_cols = len(grid[0])

    max_grid_height = SAFE_BOTTOM - (title_y + th + 200)
    max_grid_width = SAFE_RIGHT - SAFE_LEFT

    cell_size = min(max_grid_width // grid_cols, max_grid_height // grid_rows)

    grid_total_w = cell_size * grid_cols
    grid_total_h = cell_size * grid_rows

    grid_left = (PAGE_W_PX - grid_total_w) // 2
    grid_top = title_y + th + 160

    # Fuente de las letras del grid, dinámica
    try:
        letter_font_size = int(cell_size * 0.75)
        font_letter = ImageFont.truetype(FONT_PATH, letter_font_size)
    except Exception:
        font_letter = ImageFont.load_default()

    grid_line_width = 1
    grid_line_color = "#444444"
    highlight_color = (220, 235, 255)

    # -------------------
    # DIBUJAR GRID + LETRAS (centradas con anchor="mm")
    # -------------------
    for r in range(grid_rows):
        for c in range(grid_cols):
            x = grid_left + c * cell_size
            y = grid_top + r * cell_size

            # fondo de solución
            if is_solution and solution_positions and (r, c) in solution_positions:
                draw.rectangle(
                    [x + 2, y + 2, x + cell_size - 2, y + cell_size - 2],
                    fill=highlight_color
                )

            # borde de celda
            draw.rectangle(
                [x, y, x + cell_size, y + cell_size],
                outline=grid_line_color,
                width=grid_line_width
            )

            # letra centrada
            letter = grid[r][c]
            cx = x + cell_size / 2
            cy = y + cell_size / 2

            # Intentamos centrar con anchor='mm'; si Pillow es antiguo, fallback manual
            try:
                draw.text((cx, cy), letter, fill="black", font=font_letter, anchor="mm")
            except TypeError:
                # Fallback: usando bbox para centrar
                bbox_letter = draw.textbbox((0, 0), letter, font=font_letter)
                lw = bbox_letter[2] - bbox_letter[0]
                lh = bbox_letter[3] - bbox_letter[1]
                lx = x + (cell_size - lw) // 2
                ly = y + (cell_size - lh) // 2
                draw.text((lx, ly), letter, fill="black", font=font_letter)

    # -------------------
    # LISTA DE PALABRAS EN DOS COLUMNAS, CENTRADAS
    # -------------------
    words_upper = [w.upper() for w in words]

    half = (len(words_upper) + 1) // 2
    col1 = words_upper[:half]
    col2 = words_upper[half:]

    # Aseguramos que la fuente exista
    try:
        font_words = ImageFont.truetype(FONT_PATH, WORDLIST_FONT_SIZE)
    except Exception:
        font_words = ImageFont.load_default()

    # Distancia vertical entre líneas
    # Usamos bbox para calcular una altura de línea razonable
    sample_bbox = draw.textbbox((0, 0), "AY", font=font_words)
    base_line_height = sample_bbox[3] - sample_bbox[1]
    line_height = base_line_height + 40

    # Punto de partida vertical
    bottom_margin = BOTTOM_PX + 80
    max_lines = max(len(col1), len(col2))

    start_y = PAGE_H_PX - bottom_margin - max_lines * line_height

    # Que quede por debajo del grid con aire
    min_start_y = grid_top + grid_total_h + 140
    if start_y < min_start_y:
        start_y = min_start_y

    # Calculamos ancho máximo de cada columna
    def max_width(word_list):
        if not word_list:
            return 0
        widths = []
        for w in word_list:
            bb = draw.textbbox((0, 0), w, font=font_words)
            widths.append(bb[2] - bb[0])
        return max(widths)

    max_w_col1 = max_width(col1)
    max_w_col2 = max_width(col2)

    center_x = PAGE_W_PX / 2
    gap = 160  # espacio entre columnas

    # Centros de cada columna
    col1_center_x = center_x - (gap / 2) - (max_w_col1 / 2)
    col2_center_x = center_x + (gap / 2) + (max_w_col2 / 2)

    # Dibuja columna 1
    y = start_y
    for w in col1:
        try:
            draw.text((col1_center_x, y), w, fill="black", font=font_words, anchor="mm")
        except TypeError:
            bb = draw.textbbox((0, 0), w, font=font_words)
            ww = bb[2] - bb[0]
            hh = bb[3] - bb[1]
            draw.text((col1_center_x - ww / 2, y - hh / 2), w, fill="black", font=font_words)
        y += line_height

    # Dibuja columna 2
    y = start_y
    for w in col2:
        try:
            draw.text((col2_center_x, y), w, fill="black", font=font_words, anchor="mm")
        except TypeError:
            bb = draw.textbbox((0, 0), w, font=font_words)
            ww = bb[2] - bb[0]
            hh = bb[3] - bb[1]
            draw.text((col2_center_x - ww / 2, y - hh / 2), w, fill="black", font=font_words)
        y += line_height

    # -------------------
    # GUARDAR
    # -------------------
    if filename is None:
        filename = os.path.join(OUTPUT_DIR, f"puzzle_{idx}{'_sol' if is_solution else ''}.png")

    img.save(filename, dpi=(DPI, DPI))
    return filename



# =========================================================
# GENERAR EL LIBRO COMPLETO (PUZZLES + SOLUCIONES)
# =========================================================
def generate_pdf(puzzle_imgs, solution_imgs, outname="wordsearch_book_kdp.pdf"):
    pdf_path = os.path.join(OUTPUT_DIR, outname)
    c = canvas.Canvas(pdf_path, pagesize=(TRIM_W_IN * inch, TRIM_H_IN * inch))

    def add_page(image_path):
        c.drawImage(image_path, 0, 0, width=TRIM_W_IN * inch, height=TRIM_H_IN * inch)
        c.showPage()

    # Páginas de puzzles
    for img in puzzle_imgs:
        add_page(img)

    # Página separadora de soluciones
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(TRIM_W_IN * inch / 2, TRIM_H_IN * inch / 2, "SOLUTIONS")
    c.showPage()

    # Páginas de soluciones
    for img in solution_imgs:
        add_page(img)

    c.save()
    return pdf_path


# =========================================================
# EJEMPLO DE GENERACIÓN (modifica aquí tus palabras)
# =========================================================
if __name__ == "__main__":

    # EJEMPLO: listas de palabras
    wordlists = [
        ["gato", "perro", "casa", "luna", "sol", "arbol", "cielo", "mar"],
        ["python", "codigo", "amazon", "kdp", "libro", "puzzle", "print"],
    ]

    total = 6  # CUÁNTOS PUZZLES QUIERES GENERAR
    puzzles = []
    solutions = []

    for i in range(1, total + 1):
        wl = random.choice(wordlists).copy()
        random.shuffle(wl)

        while True:
            placed_result = place_words_on_grid(wl)
            if placed_result:
                grid, placed = placed_result
                break

        sol_positions = set()
        for w, (r, c, dr, dc) in placed:
            rr, cc = r, c
            for ch in w:
                sol_positions.add((rr, cc))
                rr += dr
                cc += dc

        puzzle_img = render_page(grid, wl, i, is_solution=False)
        solution_img = render_page(grid, wl, i, is_solution=True, solution_positions=sol_positions)

        puzzles.append(puzzle_img)
        solutions.append(solution_img)

    pdf_final = generate_pdf(puzzles, solutions)
    print("PDF generado:", pdf_final)
