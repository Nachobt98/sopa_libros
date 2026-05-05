"""Backward-compatible wrapper for legacy rendering imports."""

from wordsearch.rendering.backgrounds import BACKGROUND_PATH
from wordsearch.rendering.block_cover import render_block_cover
from wordsearch.rendering.puzzle_page import render_page


__all__ = ["BACKGROUND_PATH", "render_block_cover", "render_page"]