"""
Script para generar un libro TEMÁTICO completo de sopas de letras
a partir de un TXT gigante con bloques [Puzzle] ... [/Puzzle].

Flujo:
- Lee el fichero (p.ej. wordlists/black_culture_book.txt)
- Pregunta dificultad y tamaño de grid (igual para todo el libro)
- Genera grids + imágenes (puzzles y soluciones) con layout editorial
- Genera el PDF final con portada de soluciones incluida
"""

import os

from wordsearch.difficulty_levels import DifficultyLevel, difficulty_settings
from wordsearch.grid_size_utils import ask_grid_size
from wordsearch.grid_generation import place_words_on_grid
from wordsearch.image_rendering import render_page, render_block_cover
from wordsearch.pdf_book_generation import generate_pdf
from wordsearch.wordlist_utils import slugify
from wordsearch.puzzle_parser import parse_puzzle_file, PuzzleParseError


def _ask_difficulty() -> DifficultyLevel:
    print("Selecciona nivel de dificultad:")
    print("  1) EASY")
    print("  2) MEDIUM")
    print("  3) HARD")
    while True:
        raw = input("Opción [1-3, por defecto 2]: ").strip()
        if not raw:
            return DifficultyLevel.MEDIUM
        if raw == "1":
            return DifficultyLevel.EASY
        if raw == "2":
            return DifficultyLevel.MEDIUM
        if raw == "3":
            return DifficultyLevel.HARD
        print("Opción no válida. Elige 1, 2 o 3.")


def main():
    print("=== Generador TEMÁTICO de Wordsearch para KDP ===")

    book_title = input("Título del libro (p.ej. 'Black Culture Word Search Vol. 1'): ").strip()
    if not book_title:
        book_title = "Wordsearch Thematic Book"

    puzzles_txt_path = input(
        "Ruta del TXT con los puzzles temáticos "
        "[por defecto wordlists/book_thematic.txt]: "
    ).strip()
    if not puzzles_txt_path:
        puzzles_txt_path = os.path.join("wordlists", "book_thematic.txt")

    try:
        specs = parse_puzzle_file(puzzles_txt_path)
    except FileNotFoundError:
        print(f"ERROR: No se encuentra el fichero: {puzzles_txt_path}")
        return
    except PuzzleParseError as e:
        print(f"ERROR de parseo: {e}")
        return

    total_puzzles = len(specs)
    if total_puzzles == 0:
        print("No se ha encontrado ningún bloque [Puzzle] en el fichero.")
        return

    print(f"Se han cargado {total_puzzles} puzzles del fichero.")

    # ---------------------------------------------
    # Dificultad + tamaño de grid (comunes)
    # ---------------------------------------------
    difficulty = _ask_difficulty()
    settings = difficulty_settings[difficulty]
    grid_size = ask_grid_size(settings)

    # Directorio de salida
    from wordsearch.constants_and_layout import BASE_OUTPUT_DIR
    output_dir = os.path.join(BASE_OUTPUT_DIR, slugify(book_title))
    os.makedirs(output_dir, exist_ok=True)

    puzzle_imgs = []    # aquí incluiremos portadas de bloque + puzzles
    solution_imgs = []

    # ---------------------------------------------
    # Cálculo de nº de bloques (para paginación)
    # Contamos cambios de block_name en orden.
    # ---------------------------------------------
    block_names_ordered = []
    last_block = object()
    for s in specs:
        if s.block_name and s.block_name != last_block:
            block_names_ordered.append(s.block_name)
            last_block = s.block_name
    num_blocks = len(block_names_ordered)

    # En el PDF:
    # - Primero va una portada interna creada en generate_pdf (página 1)
    # - Luego TODAS las imágenes de puzzle_imgs (portadas de bloque + puzzles)
    # - Luego portada de soluciones
    # - Luego todas las soluciones.
    #
    # En la versión anterior (sin bloques), hacíamos:
    #   solution_page_number = total_puzzles + 2 + spec.index
    # donde "total_puzzles + 2" era el offset fijo antes de empezar las soluciones.
    #
    # Ahora hay num_blocks páginas extra (portadas de bloque) en la sección de puzzles,
    # así que el offset aumenta en num_blocks:
    pages_before_first_solution = total_puzzles + num_blocks + 2

    # ---------------------------------------------
    # Generación de grids e imágenes
    # ---------------------------------------------
    current_block_name = None
    block_counter = 0

    for spec in specs:
        print(f"Generando puzzle {spec.index + 1}/{total_puzzles}: {spec.title}")

        # Si empezamos un bloque nuevo, generamos primero su portada de bloque
        if spec.block_name and spec.block_name != current_block_name:
            current_block_name = spec.block_name
            block_counter += 1

            cover_bg_path = spec.block_background or None
            cover_filename = os.path.join(
                output_dir,
                f"block_{block_counter:02d}_{slugify(spec.block_name)}.png",
            )

            cover_img = render_block_cover(
                block_name=spec.block_name,
                block_index=block_counter,
                filename=cover_filename,
                background_path=cover_bg_path,
            )
            puzzle_imgs.append(cover_img)

        # Limpieza de palabras para el grid (quitamos espacios y no-alfas)
        def clean_for_grid(word: str) -> str:
            return "".join(ch for ch in word.upper() if ch.isalpha())

        words_for_grid = [clean_for_grid(w) for w in spec.words]

        placed_result = place_words_on_grid(
            words_for_grid,
            difficulty=difficulty,
            grid_size=grid_size,
        )
        if placed_result is None:
            print(f"  [AVISO] No se pudo generar grid para el puzzle {spec.index + 1}. Se salta.")
            continue

        grid, placed = placed_result

        # Paginación de la solución, teniendo en cuenta:
        # - total_puzzles      -> nº de puzzles
        # - num_blocks         -> nº de portadas de bloque
        # - "2"                -> portada interna + portada de soluciones
        solution_page_number = pages_before_first_solution + spec.index

        puzzle_filename = os.path.join(output_dir, f"puzzle_{spec.index + 1}.png")
        solution_filename = os.path.join(output_dir, f"puzzle_{spec.index + 1}_sol.png")

        bg_path = spec.block_background or None

        img_puzzle = render_page(
            grid,
            spec.words,
            spec.index + 1,
            is_solution=False,
            filename=puzzle_filename,
            placed_words=placed,
            puzzle_title=spec.title,
            fun_fact=spec.fact,
            solution_page_number=solution_page_number,
            background_path=bg_path,
        )

        img_solution = render_page(
            grid,
            spec.words,
            spec.index + 1,
            is_solution=True,
            filename=solution_filename,
            placed_words=placed,
            puzzle_title=spec.title,
            background_path=bg_path,
        )

        puzzle_imgs.append(img_puzzle)
        solution_imgs.append(img_solution)

    if not puzzle_imgs or not solution_imgs:
        print("No se han generado imágenes suficientes como para crear el PDF.")
        return

    pdf_name = f"{slugify(book_title)}.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    pdf_final = generate_pdf(puzzle_imgs, solution_imgs, outname=pdf_path)
    print("\nPDF generado:", pdf_final)


if __name__ == "__main__":
    main()
