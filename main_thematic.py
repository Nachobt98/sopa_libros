"""
Script para generar un libro TEMÁTICO completo de sopas de letras
a partir de un TXT gigante con bloques [Puzzle] ... [/Puzzle].

Flujo:
- Lee el fichero (p.ej. wordlists/book_thematic.txt)
- Pregunta dificultad y tamaño de grid (igual para todo el libro)
- Valida el libro antes de renderizar
- Genera todos los grids antes de calcular paginación
- Genera imágenes (índice, instrucciones, portadas de bloque, puzzles y soluciones)
- Genera el PDF final con portada de soluciones incluida
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from wordsearch.constants_and_layout import BASE_OUTPUT_DIR
from wordsearch.difficulty_levels import DifficultyLevel, difficulty_settings
from wordsearch.grid_generation import place_words_on_grid
from wordsearch.grid_size_utils import ask_grid_size
from wordsearch.image_rendering import (
    render_block_cover,
    render_instructions_page,
    render_page,
    render_table_of_contents,
)
from wordsearch.pdf_book_generation import generate_pdf
from wordsearch.puzzle_parser import PuzzleParseError, PuzzleSpec, parse_puzzle_file
from wordsearch.text_normalization import normalize_words_for_grid
from wordsearch.thematic_validation import validate_thematic_specs
from wordsearch.wordlist_utils import slugify


@dataclass
class GeneratedPuzzle:
    """Puzzle data after validation and successful grid generation."""

    spec: PuzzleSpec
    words_for_grid: List[str]
    grid: Sequence[Sequence[str]]
    placed_words: Sequence[Tuple[str, Tuple[int, int, int, int]]]


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


def _generate_all_grids(
    specs: Sequence[PuzzleSpec],
    difficulty: DifficultyLevel,
    grid_size: int,
) -> List[GeneratedPuzzle] | None:
    """
    Generate every puzzle grid before rendering anything.

    This keeps page numbering reliable: if any puzzle cannot be generated, the
    process stops before creating partial PNG/PDF output with incorrect page
    references.
    """
    generated: List[GeneratedPuzzle] = []
    failures: List[str] = []

    print("\n=== Generando grids ===")
    for spec in specs:
        words_for_grid = normalize_words_for_grid(spec.words)
        placed_result = place_words_on_grid(
            words_for_grid,
            difficulty=difficulty,
            grid_size=grid_size,
        )

        if placed_result is None:
            failures.append(
                f"Puzzle {spec.index + 1} - {spec.title}: no se pudo colocar "
                f"{len(words_for_grid)} palabra(s) en un grid {grid_size}x{grid_size}."
            )
            continue

        grid, placed_words = placed_result
        generated.append(
            GeneratedPuzzle(
                spec=spec,
                words_for_grid=words_for_grid,
                grid=grid,
                placed_words=placed_words,
            )
        )

    if failures:
        print("\nERROR: uno o más puzzles no se pudieron generar.")
        print("No se generará el PDF para evitar índice y soluciones con páginas incorrectas.\n")
        for failure in failures:
            print(f"- {failure}")
        print("\nPrueba a aumentar el grid, subir la dificultad o reducir palabras en esos puzzles.")
        return None

    print(f"OK: {len(generated)} grids generados correctamente.")
    return generated


def _build_page_plan(
    generated_puzzles: Sequence[GeneratedPuzzle],
) -> Tuple[Dict[str, int], List[str], Dict[int, int], int]:
    """
    Calculate page numbers after all puzzles are known to be viable.

    Current front matter convention:
    - page 1: table of contents
    - page 2: instructions
    - page 3+: block covers and puzzles
    - after puzzles: solutions cover + solution pages
    """
    block_first_page: Dict[str, int] = {}
    blocks_in_order: List[str] = []
    puzzle_page: Dict[int, int] = {}

    current_page = 3
    current_block_name = ""

    for generated in generated_puzzles:
        spec = generated.spec
        block_name = getattr(spec, "block_name", "") or ""

        if block_name and block_name != current_block_name:
            current_block_name = block_name
            if block_name not in block_first_page:
                block_first_page[block_name] = current_page
                blocks_in_order.append(block_name)
                current_page += 1

        puzzle_page[spec.index] = current_page
        current_page += 1

    last_puzzle_page = current_page - 1
    pages_before_first_solution = last_puzzle_page + 2

    return block_first_page, blocks_in_order, puzzle_page, pages_before_first_solution


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

    # --------------------------------------------------------------
    # Validación previa: si hay errores, paramos antes de renderizar.
    # --------------------------------------------------------------
    validation_report = validate_thematic_specs(specs, grid_size)
    validation_report.print_summary()
    if validation_report.has_errors:
        print("\nCorrige los errores anteriores y vuelve a ejecutar el generador.")
        return

    # --------------------------------------------------------------
    # Generar todos los grids antes de calcular páginas/renderizar.
    # --------------------------------------------------------------
    generated_puzzles = _generate_all_grids(specs, difficulty, grid_size)
    if generated_puzzles is None:
        return

    # Directorio de salida
    output_dir = os.path.join(BASE_OUTPUT_DIR, slugify(book_title))
    os.makedirs(output_dir, exist_ok=True)

    (
        block_first_page,
        blocks_in_order,
        puzzle_page,
        pages_before_first_solution,
    ) = _build_page_plan(generated_puzzles)

    # ------------------------------------------------------------------
    # Construir entradas del índice: portadas de bloque + soluciones.
    # ------------------------------------------------------------------
    toc_entries: List[Tuple[str, int, bool]] = []
    for block_name in blocks_in_order:
        toc_entries.append((block_name, block_first_page.get(block_name, 1), True))
    toc_entries.append(("Solutions", pages_before_first_solution, True))

    content_imgs: List[str] = []
    solution_imgs: List[str] = []

    # ------------------------------------------------------------------
    # 1) Página de índice
    # ------------------------------------------------------------------
    toc_imgs = render_table_of_contents(
        toc_entries,
        output_dir=output_dir,
        background_path=None,
    )
    content_imgs.extend(toc_imgs)

    # ------------------------------------------------------------------
    # 2) Página de instrucciones
    # ------------------------------------------------------------------
    instr_filename = os.path.join(output_dir, "00_instructions.png")
    instr_img = render_instructions_page(
        book_title,
        filename=instr_filename,
        background_path=None,
    )
    content_imgs.append(instr_img)

    # ------------------------------------------------------------------
    # 3) Portadas de bloque + puzzles y soluciones
    # ------------------------------------------------------------------
    current_block_name = ""
    block_index = 0

    for generated in generated_puzzles:
        spec = generated.spec
        print(f"Renderizando puzzle {spec.index + 1}/{total_puzzles}: {spec.title}")

        block_name = getattr(spec, "block_name", "") or ""
        bg_path = getattr(spec, "block_background", None)

        if block_name and block_name != current_block_name:
            current_block_name = block_name
            block_index += 1
            block_cover_filename = os.path.join(
                output_dir,
                f"block_{block_index:02d}_{slugify(block_name)}.png",
            )

            cover_img = render_block_cover(
                block_name=block_name,
                block_index=block_index,
                filename=block_cover_filename,
                background_path=bg_path,
            )
            content_imgs.append(cover_img)

        solution_page_number = pages_before_first_solution + spec.index

        puzzle_filename = os.path.join(output_dir, f"puzzle_{spec.index + 1}.png")
        solution_filename = os.path.join(output_dir, f"puzzle_{spec.index + 1}_sol.png")

        img_puzzle = render_page(
            generated.grid,
            spec.words,
            spec.index + 1,
            is_solution=False,
            filename=puzzle_filename,
            placed_words=generated.placed_words,
            puzzle_title=spec.title,
            fun_fact=spec.fact,
            solution_page_number=solution_page_number,
            background_path=bg_path,
        )

        img_solution = render_page(
            generated.grid,
            spec.words,
            spec.index + 1,
            is_solution=True,
            filename=solution_filename,
            placed_words=generated.placed_words,
            puzzle_title=spec.title,
            background_path=bg_path,
        )

        content_imgs.append(img_puzzle)
        solution_imgs.append(img_solution)

    if not content_imgs or not solution_imgs:
        print("No se han generado imágenes suficientes como para crear el PDF.")
        return

    pdf_name = f"{slugify(book_title)}.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    pdf_final = generate_pdf(content_imgs, solution_imgs, outname=pdf_path)
    print("\nPDF generado:", pdf_final)


if __name__ == "__main__":
    main()
