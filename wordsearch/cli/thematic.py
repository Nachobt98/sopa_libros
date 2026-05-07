"""
CLI entry point for the thematic KDP word search generator.

This module owns command-line parsing and interactive prompts. The generation
pipeline itself lives in `wordsearch.generation.thematic_pipeline`.
"""

from __future__ import annotations

import argparse

from wordsearch.cli.grid_size_prompts import ask_grid_size
from wordsearch.config.paths import DEFAULT_THEMATIC_WORDLIST
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.generation.difficulty import DifficultyLevel, difficulty_settings
from wordsearch.generation.thematic_pipeline import generate_thematic_book


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a thematic KDP word search book from a [Block]/[Puzzle] text file.",
    )
    parser.add_argument(
        "--title",
        "-t",
        help="Book title. If omitted, the script asks interactively.",
    )
    parser.add_argument(
        "--input",
        "-i",
        dest="input_path",
        help="Path to the thematic TXT file. Example: wordlists/book_block.txt",
    )
    parser.add_argument(
        "--difficulty",
        "-d",
        choices=("easy", "medium", "hard"),
        help="Difficulty level. If omitted, the script asks interactively.",
    )
    parser.add_argument(
        "--grid-size",
        "-g",
        type=int,
        help="Grid size. If omitted, the script asks interactively.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed for reproducible grids.",
    )
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
    book_title = (args.title or "").strip()
    if not book_title:
        book_title = input("Título del libro (p.ej. 'Black Culture Word Search Vol. 1'): ").strip()
    if not book_title:
        book_title = "Wordsearch Thematic Book"

    puzzles_txt_path = (args.input_path or "").strip()
    if not puzzles_txt_path:
        puzzles_txt_path = input(
            "Ruta del TXT con los puzzles temáticos "
            "[por defecto wordlists/book_thematic.txt]: "
        ).strip()
    if not puzzles_txt_path:
        puzzles_txt_path = DEFAULT_THEMATIC_WORDLIST

    if args.difficulty:
        difficulty = _difficulty_from_cli(args.difficulty)
    else:
        difficulty = _ask_difficulty()

    settings = difficulty_settings[difficulty]
    if args.grid_size is not None:
        if args.grid_size <= 0:
            raise ValueError("--grid-size debe ser un entero positivo.")
        grid_size = args.grid_size
    else:
        grid_size = ask_grid_size(settings)

    return ThematicGenerationOptions(
        book_title=book_title,
        puzzles_txt_path=puzzles_txt_path,
        difficulty=difficulty,
        grid_size=grid_size,
        seed=args.seed,
    )


def main() -> None:
    print("=== Generador TEMÁTICO de Wordsearch para KDP ===")

    try:
        options = _resolve_options(_parse_args())
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return

    generate_thematic_book(options)


if __name__ == "__main__":
    main()
