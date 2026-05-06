"""Interactive entry point for the simple word-search book generator."""

from __future__ import annotations

from wordsearch.cli.grid_size_prompts import ask_grid_size
from wordsearch.cli.wordlist_prompts import prompt_wordlists
from wordsearch.domain.book import SimpleGenerationOptions
from wordsearch.generation.difficulty import DifficultyLevel, difficulty_settings
from wordsearch.generation.simple_pipeline import generate_simple_book


def _ask_book_title() -> str:
    book_title = input("Título del libro (p.ej. 'Wordsearch Animals Vol 1'): ").strip()
    return book_title or "Wordsearch Book"


def _ask_difficulty() -> DifficultyLevel:
    print("\nNiveles de dificultad disponibles:")
    for index, level in enumerate(DifficultyLevel, 1):
        print(f"{index}) {difficulty_settings[level]['name']} ({level.value})")

    diff_choice = input("Elige dificultad [1/2/3, por defecto 1]: ").strip() or "1"
    try:
        return list(DifficultyLevel)[int(diff_choice) - 1]
    except (ValueError, IndexError):
        return DifficultyLevel.EASY


def _ask_total_puzzles(source_type: str, wordlist_count: int) -> int:
    if source_type == "txt":
        print(f"\nOrigen TXT detectado: se generarán {wordlist_count} sopas de letras (una por lista).")
        return wordlist_count

    default_total = 10
    while True:
        total_raw = input(f"\n¿Cuántos puzzles quieres generar? [por defecto {default_total}]: ").strip()
        if not total_raw:
            return default_total
        try:
            total = int(total_raw)
            if total <= 0:
                raise ValueError
            return total
        except ValueError:
            print("Introduce un número entero positivo, por favor.")


def main() -> None:
    book_title = _ask_book_title()
    difficulty = _ask_difficulty()
    grid_size = ask_grid_size(difficulty_settings[difficulty])

    predefined_wordlists = [
        ["gato", "perro", "casa", "luna", "sol", "arbol", "cielo", "mar"],
        ["python", "codigo", "amazon", "kdp", "libro", "puzzle", "print"],
    ]
    wordlists, source_type = prompt_wordlists(predefined_wordlists)
    total_puzzles = _ask_total_puzzles(source_type, len(wordlists))

    generate_simple_book(
        SimpleGenerationOptions(
            book_title=book_title,
            wordlists=wordlists,
            difficulty=difficulty,
            grid_size=grid_size,
            total_puzzles=total_puzzles,
        )
    )


if __name__ == "__main__":
    main()
