"""Backward-compatible wrapper for front matter rendering."""

from wordsearch.rendering.front_matter import (
    render_instructions_page,
    render_table_of_contents,
)


__all__ = ["render_instructions_page", "render_table_of_contents"]
