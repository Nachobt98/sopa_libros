"""Backward-compatible imports for word list utilities."""

from wordsearch.cli.wordlist_prompts import prompt_wordlists
from wordsearch.io.wordlists import load_wordlists_from_txt
from wordsearch.utils.slug import slugify
from wordsearch.validation.simple_wordlists import validate_wordlists_for_grid

__all__ = [
    "load_wordlists_from_txt",
    "prompt_wordlists",
    "slugify",
    "validate_wordlists_for_grid",
]
