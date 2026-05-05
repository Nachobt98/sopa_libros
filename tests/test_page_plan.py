from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.puzzle_parser import PuzzleSpec


def make_generated(index: int, title: str, block_name: str | None = None) -> GeneratedPuzzle:
    return GeneratedPuzzle(
        spec=PuzzleSpec(
            index=index,
            title=title,
            fact="Fact",
            words=["WORD"],
            block_name=block_name,
        ),
        words_for_grid=["WORD"],
        grid=[["W"]],
        placed_words=[],
    )


def test_build_page_plan_with_blocks_and_puzzles():
    generated = [
        make_generated(0, "Puzzle 1", "Block A"),
        make_generated(1, "Puzzle 2", "Block A"),
        make_generated(2, "Puzzle 3", "Block B"),
    ]

    plan = build_page_plan(generated)

    assert plan.block_first_page == {
        "Block A": 4,
        "Block B": 7,
    }
    assert plan.blocks_in_order == ["Block A", "Block B"]
    assert plan.puzzle_page == {
        0: 5,
        1: 6,
        2: 8,
    }
    assert plan.first_solution_page == 10


def test_build_page_plan_without_blocks():
    generated = [
        make_generated(0, "Puzzle 1"),
        make_generated(1, "Puzzle 2"),
    ]

    plan = build_page_plan(generated)

    assert plan.block_first_page == {}
    assert plan.blocks_in_order == []
    assert plan.puzzle_page == {
        0: 4,
        1: 5,
    }
    assert plan.first_solution_page == 7
