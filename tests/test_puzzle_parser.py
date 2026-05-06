from pathlib import Path

import pytest

from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file


def write_tmp_file(tmp_path: Path, content: str) -> str:
    path = tmp_path / "book.txt"
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return str(path)


def test_parse_single_puzzle(tmp_path):
    path = write_tmp_file(
        tmp_path,
        """
        [Puzzle]
        title: Black Inventors
        fact: Garrett Morgan invented traffic safety devices.
        words:
        Garrett Morgan
        Traffic Light
        Gas Mask
        [/Puzzle]
        """,
    )

    specs = parse_puzzle_file(path)

    assert len(specs) == 1
    assert specs[0].index == 0
    assert specs[0].title == "Black Inventors"
    assert specs[0].fact == "Garrett Morgan invented traffic safety devices."
    assert specs[0].words == ["Garrett Morgan", "Traffic Light", "Gas Mask"]
    assert specs[0].block_name is None
    assert specs[0].block_background is None


def test_parse_block_metadata_is_inherited_by_following_puzzles(tmp_path):
    path = write_tmp_file(
        tmp_path,
        """
        [Block]
        name: Black History Foundations
        background: assets/history.png
        [/Block]

        [Puzzle]
        title: Civil Rights
        fact: A short fact.
        words:
        Justice
        Freedom
        [/Puzzle]
        """,
    )

    specs = parse_puzzle_file(path)

    assert len(specs) == 1
    assert specs[0].block_name == "Black History Foundations"
    assert specs[0].block_background == "assets/history.png"


def test_parse_puzzle_deduplicates_words_preserving_order(tmp_path):
    path = write_tmp_file(
        tmp_path,
        """
        [Puzzle]
        title: Duplicate Words
        fact: A short fact.
        words:
        Jazz
        Blues
        Jazz
        Soul
        Blues
        [/Puzzle]
        """,
    )

    specs = parse_puzzle_file(path)

    assert specs[0].words == ["Jazz", "Blues", "Soul"]


def test_parse_puzzle_missing_closing_tag_raises_error(tmp_path):
    path = write_tmp_file(
        tmp_path,
        """
        [Puzzle]
        title: Missing Close
        fact: A short fact.
        words:
        Justice
        """,
    )

    with pytest.raises(PuzzleParseError, match=r"Falta '\[/Puzzle\]'"):
        parse_puzzle_file(path)


def test_parse_puzzle_missing_required_title_raises_error(tmp_path):
    path = write_tmp_file(
        tmp_path,
        """
        [Puzzle]
        fact: A short fact.
        words:
        Justice
        [/Puzzle]
        """,
    )

    with pytest.raises(PuzzleParseError, match="falta 'title:'"):
        parse_puzzle_file(path)
