from wordsearch.config.design import PREMIUM_NEUTRAL_THEME
from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.grid import PlacedWord
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.generation import book_assembly


def make_generated(
    index: int,
    title: str,
    *,
    block_name: str | None = None,
    block_background: str | None = None,
) -> GeneratedPuzzle:
    return GeneratedPuzzle(
        spec=PuzzleSpec(
            index=index,
            title=title,
            fact=f"Fact {index}",
            words=[f"WORD{index}"],
            block_name=block_name,
            block_background=block_background,
        ),
        words_for_grid=[f"WORD{index}"],
        grid=[[str(index)]],
        placed_words=[PlacedWord(f"WORD{index}", 0, 0, 0, 1)],
    )


def test_build_toc_entries_includes_blocks_and_solutions():
    generated = [
        make_generated(0, "Puzzle 1", block_name="Block A"),
        make_generated(1, "Puzzle 2", block_name="Block B"),
    ]
    page_plan = build_page_plan(generated)

    assert book_assembly.build_toc_entries(page_plan) == [
        ("Block A", 4, True),
        ("Block B", 6, True),
        ("Solutions", 9, True),
    ]


def test_render_thematic_book_images_orchestrates_pages_in_order(monkeypatch, tmp_path):
    generated = [
        make_generated(0, "Puzzle 1", block_name="Block A", block_background="a.png"),
        make_generated(1, "Puzzle 2", block_name="Block A", block_background="a.png"),
        make_generated(2, "Puzzle 3", block_name="Block B", block_background="b.png"),
    ]
    page_plan = build_page_plan(generated)
    calls = []

    def fake_render_title_page(book_title, *, filename, background_path, theme):
        calls.append(("title", book_title, filename, background_path, theme.name))
        return filename

    def fake_render_table_of_contents(entries, *, output_dir, background_path, theme):
        calls.append(("toc", entries, output_dir, background_path, theme.name))
        return [str(tmp_path / "toc_1.png"), str(tmp_path / "toc_2.png")]

    def fake_render_instructions_page(book_title, *, filename, background_path, theme):
        calls.append(("instructions", book_title, filename, background_path, theme.name))
        return filename

    def fake_render_block_cover(*, block_name, block_index, filename, background_path, theme):
        calls.append(("block", block_name, block_index, filename, background_path, theme.name))
        return filename

    def fake_render_page(
        grid,
        words,
        idx,
        *,
        filename,
        puzzle_title,
        fun_fact,
        solution_page_number,
        background_path,
        theme=None,
    ):
        calls.append(
            (
                "puzzle",
                grid,
                list(words),
                idx,
                filename,
                puzzle_title,
                fun_fact,
                solution_page_number,
                background_path,
                None if theme is None else theme.name,
            )
        )
        return filename

    def fake_render_solution_page(
        grid,
        words,
        idx,
        *,
        filename,
        placed_words,
        puzzle_title,
        background_path,
        theme=None,
    ):
        calls.append(
            (
                "solution",
                grid,
                list(words),
                idx,
                filename,
                list(placed_words),
                puzzle_title,
                background_path,
                None if theme is None else theme.name,
            )
        )
        return filename

    monkeypatch.setattr(book_assembly, "render_title_page", fake_render_title_page)
    monkeypatch.setattr(book_assembly, "render_table_of_contents", fake_render_table_of_contents)
    monkeypatch.setattr(book_assembly, "render_instructions_page", fake_render_instructions_page)
    monkeypatch.setattr(book_assembly, "render_block_cover", fake_render_block_cover)
    monkeypatch.setattr(book_assembly, "render_page", fake_render_page)
    monkeypatch.setattr(book_assembly, "render_solution_page", fake_render_solution_page)

    rendered = book_assembly.render_thematic_book_images(
        book_title="Thematic Book",
        generated_puzzles=generated,
        page_plan=page_plan,
        output_dir=str(tmp_path),
        theme=PREMIUM_NEUTRAL_THEME,
    )

    assert rendered.is_complete
    assert rendered.content_imgs == [
        str(tmp_path / "00_title_page.png"),
        str(tmp_path / "toc_1.png"),
        str(tmp_path / "toc_2.png"),
        str(tmp_path / "02_instructions.png"),
        str(tmp_path / "block_01_block_a.png"),
        str(tmp_path / "puzzle_1.png"),
        str(tmp_path / "puzzle_2.png"),
        str(tmp_path / "block_02_block_b.png"),
        str(tmp_path / "puzzle_3.png"),
    ]
    assert rendered.solution_imgs == [
        str(tmp_path / "puzzle_1_sol.png"),
        str(tmp_path / "puzzle_2_sol.png"),
        str(tmp_path / "puzzle_3_sol.png"),
    ]
    assert [call[0] for call in calls] == [
        "title",
        "toc",
        "instructions",
        "block",
        "puzzle",
        "solution",
        "puzzle",
        "solution",
        "block",
        "puzzle",
        "solution",
    ]

    front_matter_calls = [call for call in calls if call[0] in {"title", "toc", "instructions"}]
    assert [call[-1] for call in front_matter_calls] == ["premium-neutral"] * 3

    block_calls = [call for call in calls if call[0] == "block"]
    assert block_calls[0][1:] == (
        "Block A",
        1,
        str(tmp_path / "block_01_block_a.png"),
        "a.png",
        "premium-neutral",
    )
    assert block_calls[1][1:] == (
        "Block B",
        2,
        str(tmp_path / "block_02_block_b.png"),
        "b.png",
        "premium-neutral",
    )

    puzzle_calls = [call for call in calls if call[0] == "puzzle"]
    assert [call[7] for call in puzzle_calls] == [page_plan.first_solution_page + index for index in range(3)]
    assert [call[8] for call in puzzle_calls] == ["a.png", "a.png", "b.png"]
    assert [call[9] for call in puzzle_calls] == ["premium-neutral"] * 3

    solution_calls = [call for call in calls if call[0] == "solution"]
    assert [call[-1] for call in solution_calls] == ["premium-neutral"] * 3
