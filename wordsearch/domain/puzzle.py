"""Puzzle domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PuzzleSpec:
    """Parsed thematic puzzle data ready for validation and generation."""

    index: int
    title: str
    fact: str
    words: list[str]
    block_name: str | None = None
    block_background: str | None = None
