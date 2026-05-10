"""CLI entry point for the thematic KDP word search generator."""

from __future__ import annotations

import argparse

from wordsearch.cli.grid_size_prompts import ask_grid_size
from wordsearch.cli.ui import print_app_header, print_error, print_info, print_success
from wordsearch.config.design import DEFAULT_THEME_NAME, get_theme, theme_names
from wordsearch.config.formats import DEFAULT_FORMAT_NAME, format_names, get_format_preset
from wordsearch.config.paths import DEFAULT_THEMATIC_WORDLIST
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.generation.difficulty import DifficultyLevel, difficulty_settings
from wordsearch.generation.thematic_pipeline import generate_thematic_book

PREVIEW_DEFAULT_LIMIT = 5
PREVIEW_DEFAULT_SEED = 1234


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a thematic KDP word search book from a [Block]/[Puzzle] text file.")
    parser.add_argument("--title", "-t", help="Book title. If omitted, the script asks interactively.")
    parser.add_argument("--input", "-i", dest="input_path", help="Path to the thematic TXT file. Example: wordlists/book_block.txt")
    parser.add_argument("--difficulty", "-d", choices=("easy", "medium", "hard"), help="Difficulty level. If omitted, the script asks interactively.")
    parser.add_argument("--grid-size", "-g", type=int, help="Grid size. If omitted, the script asks interactively.")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible grids.")
    parser.add_argument("--theme", choices=theme_names(), default=DEFAULT_THEME_NAME, help="Visual theme preset for shared page-frame styling.")
    parser.add_argument("--format", choices=format_names(), default=DEFAULT_FORMAT_NAME, help="Editorial book format preset for trim size, margins and safe area.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to output_puzzles_kdp/<book_slug>.")
    parser.add_argument("--limit", type=int, help="Generate only the first N parsed puzzles. Useful for visual iteration.")
    parser.add_argument(
        "--preview",
        action="store_true",
        help=(
            "Preview mode: generate a small, reproducible subset. "
            f"Defaults to --limit {PREVIEW_DEFAULT_LIMIT} and --seed {PREVIEW_DEFAULT_SEED} when omitted."
        ),
    )
    parser.add_argument("--validate-only", action="store_true", help="Parse and validate the thematic input/assets without generating grids, images or PDF.")
    parser.add_argument("--clean-output", action="store_true", help="Remove the generated output folder for this book before creating new files.")
    return parser.parse_args()


def _difficulty_from_cli(value: str) -> DifficultyLevel:
    normalized = value.strip().lower()
    if normalized == "easy":
        return DifficultyLevel.EASY
    if normalized == "medium":
        return DifficultyLevel.MEDIUM
    if normalized == "hard":
        return DifficultyLevel.HARD
    raise ValueError(f"Dificultad no soportada: {value}")


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


def _resolve_options(args: argparse.Namespace) -> ThematicGenerationOptions:
    if args.validate_only and args.clean_output:
        raise ValueError("--clean-output no se puede combinar con --validate-only.")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit debe ser un entero positivo.")

    book_title = (args.title or "").strip()
    if not book_title:
        book_title = input("Título del libro (p.ej. 'Black Culture Word Search Vol. 1'): ").strip()
    if not book_title:
        book_title = "Wordsearch Thematic Book"

    puzzles_txt_path = (args.input_path or "").strip()
    if not puzzles_txt_path:
        puzzles_txt_path = input("Ruta del TXT con los puzzles temáticos [por defecto wordlists/book_thematic.txt]: ").strip()
    if not puzzles_txt_path:
        puzzles_txt_path = DEFAULT_THEMATIC_WORDLIST

    difficulty = _difficulty_from_cli(args.difficulty) if args.difficulty else _ask_difficulty()
    settings = difficulty_settings[difficulty]
    if args.grid_size is not None:
        if args.grid_size <= 0:
            raise ValueError("--grid-size debe ser un entero positivo.")
        grid_size = args.grid_size
    else:
        grid_size = ask_grid_size(settings)

    theme = get_theme(args.theme)
    book_format = get_format_preset(getattr(args, "format", DEFAULT_FORMAT_NAME))
    seed = args.seed
    limit = args.limit
    if args.preview:
        if seed is None:
            seed = PREVIEW_DEFAULT_SEED
        if limit is None:
            limit = PREVIEW_DEFAULT_LIMIT

    return ThematicGenerationOptions(
        book_title=book_title,
        puzzles_txt_path=puzzles_txt_path,
        difficulty=difficulty,
        grid_size=grid_size,
        seed=seed,
        validate_only=args.validate_only,
        clean_output=args.clean_output,
        theme_name=theme.name,
        format_name=book_format.name,
        output_dir=(args.output_dir or "").strip() or None,
        limit=limit,
        preview=args.preview,
    )


def _print_options_summary(options: ThematicGenerationOptions) -> None:
    print_info(f"Book title: {options.book_title}")
    print_info(f"Input file: {options.puzzles_txt_path}")
    print_info(f"Difficulty: {options.difficulty.value.upper()}")
    print_info(f"Grid size: {options.grid_size}")
    print_info(f"Theme: {options.theme_name}")
    print_info(f"Format: {options.format_name}")
    if options.seed is not None:
        print_info(f"Seed: {options.seed}")
    if options.limit is not None:
        print_info(f"Limit: {options.limit}")
    if options.validate_only:
        print_info("Mode: validate only")
    if options.clean_output:
        print_info("Clean output: enabled")


def main() -> None:
    print_app_header("Thematic KDP word search book generator")
    try:
        options = _resolve_options(_parse_args())
    except ValueError as exc:
        print_error(str(exc))
        return

    _print_options_summary(options)
    print_info("Starting thematic generation pipeline...")
    generate_thematic_book(options)
    print_success("Thematic generation finished")


if __name__ == "__main__":
    main()
