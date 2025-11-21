"""
Parser para ficheros de libro temático con bloques [Puzzle] ... [/Puzzle]
y, opcionalmente, bloques de sección [Block] ... [/Block].

Formato mínimo (compatible con la versión antigua):

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

Formato extendido con bloques temáticos:

[Block]
name: Black History
background: assets/bg_history.png
[/Block]

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

[Puzzle]
title: The Harlem Renaissance
fact: The Harlem Renaissance was a cultural movement in the 1920s...
words:
Harlem
Poetry
Jazz
...
[/Puzzle]

[Block]
name: Black Music & Rhythm
background: assets/bg_music.png
[/Block]

[Puzzle]
title: Jazz Legends
fact: Louis Armstrong helped popularize jazz around the world.
words:
Louis Armstrong
Duke Ellington
...
[/Puzzle]
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PuzzleSpec:
    index: int
    title: str
    fact: str
    words: List[str]
    # Metadatos opcionales de bloque temático
    block_name: Optional[str] = None
    block_background: Optional[str] = None


class PuzzleParseError(Exception):
    pass


def parse_puzzle_file(path: str) -> List[PuzzleSpec]:
    """
    Devuelve una lista de PuzzleSpec a partir de un fichero de texto.

    - Soporta el formato clásico únicamente con [Puzzle] ... [/Puzzle]
    - Opcionalmente soporta bloques [Block] ... [/Block] para definir secciones:
      name: Nombre del bloque
      background: Ruta a imagen de fondo (opcional)

    Los puzzles que aparecen después de un [Block] heredan sus metadatos
    (block_name, block_background) hasta que aparece un nuevo [Block].
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    specs: List[PuzzleSpec] = []

    current_block_name: Optional[str] = None
    current_block_background: Optional[str] = None
    puzzle_index = 0
    block_index = 0

    i = 0
    n = len(lines)

    while i < n:
        stripped = lines[i].strip()

        # ------------------------------------------------------------
        # Bloque temático [Block] ... [/Block] (opcional)
        # ------------------------------------------------------------
        if stripped == "[Block]":
            start = i + 1
            j = start
            while j < n and lines[j].strip() != "[/Block]":
                j += 1
            if j >= n:
                raise PuzzleParseError("Falta '[/Block]' de cierre para un bloque [Block].")

            block_lines = lines[start:j]
            current_block_name, current_block_background = _parse_block_block(
                block_lines, block_index
            )
            block_index += 1
            i = j + 1
            continue

        # ------------------------------------------------------------
        # Bloque de puzzle [Puzzle] ... [/Puzzle] (obligatorio)
        # ------------------------------------------------------------
        if stripped == "[Puzzle]":
            start = i + 1
            j = start
            while j < n and lines[j].strip() != "[/Puzzle]":
                j += 1
            if j >= n:
                raise PuzzleParseError("Falta '[/Puzzle]' de cierre para un bloque [Puzzle].")

            puzzle_lines = lines[start:j]
            spec = _parse_single_block(puzzle_lines, puzzle_index)

            # Heredamos el contexto del bloque si existe
            spec.block_name = current_block_name
            spec.block_background = current_block_background

            specs.append(spec)
            puzzle_index += 1
            i = j + 1
            continue

        # Línea que no forma parte de ningún bloque reconocido: la ignoramos
        i += 1

    return specs


def _parse_block_block(block_lines: List[str], index: int) -> (Optional[str], Optional[str]):
    """
    Parsea un bloque [Block] ... [/Block].

    Parámetros reconocidos (case-insensitive):
    - name: Nombre del bloque temático
    - background: Ruta a la imagen de fondo para este bloque (opcional)
    """
    name: Optional[str] = None
    background: Optional[str] = None

    for raw in block_lines:
        line = raw.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        elif lower.startswith("background:"):
            background = line.split(":", 1)[1].strip()

    # No exigimos name obligatorio, pero es recomendable
    if not name:
        name = f"Block {index}"

    return name, background


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
            # Modo 'words': cada línea es una palabra/frase
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
