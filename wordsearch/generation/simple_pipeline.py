"""Simple word-list book generation pipeline."""

from __future__ import annotations

from secrets import SystemRandom

from wordsearch.config.paths import BASE_OUTPUT_DIR, build_book_output_dir, build_output_file
from wordsearch.domain.book import SimpleGenerationOptions
from wordsearch.domain.grid import GridGenerationFailure
from wordsearch.generation.grid import generate_word_search_grid
from wordsearch.rendering.pdf import generate_pdf
from wordsearch.rendering.puzzle_page import render_page
from wordsearch.rendering.solution_page import render_solution_page
from wordsearch.utils.slug import slugify
from wordsearch.validation.assets import validate_generation_assets
from wordsearch.validation.simple_wordlists import validate_wordlists_for_grid

DEFAULT_MAX_GRID_ATTEMPTS = 10
_WORD_SHUFFLER = SystemRandom()


def _print_validation_errors(problems: list[dict], grid_size: int) -> None:
    print("\n[ERROR] Se han encontrado palabras que no caben en el grid seleccionado.")
    print(f"Tamaño del grid: {grid_size}x{grid_size}")
    print("Revisa y corrige estas palabras en tus listas (o aumenta el tamaño de grid):\n")

    by_list = {}
    for problem in problems:
        by_list.setdefault(problem["list_index"], []).append(problem)

    for list_index, items in by_list.items():
        print(f"  - Lista #{list_index + 1}:")
        for problem in items:
            print(
                f"      - '{problem['word']}' (limpia: '{problem['clean_word']}') "
                f"tiene longitud {problem['length']} > {grid_size}"
            )
        print()

    print("Corrige el archivo de palabras (o el tamaño de grid) y vuelve a ejecutar el script.")


def generate_simple_book(options: SimpleGenerationOptions) -> str | None:
    """
    Generate a simple word-search book from already-resolved options.

    Returns the generated PDF path on success. Returns None when validation,
    grid generation or PDF writing fails.
    """
    slug = slugify(options.book_title)
    output_dir = build_book_output_dir(slug, BASE_OUTPUT_DIR)
    print(f"\nLos archivos se guardarán en: {output_dir}")

    asset_report = validate_generation_assets(output_dir=output_dir)
    asset_report.print_summary()
    if asset_report.has_errors:
        print("\nCorrige los errores de assets anteriores y vuelve a ejecutar el generador.")
        return None

    problems = validate_wordlists_for_grid(
        options.wordlists,
        options.grid_size,
        remove_spaces=True,
    )
    if problems:
        _print_validation_errors(problems, options.grid_size)
        return None

    puzzles = []
    solutions = []

    for puzzle_number in range(1, options.total_puzzles + 1):
        words = list(options.wordlists[(puzzle_number - 1) % len(options.wordlists)])
        _WORD_SHUFFLER.shuffle(words)

        grid_result = generate_word_search_grid(
            words,
            difficulty=options.difficulty,
            grid_size=options.grid_size,
            max_attempts=DEFAULT_MAX_GRID_ATTEMPTS,
        )
        if isinstance(grid_result, GridGenerationFailure):
            print(
                f"[Aviso] Puzzle #{puzzle_number}: no se ha podido generar un grid válido "
                f"tras {DEFAULT_MAX_GRID_ATTEMPTS} intentos."
            )
            print("Probablemente hay demasiadas palabras o la lista es muy densa para este tamaño de grid.")
            print("Ajusta manualmente la lista o el tamaño y vuelve a intentarlo.")
            return None

        puzzle_img = render_page(
            grid_result.grid,
            words,
            puzzle_number,
            filename=build_output_file(output_dir, f"puzzle_{puzzle_number}.png"),
        )
        solution_img = render_solution_page(
            grid_result.grid,
            words,
            puzzle_number,
            filename=build_output_file(output_dir, f"puzzle_{puzzle_number}_sol.png"),
            placed_words=grid_result.placed_words,
        )
        puzzles.append(puzzle_img)
        solutions.append(solution_img)

    pdf_path = build_output_file(output_dir, f"{slug}.pdf")
    try:
        pdf_final = generate_pdf(puzzles, solutions, outname=pdf_path)
    except PermissionError:
        print("\nERROR: No se pudo guardar el PDF.")
        print("Cierra el archivo si está abierto en un visor PDF/navegador y vuelve a intentarlo.")
        print(f"Ruta bloqueada: {pdf_path}")
        return None

    print("\nPDF generado:", pdf_final)
    return pdf_final
