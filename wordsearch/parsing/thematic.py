"""Parser for thematic book files with [Puzzle] and optional [Block] sections."""

from __future__ import annotations

from wordsearch.domain.puzzle import PuzzleSpec


class PuzzleParseError(Exception):
    """Raised when a thematic puzzle input file is malformed."""


def parse_puzzle_file(path: str) -> list[PuzzleSpec]:
    """
    Return parsed puzzle specs from a thematic text file.

    Supports the classic [Puzzle] ... [/Puzzle] format and optional [Block]
    sections that provide inherited block metadata for subsequent puzzles.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    specs: list[PuzzleSpec] = []

    current_block_name: str | None = None
    current_block_background: str | None = None
    puzzle_index = 0
    block_index = 0

    i = 0
    line_count = len(lines)

    while i < line_count:
        stripped = lines[i].strip()

        if stripped == "[Block]":
            start = i + 1
            end = start
            while end < line_count and lines[end].strip() != "[/Block]":
                end += 1
            if end >= line_count:
                raise PuzzleParseError("Falta '[/Block]' de cierre para un bloque [Block].")

            block_lines = lines[start:end]
            current_block_name, current_block_background = _parse_block_block(
                block_lines,
                block_index,
            )
            block_index += 1
            i = end + 1
            continue

        if stripped == "[Puzzle]":
            start = i + 1
            end = start
            while end < line_count and lines[end].strip() != "[/Puzzle]":
                end += 1
            if end >= line_count:
                raise PuzzleParseError("Falta '[/Puzzle]' de cierre para un bloque [Puzzle].")

            puzzle_lines = lines[start:end]
            spec = _parse_single_block(puzzle_lines, puzzle_index)
            spec.block_name = current_block_name
            spec.block_background = current_block_background

            specs.append(spec)
            puzzle_index += 1
            i = end + 1
            continue

        i += 1

    return specs


def _parse_block_block(block_lines: list[str], index: int) -> tuple[str, str | None]:
    """Parse one [Block] ... [/Block] section."""
    name: str | None = None
    background: str | None = None

    for raw in block_lines:
        line = raw.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        elif lower.startswith("background:"):
            background = line.split(":", 1)[1].strip()

    if not name:
        name = f"Block {index}"

    return name, background


def _parse_single_block(block_lines: list[str], index: int) -> PuzzleSpec:
    title = None
    fact = None
    words: list[str] = []

    mode = "header"
    for raw in block_lines:
        line = raw.strip()
        if not line:
            continue

        lower = line.lower()

        if mode == "header":
            if lower.startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif lower.startswith("fact:"):
                fact = line.split(":", 1)[1].strip()
            elif lower.startswith("words:"):
                mode = "words"
        else:
            words.append(line)

    if not title:
        raise PuzzleParseError(f"Puzzle {index}: falta 'title:'")
    if not fact:
        raise PuzzleParseError(f"Puzzle {index}: falta 'fact:'")
    if not words:
        raise PuzzleParseError(f"Puzzle {index}: no se han definido palabras tras 'words:'")

    seen = set()
    clean_words: list[str] = []
    for word in words:
        if word not in seen:
            seen.add(word)
            clean_words.append(word)

    return PuzzleSpec(index=index, title=title.strip(), fact=fact.strip(), words=clean_words)
