"""Backward-compatible imports for grid generation."""

from wordsearch.generation.grid import (
    DEFAULT_MAX_ATTEMPTS,
    generate_word_search_grid,
    place_words_on_grid,
)

__all__ = [
    "DEFAULT_MAX_ATTEMPTS",
    "generate_word_search_grid",
    "place_words_on_grid",
]
