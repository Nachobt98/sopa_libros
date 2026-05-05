"""Page planning domain model and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from wordsearch.domain.generated_puzzle import GeneratedPuzzle


@dataclass
class PagePlan:
    """Calculated page numbers for a thematic book."""

    block_first_page: Dict[str, int]
    blocks_in_order: List[str]
    puzzle_page: Dict[int, int]
    first_solution_page: int


def build_page_plan(generated_puzzles: Sequence[GeneratedPuzzle]) -> PagePlan:
    """
    Calculate page numbers after all puzzles are known to be viable.

    Current front matter convention:
    - page 1: title page
    - page 2: table of contents
    - page 3: instructions
    - page 4+: block covers and puzzles
    - after puzzles: solutions cover + solution pages
    """
    block_first_page: Dict[str, int] = {}
    blocks_in_order: List[str] = []
    puzzle_page: Dict[int, int] = {}

    current_page = 4
    current_block_name = ""

    for generated in generated_puzzles:
        spec = generated.spec
        block_name = getattr(spec, "block_name", "") or ""

        if block_name and block_name != current_block_name:
            current_block_name = block_name
            if block_name not in block_first_page:
                block_first_page[block_name] = current_page
                blocks_in_order.append(block_name)
                current_page += 1

        puzzle_page[spec.index] = current_page
        current_page += 1

    last_puzzle_page = current_page - 1
    first_solution_page = last_puzzle_page + 2

    return PagePlan(
        block_first_page=block_first_page,
        blocks_in_order=blocks_in_order,
        puzzle_page=puzzle_page,
        first_solution_page=first_solution_page,
    )
