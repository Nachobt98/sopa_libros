"""Simple word-list book generation pipeline."""

from __future__ import annotations

from secrets import SystemRandom

from wordsearch.cli.ui import print_error, print_info, print_section, print_success, print_warning, track_progress
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
    print_error("Words were found that do not fit in the selected grid.")
    print_info(f"Grid size: {grid_size}x{grid_size}")
    print_info("Review these words in your lists, or increase the grid size:")

    by_list = {}
    for problem in problems:
        by_list.setdefault(problem["list_index"], []).append(problem)

    for list_index, items in by_list.items():
        print_warning(f"List #{list_index + 1}")
        for problem in items:
            print_error(
                f"'{problem['word']}' (clean: '{problem['clean_word']}') "
                f"has length {problem['length']} > {grid_size}"
            )

    print_info("Fix the word source or grid size and run the script again.")


def generate_simple_book(options: SimpleGenerationOptions) -> str | None:
    """
    Generate a simple word-search book from already-resolved options.

    Returns the generated PDF path on success. Returns None when validation,
    grid generation or PDF writing fails.
    """
    slug = slugify(options.book_title)
    output_dir = build_book_output_dir(slug, BASE_OUTPUT_DIR)
    print_section("Output")
    print_info(f"Files will be saved in: {output_dir}")

    print_section("Validation")
    asset_report = validate_generation_assets(output_dir=output_dir)
    asset_report.print_summary()
    if asset_report.has_errors:
        print_error("Fix the asset errors above and run the generator again.")
        return None
    print_success("Assets validated")

    problems = validate_wordlists_for_grid(
        options.wordlists,
        options.grid_size,
        remove_spaces=True,
    )
    if problems:
        _print_validation_errors(problems, options.grid_size)
        return None
    print_success("Word lists validated")

    puzzles = []
    solutions = []

    print_section("Puzzle generation")
    for puzzle_number in track_progress(
        range(1, options.total_puzzles + 1),
        description="Generating puzzle and solution pages",
        total=options.total_puzzles,
    ):
        words = list(options.wordlists[(puzzle_number - 1) % len(options.wordlists)])
        _WORD_SHUFFLER.shuffle(words)

        grid_result = generate_word_search_grid(
            words,
            difficulty=options.difficulty,
            grid_size=options.grid_size,
            max_attempts=DEFAULT_MAX_GRID_ATTEMPTS,
        )
        if isinstance(grid_result, GridGenerationFailure):
            print_warning(
                f"Puzzle #{puzzle_number}: no valid grid could be generated "
                f"after {DEFAULT_MAX_GRID_ATTEMPTS} attempts."
            )
            print_info("The word list is probably too dense for this grid size.")
            print_info("Adjust the list or grid size and try again.")
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
    print_success(f"Generated {len(puzzles)} puzzles and {len(solutions)} solution pages")

    print_section("PDF assembly")
    pdf_path = build_output_file(output_dir, f"{slug}.pdf")
    try:
        pdf_final = generate_pdf(puzzles, solutions, outname=pdf_path)
    except PermissionError:
        print_error("Could not save the PDF.")
        print_warning("Close the file if it is open in a PDF viewer/browser and try again.")
        print_info(f"Blocked path: {pdf_path}")
        return None

    print_success(f"PDF generated: {pdf_final}")
    return pdf_final
