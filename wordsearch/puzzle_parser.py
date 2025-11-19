"""
Parser para ficheros de libro temático con bloques [Puzzle] ... [/Puzzle].

Ejemplo de formato:

[Puzzle]
title: Black Inventors
fact: Garrett Morgan invented the traffic light and the gas mask.
words:
Garrett Morgan
Traffic Light
Gas Mask
Innovation
Patent
Safety Gear
[/Puzzle]
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PuzzleSpec:
    index: int
    title: str
    fact: str
    words: List[str]


class PuzzleParseError(Exception):
    pass


def parse_puzzle_file(path: str) -> List[PuzzleSpec]:
    """
    Devuelve una lista de PuzzleSpec a partir de un fichero de texto.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    puzzles_raw: List[List[str]] = []
    current_block: List[str] = []
    inside = False

    for line in lines:
        stripped = line.strip()

        if stripped == "[Puzzle]":
            if inside:
                raise PuzzleParseError("Se encontró '[Puzzle]' dentro de otro bloque.")
            inside = True
            current_block = []
            continue

        if stripped == "[/Puzzle]":
            if not inside:
                raise PuzzleParseError("Se encontró '[/Puzzle]' sin bloque abierto.")
            inside = False
            puzzles_raw.append(current_block)
            current_block = []
            continue

        if inside:
            current_block.append(line)

    if inside:
        raise PuzzleParseError("Falta '[/Puzzle]' de cierre al final del archivo.")

    specs: List[PuzzleSpec] = []
    for idx, block in enumerate(puzzles_raw):
        specs.append(_parse_single_block(block, idx))

    return specs


def _parse_single_block(block_lines: List[str], index: int) -> PuzzleSpec:
    title = None
    fact = None
    words: List[str] = []

    mode = "header"  # 'header' o 'words'
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

    # Quitar duplicados preservando orden
    seen = set()
    clean_words: List[str] = []
    for w in words:
        if w not in seen:
            seen.add(w)
            clean_words.append(w)

    return PuzzleSpec(index=index, title=title.strip(), fact=fact.strip(), words=clean_words)
