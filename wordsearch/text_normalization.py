"""
Utilities for normalizing puzzle words consistently across the project.

A word search needs two different representations of the same word:

- display text: what the reader sees in the word list, preserving spaces and style.
- grid text: what is actually placed inside the letter grid.

This module centralizes the grid normalization so validation, generation and future
features use the same rules.
"""

from __future__ import annotations

import unicodedata
from typing import Iterable, List


def strip_accents(text: str) -> str:
    """
    Remove accents/diacritics from a string while preserving base letters.

    Examples:
        "Atlántico" -> "Atlantico"
        "Ge'ez" -> "Ge'ez"
    """
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_word_for_grid(word: str) -> str:
    """
    Convert a display word/phrase into the text that should be placed in the grid.

    Rules:
    - convert to uppercase;
    - remove accents;
    - keep alphabetic characters only;
    - remove spaces, punctuation, apostrophes, hyphens and numbers.

    Examples:
        "Garrett Morgan" -> "GARRETTMORGAN"
        "Traffic Light" -> "TRAFFICLIGHT"
        "Ge'ez" -> "GEEZ"
        "atlántico" -> "ATLANTICO"
        "Act 1965" -> "ACT"
    """
    if word is None:
        return ""

    without_accents = strip_accents(str(word))
    return "".join(ch for ch in without_accents.upper() if ch.isalpha())


def normalize_words_for_grid(words: Iterable[str]) -> List[str]:
    """
    Normalize a collection of display words for grid placement.
    """
    return [normalize_word_for_grid(word) for word in words]
