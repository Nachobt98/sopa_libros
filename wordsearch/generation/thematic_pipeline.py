"""
Thematic book generation pipeline.

This module owns the orchestration after CLI options have been resolved:
parse input, validate, generate grids, build the page plan, render images and
export the final PDF.
"""

from __future__ import annotations

import os
from typing import List, Sequence, Tuple

from wordsearch.constants_and_layout import BASE_OUTPUT_DIR
from wordsearch.difficulty_levels import DifficultyLevel
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.grid_generation import place_words_on_grid
from wordsearch.image_rendering import render_page
from wordsearch.puzzle_parser import PuzzleParseError, PuzzleSpec, parse_puzzle_file
from wordsearch.rendering.block_cover import render_block_cover
from wordsearch.rendering.front_matter import render_instructions_page, render_table_of_contents
from wordsearch.rendering.pdf import generate_pdf
from wordsearch.rendering.title_page import render_title_page
from wordsearch.text_normalization import normalize_words_for_grid
from wordsearch.thematic_validation import validate_thematic_specs
from wordsearch.wordlist_utils import slugify


def print_run_summary(options: ThematicGenerationOptions) -> None:
    print("\n=== Parámetros de generación ===")
    print(f"Título: {options.book_title}")
    print(f"Archivo: {options.puzzles_txt_path}")
    print(f"Dificultad: {options.difficulty.name}")
    print(f"Grid: {options.grid_size}x{options.grid_size}")


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


def generate_thematic_book(options: ThematicGenerationOptions) -> str | None:
    """
    Generate the complete thematic book.

    Returns the generated PDF path on success. Returns None when generation is
    intentionally stopped because of parse, validation, grid-generation or file
    writing errors.
    """
    print_run_summary(options)

    try:
        specs = parse_puzzle_file(options.puzzles_txt_path)
    except FileNotFoundError:
        print(f"ERROR: No se encuentra el fichero: {options.puzzles_txt_path}")
        return None
    except PuzzleParseError as e:
        print(f"ERROR de parseo: {e}")
        return None

    total_puzzles = len(specs)
    if total_puzzles == 0:
        print("No se ha encontrado ningún bloque [Puzzle] en el fichero.")
        return None

    print(f"\nSe han cargado {total_puzzles} puzzles del fichero.")

    # --------------------------------------------------------------
    # Validación previa: si hay errores, paramos antes de renderizar.
    # --------------------------------------------------------------
    validation_report = validate_thematic_specs(specs, options.grid_size)
    validation_report.print_summary()
    if validation_report.has_errors:
        print("\nCorrige los errores anteriores y vuelve a ejecutar el generador.")
        return None

    # --------------------------------------------------------------
    # Generar todos los grids antes de calcular páginas/renderizar.
    # --------------------------------------------------------------
    generated_puzzles = _generate_all_grids(specs, options.difficulty, options.grid_size)
    if generated_puzzles is None:
        return None

    # Directorio de salida
    output_dir = os.path.join(BASE_OUTPUT_DIR, slugify(options.book_title))
    os.makedirs(output_dir, exist_ok=True)

    page_plan = build_page_plan(generated_puzzles)

    # ------------------------------------------------------------------
    # Construir entradas del índice: portadas de bloque + soluciones.
    # ------------------------------------------------------------------
    toc_entries: List[Tuple[str, int, bool]] = []
    for block_name in page_plan.blocks_in_order:
        toc_entries.append((block_name, page_plan.block_first_page.get(block_name, 1), True))
    toc_entries.append(("Solutions", page_plan.first_solution_page, True))

    content_imgs: List[str] = []
    solution_imgs: List[str] = []

    # ------------------------------------------------------------------
    # 1) Portada interior del libro
    # ------------------------------------------------------------------
    title_page_filename = os.path.join(output_dir, "00_title_page.png")
    title_page_img = render_title_page(
        options.book_title,
        filename=title_page_filename,
        background_path=None,
    )
    content_imgs.append(title_page_img)

    # ------------------------------------------------------------------
    # 2) Página de índice
    # ------------------------------------------------------------------
    toc_imgs = render_table_of_contents(
        toc_entries,
        output_dir=output_dir,
        background_path=None,
    )
    content_imgs.extend(toc_imgs)

    # ------------------------------------------------------------------
    # 3) Página de instrucciones
    # ------------------------------------------------------------------
    instr_filename = os.path.join(output_dir, "02_instructions.png")
    instr_img = render_instructions_page(
        options.book_title,
        filename=instr_filename,
        background_path=None,
    )
    content_imgs.append(instr_img)

    # ------------------------------------------------------------------
    # 4) Portadas de bloque + puzzles y soluciones
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

        solution_page_number = page_plan.first_solution_page + spec.index

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
        return None

    pdf_name = f"{slugify(options.book_title)}.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    try:
        pdf_final = generate_pdf(content_imgs, solution_imgs, outname=pdf_path)
    except PermissionError:
        print("\nERROR: No se pudo guardar el PDF.")
        print("Cierra el archivo si está abierto en un visor PDF/navegador y vuelve a intentarlo.")
        print(f"Ruta bloqueada: {pdf_path}")
        return None

    print("\nPDF generado:", pdf_final)
    return pdf_final
