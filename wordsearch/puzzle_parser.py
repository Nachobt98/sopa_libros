"""Backward-compatible imports for thematic puzzle parsing."""

from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file

__all__ = [
    "PuzzleParseError",
    "PuzzleSpec",
    "parse_puzzle_file",
]
