"""
Thematic book generation pipeline.

This module owns the top-level orchestration after CLI options have been
resolved. Detailed grid batching and page rendering orchestration live in
dedicated generation modules.
"""

from __future__ import annotations

import os

from wordsearch.config.paths import BASE_OUTPUT_DIR
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.generation.book_assembly import render_thematic_book_images
from wordsearch.generation.grid_batch import generate_thematic_grids
from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file
from wordsearch.rendering.pdf import generate_pdf
from wordsearch.validation.assets import validate_generation_assets
from wordsearch.validation.thematic import validate_thematic_specs
from wordsearch.utils.slug import slugify


def print_run_summary(options: ThematicGenerationOptions) -> None:
    print("\n=== Parametros de generacion ===")
    print(f"Titulo: {options.book_title}")
    print(f"Archivo: {options.puzzles_txt_path}")
    print(f"Dificultad: {options.difficulty.name}")
    print(f"Grid: {options.grid_size}x{options.grid_size}")


def _print_grid_failures(failures: list[str]) -> None:
    print("\nERROR: uno o mas puzzles no se pudieron generar.")
    print("No se generara el PDF para evitar indice y soluciones con paginas incorrectas.\n")
    for failure in failures:
        print(f"- {failure}")
    print("\nPrueba a aumentar el grid, subir la dificultad o reducir palabras en esos puzzles.")


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
    except PuzzleParseError as exc:
        print(f"ERROR de parseo: {exc}")
        return None

    if not specs:
        print("No se ha encontrado ningun bloque [Puzzle] en el fichero.")
        return None

    print(f"\nSe han cargado {len(specs)} puzzles del fichero.")

    output_dir = os.path.join(BASE_OUTPUT_DIR, slugify(options.book_title))
    asset_report = validate_generation_assets(
        output_dir=output_dir,
        optional_backgrounds=(spec.block_background for spec in specs),
    )
    asset_report.print_summary()
    if asset_report.has_errors:
        print("\nCorrige los errores de assets anteriores y vuelve a ejecutar el generador.")
        return None

    validation_report = validate_thematic_specs(
        specs,
        options.grid_size,
        check_background_files=False,
    )
    validation_report.print_summary()
    if validation_report.has_errors:
        print("\nCorrige los errores anteriores y vuelve a ejecutar el generador.")
        return None

    print("\n=== Generando grids ===")
    grid_batch = generate_thematic_grids(specs, options.difficulty, options.grid_size)
    if grid_batch.has_failures:
        _print_grid_failures(grid_batch.failures)
        return None

    generated_puzzles = grid_batch.generated_puzzles
    print(f"OK: {len(generated_puzzles)} grids generados correctamente.")

    page_plan = build_page_plan(generated_puzzles)
    rendered_images = render_thematic_book_images(
        book_title=options.book_title,
        generated_puzzles=generated_puzzles,
        page_plan=page_plan,
        output_dir=output_dir,
    )

    if not rendered_images.is_complete:
        print("No se han generado imagenes suficientes como para crear el PDF.")
        return None

    pdf_name = f"{slugify(options.book_title)}.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    try:
        pdf_final = generate_pdf(
            rendered_images.content_imgs,
            rendered_images.solution_imgs,
            outname=pdf_path,
        )
    except PermissionError:
        print("\nERROR: No se pudo guardar el PDF.")
        print("Cierra el archivo si esta abierto en un visor PDF/navegador y vuelve a intentarlo.")
        print(f"Ruta bloqueada: {pdf_path}")
        return None

    print("\nPDF generado:", pdf_final)
    return pdf_final
