from wordsearch.asset_generation.brief import build_book_visual_brief
from wordsearch.domain.puzzle import PuzzleSpec


def make_spec(index: int, *, title: str, fact: str, words: list[str], block_name: str) -> PuzzleSpec:
    return PuzzleSpec(
        index=index,
        title=title,
        fact=fact,
        words=words,
        block_name=block_name,
    )


def test_build_book_visual_brief_extracts_subject_keywords_and_blocks():
    specs = [
        make_spec(
            0,
            title="Nile Pharaohs",
            fact="Ancient Egyptian pharaohs built monuments near the Nile.",
            words=["NILE", "PHARAOH", "PYRAMID", "TEMPLE"],
            block_name="Pharaohs and Queens",
        ),
        make_spec(
            1,
            title="Gods of Egypt",
            fact="Ra and Osiris appear in many Egyptian mythology stories.",
            words=["RA", "OSIRIS", "MYTHOLOGY", "TEMPLE"],
            block_name="Gods and Mythology",
        ),
    ]

    brief = build_book_visual_brief(
        book_title="Ancient Egypt Word Search Collection",
        specs=specs,
        style="premium-historical",
    )

    assert brief.subject == "Ancient Egypt"
    assert brief.style == "premium-historical"
    assert brief.tone == "educational, elegant, historical, print-friendly"
    assert brief.keywords[:2] == ["ancient", "egypt"]
    assert "egyptian" in brief.keywords
    assert "temple" in brief.keywords
    assert "readable text" in brief.avoid
    assert brief.visual_keywords[0] == "premium historical editorial style"
    assert [block.slug for block in brief.blocks] == ["pharaohs_and_queens", "gods_and_mythology"]
    assert brief.blocks[0].keywords[:2] == ["ancient", "egypt"]
    assert brief.blocks[0].puzzle_count == 1
    assert brief.blocks[0].sample_titles == ["Nile Pharaohs"]
    assert "Pharaohs and Queens" in brief.blocks[0].visual_direction


def test_build_book_visual_brief_uses_default_block_when_missing():
    specs = [
        PuzzleSpec(
            index=0,
            title="Mixed Facts",
            fact="A general fact about science and nature.",
            words=["SCIENCE", "NATURE"],
        )
    ]

    brief = build_book_visual_brief(
        book_title="Word Search Book",
        specs=specs,
        style="unknown-style",
    )

    assert brief.subject == "general knowledge"
    assert brief.tone == "educational, clean, low-contrast, print-friendly"
    assert brief.blocks[0].slug == "default"
    assert brief.blocks[0].name == "default"
    assert brief.visual_keywords[0] == "subtle editorial placeholder style"


def test_build_book_visual_brief_filters_layout_fixture_noise():
    specs = [
        make_spec(
            0,
            title="Baseline Layout Checks",
            fact="This layout check verifies grid wrapping and solution list spacing.",
            words=["LAYOUT", "GRID", "SOLUTION", "SPACING"],
            block_name="Solution And Word List Checks",
        )
    ]

    brief = build_book_visual_brief(
        book_title="Ancient Egypt Word Search",
        specs=specs,
        style="premium-historical",
    )

    assert brief.keywords == ["ancient", "egypt"]
    assert brief.blocks[0].keywords == ["ancient", "egypt"]
    assert "checks" not in brief.visual_keywords[-1]


def test_visual_brief_to_dict_serializes_nested_blocks():
    specs = [
        make_spec(
            0,
            title="Civil Rights Leaders",
            fact="Civil rights leaders organized marches and community action.",
            words=["JUSTICE", "MARCH", "LEADERS"],
            block_name="Civil Rights",
        )
    ]

    payload = build_book_visual_brief(
        book_title="Black History Word Search",
        specs=specs,
        style="premium-neutral",
    ).to_dict()

    assert payload["subject"] == "Black History"
    assert payload["keywords"][:2] == ["black", "history"]
    assert payload["blocks"][0]["slug"] == "civil_rights"
    assert payload["blocks"][0]["keywords"]
    assert payload["avoid"]
