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
from wordsearch.image_rendering import render_page
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

    # Dificultad + tamaño de grid (comunes para todo el libro)
    difficulty = _ask_difficulty()
    settings = difficulty_settings[difficulty]
    grid_size = ask_grid_size(settings)

    # Directorio de salida
    from wordsearch.constants_and_layout import BASE_OUTPUT_DIR
    output_dir = os.path.join(BASE_OUTPUT_DIR, slugify(book_title))
    os.makedirs(output_dir, exist_ok=True)

    puzzle_imgs = []
    solution_imgs = []

    for spec in specs:
        print(f"Generando puzzle {spec.index + 1}/{total_puzzles}: {spec.title}")

        def clean_for_grid(word: str) -> str:
            return "".join(ch for ch in word.upper() if ch.isalpha())
        
        words_for_grid = [clean_for_grid(w) for w in spec.words]

        placed_result = place_words_on_grid(words_for_grid, difficulty=difficulty, grid_size=grid_size)
        if placed_result is None:
            print(f"  [AVISO] No se pudo generar grid para el puzzle {spec.index + 1}. Se salta.")
            continue

        grid, placed = placed_result

        # PDF final: primero todos los puzzles, luego portada de soluciones, luego soluciones.
        # -> Puzzle i está en página (i+1)
        # -> Portada soluciones en página (N + 1)
        # -> Solución i está en página (N + 2 + i)
        solution_page_number = total_puzzles + 2 + spec.index

        puzzle_filename = os.path.join(output_dir, f"puzzle_{spec.index + 1}.png")
        solution_filename = os.path.join(output_dir, f"puzzle_{spec.index + 1}_sol.png")

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
        )

        img_solution = render_page(
            grid,
            spec.words,
            spec.index + 1,
            is_solution=True,
            filename=solution_filename,
            placed_words=placed,
            puzzle_title=spec.title,
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
