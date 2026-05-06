"""Validation helpers for simple word list generation."""

from __future__ import annotations

from typing import Any


def validate_wordlists_for_grid(
    wordlists: list[list[str]],
    grid_size: int,
    remove_spaces: bool = True,
) -> list[dict[str, Any]]:
    """
    Report words that cannot fit inside a grid of size ``grid_size``.

    This function does not mutate the input word lists.
    """
    problems: list[dict[str, Any]] = []

    for list_index, wordlist in enumerate(wordlists):
        for word in wordlist:
            if not word:
                continue
            clean_word = word.strip()
            if remove_spaces:
                clean_word = clean_word.replace(" ", "")

            if not clean_word:
                continue

            if len(clean_word) > grid_size:
                problems.append(
                    {
                        "list_index": list_index,
                        "word": word,
                        "clean_word": clean_word,
                        "length": len(clean_word),
                    }
                )

    return problems
