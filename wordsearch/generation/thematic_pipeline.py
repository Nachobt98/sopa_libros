"""Top-level orchestration for thematic book generation."""

from __future__ import annotations

import shutil
from pathlib import Path

from wordsearch.config.design import DEFAULT_THEME_NAME, get_theme
from wordsearch.config.formats import DEFAULT_FORMAT_NAME, get_format_preset
from wordsearch.config.paths import BASE_OUTPUT_DIR, build_book_output_dir, build_output_file
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.generation.book_assembly import render_thematic_book_images
from wordsearch.generation.grid_batch import generate_thematic_grids
from wordsearch.generation.reporting import build_thematic_generation_report, write_generation_report
from wordsearch.generation.review_summary import build_production_review_summary, write_production_review_summary
from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file
from wordsearch.rendering.pdf import generate_pdf
from wordsearch.validation.assets import validate_generation_assets
from wordsearch.validation.kdp import build_kdp_preflight_report, write_kdp_preflight_report
from wordsearch.validation.render_quality import build_render_quality_report
from wordsearch.validation.thematic import validate_thematic_specs
from wordsearch.validation.visual import build_visual_regression_report, write_visual_regression_report
from wordsearch.utils.slug import slugify


def print_run_summary(options: ThematicGenerationOptions) -> None:
    print("\n=== Parametros de generacion ===")
    print(f"Titulo: {options.book_title}")
    print(f"Archivo: {options.puzzles_txt_path}")
    print(f"Dificultad: {options.difficulty.name}")
    print(f"Grid: {options.grid_size}x{options.grid_size}")
    print(f"Tema: {options.theme_name}")
    print(f"Formato: {options.format_name}")
    if options.seed is not None:
        print(f"Seed: {options.seed}")
    if options.output_dir:
        print(f"Output dir: {options.output_dir}")
    if options.limit is not None:
        print(f"Limite de puzzles: {options.limit}")
    if options.preview:
        print("Modo: preview")
    if options.validate_only:
        print("Modo: validate-only")
    if options.clean_output:
        print("Modo: clean-output")


def build_pdf_metadata(options: ThematicGenerationOptions) -> dict[str, str]:
    return {
        "title": options.book_title,
        "author": "",
        "subject": f"Word search puzzle book generated with {options.difficulty.name} difficulty",
        "keywords": f"word search, puzzle book, KDP, {options.difficulty.name.lower()}, {options.theme_name}",
        "creator": "sopa-libros",
    }


def _resolve_output_dir(options: ThematicGenerationOptions, book_slug: str) -> str:
    return str(Path(options.output_dir)) if options.output_dir else build_book_output_dir(book_slug, BASE_OUTPUT_DIR)


def _apply_preview_limit(specs: list[PuzzleSpec], limit: int | None) -> list[PuzzleSpec]:
    return specs if limit is None else specs[:limit]


def _format_kwargs(options: ThematicGenerationOptions, layout) -> dict:
    return {"layout": layout} if options.format_name != DEFAULT_FORMAT_NAME else {}


def _print_grid_failures(failures: list[str]) -> None:
    print("\nERROR: uno o mas puzzles no se pudieron generar.")
    print("No se generara el PDF para evitar indice y soluciones con paginas incorrectas.\n")
    for failure in failures:
        print(f"- {failure}")
    print("\nPrueba a aumentar el grid, subir la dificultad o reducir palabras en esos puzzles.")


def _clean_output_dir(output_dir: str) -> bool:
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"\nClean output: no existe la carpeta de salida, no hay nada que limpiar: {output_path}")
        return True
    if not output_path.is_dir():
        print(f"\nERROR: la ruta de salida existe pero no es un directorio: {output_path}")
        return False
    try:
        shutil.rmtree(output_path)
    except OSError as exc:
        print(f"\nERROR: no se pudo limpiar la carpeta de salida ({exc}): {output_path}")
        return False
    print(f"\nClean output: carpeta de salida eliminada: {output_path}")
    return True


def generate_thematic_book(options: ThematicGenerationOptions) -> str | None:
    print_run_summary(options)
    theme = get_theme(options.theme_name)
    layout = get_format_preset(options.format_name).to_layout_config()
    format_kwargs = _format_kwargs(options, layout)

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

    parsed_count = len(specs)
    specs = _apply_preview_limit(specs, options.limit)
    print(f"\nSe han cargado {parsed_count} puzzles del fichero.")
    if options.limit is not None:
        print(f"Preview/limit activo: se generaran {len(specs)} puzzles.")
    if not specs:
        print("No queda ningun puzzle despues de aplicar el limite de generacion.")
        return None

    book_slug = slugify(options.book_title)
    output_dir = _resolve_output_dir(options, book_slug)
    if options.clean_output and not _clean_output_dir(output_dir):
        return None

    asset_report = validate_generation_assets(output_dir=output_dir, optional_backgrounds=(spec.block_background for spec in specs))
    asset_report.print_summary()
    if asset_report.has_errors:
        print("\nCorrige los errores de assets anteriores y vuelve a ejecutar el generador.")
        return None

    validation_report = validate_thematic_specs(specs, options.grid_size, check_background_files=False)
    validation_report.print_summary()
    if validation_report.has_errors:
        print("\nCorrige los errores anteriores y vuelve a ejecutar el generador.")
        return None
    if options.validate_only:
        print("\nOK: validacion completada. No se generaron grids, imagenes ni PDF.")
        return None

    print("\n=== Generando grids ===")
    grid_batch = generate_thematic_grids(specs, options.difficulty, options.grid_size, seed=options.seed)
    if grid_batch.has_failures:
        _print_grid_failures(grid_batch.failures)
        return None

    generated_puzzles = grid_batch.generated_puzzles
    print(f"OK: {len(generated_puzzles)} grids generados correctamente.")
    page_plan = build_page_plan(generated_puzzles)
    render_kwargs = {"book_title": options.book_title, "generated_puzzles": generated_puzzles, "page_plan": page_plan, "output_dir": output_dir}
    if options.theme_name != DEFAULT_THEME_NAME:
        render_kwargs["theme"] = theme
    render_kwargs.update(format_kwargs)
    rendered_images = render_thematic_book_images(**render_kwargs)
    if not rendered_images.is_complete:
        print("No se han generado imagenes suficientes como para crear el PDF.")
        return None

    render_quality_report = build_render_quality_report(
        book_title=options.book_title,
        generated_puzzles=generated_puzzles,
        page_plan=page_plan,
        content_image_paths=rendered_images.content_imgs,
        theme=theme,
    )
    render_quality_report.print_summary()

    visual_regression_report_path = None
    if options.preview:
        visual_report = build_visual_regression_report([*rendered_images.content_imgs, *rendered_images.solution_imgs])
        visual_regression_report_path = write_visual_regression_report(visual_report, output_dir=output_dir)

    pdf_path = build_output_file(output_dir, f"{book_slug}.pdf")
    pdf_metadata = build_pdf_metadata(options)
    try:
        pdf_final = generate_pdf(rendered_images.content_imgs, rendered_images.solution_imgs, outname=pdf_path, metadata=pdf_metadata, **format_kwargs)
    except PermissionError:
        print("\nERROR: No se pudo guardar el PDF.")
        print("Cierra el archivo si esta abierto en un visor PDF/navegador y vuelve a intentarlo.")
        print(f"Ruta bloqueada: {pdf_path}")
        return None

    preflight_report = build_kdp_preflight_report(
        pdf_path=pdf_final,
        output_dir=output_dir,
        content_image_paths=rendered_images.content_imgs,
        solution_image_paths=rendered_images.solution_imgs,
        expected_pdf_metadata=pdf_metadata,
        **format_kwargs,
    )
    preflight_report.print_summary()
    preflight_report_path = write_kdp_preflight_report(preflight_report, output_dir=output_dir)

    report = build_thematic_generation_report(
        options=options,
        output_dir=output_dir,
        pdf_path=pdf_final,
        page_plan=page_plan,
        rendered_images=rendered_images,
        puzzle_count=len(generated_puzzles),
        render_quality_report=render_quality_report,
    )
    report_path = write_generation_report(report, output_dir=output_dir)

    review_summary = build_production_review_summary(
        book_title=options.book_title,
        pdf_path=pdf_final,
        generation_report_path=report_path,
        preflight_report_path=preflight_report_path,
        preflight_report=preflight_report,
        render_quality_report=render_quality_report,
        puzzle_count=len(generated_puzzles),
        visual_regression_report_path=visual_regression_report_path,
    )
    review_summary.print_summary()
    review_summary_path = write_production_review_summary(review_summary, output_dir=output_dir)

    print("\nPDF generado:", pdf_final)
    print("Reporte generado:", report_path)
    print("Preflight generado:", preflight_report_path)
    print("Production review generado:", review_summary_path)
    if visual_regression_report_path:
        print("Visual regression generado:", visual_regression_report_path)
    return pdf_final
