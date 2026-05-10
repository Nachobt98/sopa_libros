"""Top-level orchestration for thematic book generation."""

from __future__ import annotations

import inspect
import shutil
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from wordsearch.cli.ui import (
    create_progress,
    print_completion_animation,
    print_completion_panel,
    print_error,
    print_info,
    print_key_value_table,
    print_section,
    print_success,
    print_warning,
)
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

MIN_PREFLIGHT_PROGRESS_SECONDS = 4.0


def print_run_summary(options: ThematicGenerationOptions) -> None:
    print_section("Generation parameters")
    print_info(f"Title: {options.book_title}")
    print_info(f"Input file: {options.puzzles_txt_path}")
    print_info(f"Difficulty: {options.difficulty.name}")
    print_info(f"Grid: {options.grid_size}x{options.grid_size}")
    print_info(f"Theme: {options.theme_name}")
    print_info(f"Format: {options.format_name}")
    if options.seed is not None:
        print_info(f"Seed: {options.seed}")
    if options.output_dir:
        print_info(f"Output dir: {options.output_dir}")
    if options.limit is not None:
        print_info(f"Puzzle limit: {options.limit}")
    if options.preview:
        print_info("Mode: preview")
    if options.validate_only:
        print_info("Mode: validate-only")
    if options.clean_output:
        print_info("Clean output: enabled")


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


def _accepts_keyword(func: Callable[..., Any], keyword: str) -> bool:
    """Return whether a callable accepts the given keyword argument."""
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return True
    return any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD or name == keyword
        for name, parameter in signature.parameters.items()
    )


def _generate_thematic_grids_with_optional_progress(
    specs: list[PuzzleSpec],
    options: ThematicGenerationOptions,
    *,
    progress_callback: Callable[[], None],
):
    kwargs: dict[str, Any] = {"seed": options.seed}
    if _accepts_keyword(generate_thematic_grids, "progress_callback"):
        kwargs["progress_callback"] = progress_callback
    return generate_thematic_grids(
        specs,
        options.difficulty,
        options.grid_size,
        **kwargs,
    )


def _render_thematic_book_images_with_optional_progress(
    render_kwargs: dict[str, Any],
    *,
    progress_callback: Callable[[], None],
):
    kwargs = dict(render_kwargs)
    if _accepts_keyword(render_thematic_book_images, "progress_callback"):
        kwargs["progress_callback"] = progress_callback
    return render_thematic_book_images(**kwargs)


def _build_generation_report_with_optional_render_quality(
    *,
    options: ThematicGenerationOptions,
    output_dir: str,
    pdf_path: str,
    page_plan,
    rendered_images,
    puzzle_count: int,
    render_quality_report,
):
    kwargs: dict[str, Any] = {
        "options": options,
        "output_dir": output_dir,
        "pdf_path": pdf_path,
        "page_plan": page_plan,
        "rendered_images": rendered_images,
        "puzzle_count": puzzle_count,
    }
    if _accepts_keyword(build_thematic_generation_report, "render_quality_report"):
        kwargs["render_quality_report"] = render_quality_report
    return build_thematic_generation_report(**kwargs)


def _print_grid_failures(failures: list[str]) -> None:
    print_error("One or more puzzles could not be generated.")
    print_warning("PDF creation was stopped to avoid incorrect TOC or solution page numbers.")
    for failure in failures:
        print_error(failure)
    print_info("Try increasing the grid size, using a harder difficulty, or reducing words in those puzzles.")


def _clean_output_dir(output_dir: str) -> bool:
    output_path = Path(output_dir)
    if not output_path.exists():
        print_info(f"Clean output: output folder does not exist yet: {output_path}")
        return True
    if not output_path.is_dir():
        print_error(f"Output path exists but is not a directory: {output_path}")
        return False
    try:
        shutil.rmtree(output_path)
    except OSError as exc:
        print_error(f"Could not clean output folder ({exc}): {output_path}")
        return False
    print_success(f"Clean output: removed output folder: {output_path}")
    return True


def _print_preflight_report_summary(preflight_report) -> None:
    errors = list(getattr(preflight_report, "errors", []) or [])
    warnings = list(getattr(preflight_report, "warnings", []) or [])
    issues = list(getattr(preflight_report, "issues", [*errors, *warnings]) or [])
    passed = bool(getattr(preflight_report, "passed", not errors))
    status = "PASSED" if passed else "FAILED"
    expected_page_count = getattr(preflight_report, "expected_page_count", "?")
    actual_page_count = getattr(preflight_report, "actual_page_count", None) or "?"
    trim_width = getattr(preflight_report, "trim_width_in", "?")
    trim_height = getattr(preflight_report, "trim_height_in", "?")
    dpi = getattr(preflight_report, "dpi", "?")
    format_name = getattr(preflight_report, "format_name", "?")

    print_key_value_table(
        "Preflight summary",
        [
            ("Status", status),
            ("Format", str(format_name)),
            ("Trim", f"{trim_width}x{trim_height} in @ {dpi} DPI"),
            ("Pages", f"{actual_page_count} / expected {expected_page_count}"),
            ("Errors", str(len(errors))),
            ("Warnings", str(len(warnings))),
        ],
    )
    if errors:
        for issue in errors:
            formatter = getattr(issue, "format", None)
            print_error(formatter() if callable(formatter) else str(issue))
    if warnings:
        for issue in warnings:
            formatter = getattr(issue, "format", None)
            print_warning(formatter() if callable(formatter) else str(issue))
    if not issues:
        print_success("No basic KDP preflight issues detected")


def generate_thematic_book(options: ThematicGenerationOptions) -> str | None:
    print_run_summary(options)
    theme = get_theme(options.theme_name)
    layout = get_format_preset(options.format_name).to_layout_config()
    format_kwargs = _format_kwargs(options, layout)

    print_section("Parsing")
    try:
        specs = parse_puzzle_file(options.puzzles_txt_path)
    except FileNotFoundError:
        print_error(f"Input file not found: {options.puzzles_txt_path}")
        return None
    except PuzzleParseError as exc:
        print_error(f"Parse error: {exc}")
        return None

    if not specs:
        print_error("No [Puzzle] blocks were found in the input file.")
        return None

    parsed_count = len(specs)
    specs = _apply_preview_limit(specs, options.limit)
    print_success(f"Loaded {parsed_count} puzzles from input file")
    if options.limit is not None:
        print_info(f"Preview/limit active: {len(specs)} puzzles will be generated")
    if not specs:
        print_error("No puzzles remain after applying the generation limit.")
        return None

    book_slug = slugify(options.book_title)
    output_dir = _resolve_output_dir(options, book_slug)
    if options.clean_output and not _clean_output_dir(output_dir):
        return None

    print_section("Validation")
    asset_report = validate_generation_assets(output_dir=output_dir, optional_backgrounds=(spec.block_background for spec in specs))
    asset_report.print_summary()
    if asset_report.has_errors:
        print_error("Fix the asset errors above and run the generator again.")
        return None
    print_success("Assets validated")

    validation_report = validate_thematic_specs(specs, options.grid_size, check_background_files=False)
    validation_report.print_summary()
    if validation_report.has_errors:
        print_error("Fix the validation errors above and run the generator again.")
        return None
    print_success("Puzzle specs validated")
    if options.validate_only:
        print_success("Validation completed. No grids, images or PDF were generated.")
        return None

    print_section("Grid generation")
    with create_progress() as progress:
        task_id = progress.add_task("Generating grids", total=len(specs))
        grid_batch = _generate_thematic_grids_with_optional_progress(
            specs,
            options,
            progress_callback=lambda: progress.update(task_id, advance=1),
        )
        progress.update(task_id, completed=len(specs))
    if grid_batch.has_failures:
        _print_grid_failures(grid_batch.failures)
        return None

    generated_puzzles = grid_batch.generated_puzzles
    print_success(f"Generated {len(generated_puzzles)} grids")

    print_section("Rendering")
    page_plan = build_page_plan(generated_puzzles)
    render_kwargs = {
        "book_title": options.book_title,
        "generated_puzzles": generated_puzzles,
        "page_plan": page_plan,
        "output_dir": output_dir,
    }
    if options.theme_name != DEFAULT_THEME_NAME:
        render_kwargs["theme"] = theme
    render_kwargs.update(format_kwargs)
    with create_progress() as progress:
        task_id = progress.add_task("Rendering puzzle and solution pages", total=len(generated_puzzles))
        rendered_images = _render_thematic_book_images_with_optional_progress(
            render_kwargs,
            progress_callback=lambda: progress.update(task_id, advance=1),
        )
        progress.update(task_id, completed=len(generated_puzzles))
    if not rendered_images.is_complete:
        print_error("Not enough images were generated to create the PDF.")
        return None
    print_success(f"Rendered {len(rendered_images.content_imgs) + len(rendered_images.solution_imgs)} images")

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
        print_section("Visual regression")
        visual_report = build_visual_regression_report([*rendered_images.content_imgs, *rendered_images.solution_imgs])
        visual_regression_report_path = write_visual_regression_report(visual_report, output_dir=output_dir)
        print_success(f"Visual regression report generated: {visual_regression_report_path}")

    print_section("PDF assembly")
    pdf_path = build_output_file(output_dir, f"{book_slug}.pdf")
    pdf_metadata = build_pdf_metadata(options)
    try:
        with create_progress() as progress:
            task_id = progress.add_task("Building final PDF", total=1)
            pdf_final = generate_pdf(
                rendered_images.content_imgs,
                rendered_images.solution_imgs,
                outname=pdf_path,
                metadata=pdf_metadata,
                **format_kwargs,
            )
            progress.update(task_id, advance=1)
    except PermissionError:
        print_error("Could not save the PDF.")
        print_warning("Close the file if it is open in a PDF viewer/browser and try again.")
        print_info(f"Blocked path: {pdf_path}")
        return None
    print_success(f"PDF generated: {pdf_final}")

    print_section("Preflight and reports")
    with create_progress() as progress:
        preflight_start = time.monotonic()
        task_id = progress.add_task("Running preflight and writing reports", total=4)
        preflight_report = build_kdp_preflight_report(
            pdf_path=pdf_final,
            output_dir=output_dir,
            content_image_paths=rendered_images.content_imgs,
            solution_image_paths=rendered_images.solution_imgs,
            expected_pdf_metadata=pdf_metadata,
            **format_kwargs,
        )
        progress.update(task_id, advance=1)
        preflight_report_path = write_kdp_preflight_report(preflight_report, output_dir=output_dir)
        progress.update(task_id, advance=1)

        report = _build_generation_report_with_optional_render_quality(
            options=options,
            output_dir=output_dir,
            pdf_path=pdf_final,
            page_plan=page_plan,
            rendered_images=rendered_images,
            puzzle_count=len(generated_puzzles),
            render_quality_report=render_quality_report,
        )
        report_path = write_generation_report(report, output_dir=output_dir)
        progress.update(task_id, advance=1)

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
        review_summary_path = write_production_review_summary(review_summary, output_dir=output_dir)
        progress.update(task_id, advance=1)

        elapsed = time.monotonic() - preflight_start
        if progress.console.is_terminal and elapsed < MIN_PREFLIGHT_PROGRESS_SECONDS:
            time.sleep(MIN_PREFLIGHT_PROGRESS_SECONDS - elapsed)

    _print_preflight_report_summary(preflight_report)
    print_completion_panel(
        title="GENERATION COMPLETE",
        subtitle="All core production artifacts were created successfully.",
        pdf_path=pdf_final,
        report_path=report_path,
        preflight_report_path=preflight_report_path,
        review_summary_path=review_summary_path,
        recommendation=review_summary.recommendation,
    )
    print_completion_animation()
    return pdf_final
