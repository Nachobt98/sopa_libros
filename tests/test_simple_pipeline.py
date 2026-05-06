from wordsearch.domain.book import SimpleGenerationOptions
from wordsearch.domain.grid import GridGenerationFailure, GridGenerationResult, PlacedWord
from wordsearch.generation import simple_pipeline
from wordsearch.generation.difficulty import DifficultyLevel


def make_options() -> SimpleGenerationOptions:
    return SimpleGenerationOptions(
        book_title="Simple Test Book",
        wordlists=[["CAT", "DOG"], ["SUN", "MOON"]],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        total_puzzles=2,
    )


def test_generate_simple_book_renders_images_and_pdf(monkeypatch, tmp_path):
    generated_grids = []
    rendered_puzzles = []
    rendered_solutions = []

    def fake_generate_word_search_grid(words, *, difficulty, grid_size, max_attempts):
        generated_grids.append(
            {
                "words": list(words),
                "difficulty": difficulty,
                "grid_size": grid_size,
                "max_attempts": max_attempts,
            }
        )
        return GridGenerationResult(
            grid=[["C", "A", "T"]],
            placed_words=[PlacedWord("CAT", 0, 0, 0, 1)],
            attempts_used=1,
        )

    def fake_render_page(grid, words, idx, *, filename):
        rendered_puzzles.append((grid, list(words), idx, filename))
        return filename

    def fake_render_solution_page(grid, words, idx, *, filename, placed_words):
        rendered_solutions.append((grid, list(words), idx, filename, list(placed_words)))
        return filename

    def fake_generate_pdf(puzzles, solutions, *, outname):
        assert puzzles == [item[3] for item in rendered_puzzles]
        assert solutions == [item[3] for item in rendered_solutions]
        return outname

    monkeypatch.setattr(simple_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(simple_pipeline, "validate_wordlists_for_grid", lambda *args, **kwargs: [])
    monkeypatch.setattr(simple_pipeline, "generate_word_search_grid", fake_generate_word_search_grid)
    monkeypatch.setattr(simple_pipeline, "render_page", fake_render_page)
    monkeypatch.setattr(simple_pipeline, "render_solution_page", fake_render_solution_page)
    monkeypatch.setattr(simple_pipeline, "generate_pdf", fake_generate_pdf)
    monkeypatch.setattr(simple_pipeline._WORD_SHUFFLER, "shuffle", lambda words: words.reverse())

    pdf_path = simple_pipeline.generate_simple_book(make_options())

    assert pdf_path == str(tmp_path / "simple_test_book" / "simple_test_book.pdf")
    assert len(generated_grids) == 2
    assert generated_grids[0]["words"] == ["DOG", "CAT"]
    assert generated_grids[0]["difficulty"] is DifficultyLevel.EASY
    assert generated_grids[0]["grid_size"] == 8
    assert generated_grids[0]["max_attempts"] == simple_pipeline.DEFAULT_MAX_GRID_ATTEMPTS
    assert len(rendered_puzzles) == 2
    assert len(rendered_solutions) == 2


def test_generate_simple_book_stops_on_validation_errors(monkeypatch, tmp_path):
    validation_errors = [
        {
            "list_index": 0,
            "word": "TOOLONG",
            "clean_word": "TOOLONG",
            "length": 7,
        }
    ]

    monkeypatch.setattr(simple_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(
        simple_pipeline,
        "validate_wordlists_for_grid",
        lambda *args, **kwargs: validation_errors,
    )

    called = {"grid": False}

    def fake_generate_word_search_grid(*args, **kwargs):
        called["grid"] = True
        raise AssertionError("grid generation should not run after validation errors")

    monkeypatch.setattr(simple_pipeline, "generate_word_search_grid", fake_generate_word_search_grid)

    assert simple_pipeline.generate_simple_book(make_options()) is None
    assert called["grid"] is False


def test_generate_simple_book_stops_on_grid_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(simple_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(simple_pipeline, "validate_wordlists_for_grid", lambda *args, **kwargs: [])
    monkeypatch.setattr(simple_pipeline._WORD_SHUFFLER, "shuffle", lambda words: None)
    monkeypatch.setattr(
        simple_pipeline,
        "generate_word_search_grid",
        lambda *args, **kwargs: GridGenerationFailure(
            reason="failed",
            attempts_used=10,
            failed_words=["CAT"],
        ),
    )

    called = {"render": False}

    def fake_render_page(*args, **kwargs):
        called["render"] = True
        raise AssertionError("rendering should not run after grid generation failure")

    monkeypatch.setattr(simple_pipeline, "render_page", fake_render_page)

    assert simple_pipeline.generate_simple_book(make_options()) is None
    assert called["render"] is False


def test_generate_simple_book_returns_none_when_pdf_is_locked(monkeypatch, tmp_path):
    monkeypatch.setattr(simple_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(simple_pipeline, "validate_wordlists_for_grid", lambda *args, **kwargs: [])
    monkeypatch.setattr(simple_pipeline._WORD_SHUFFLER, "shuffle", lambda words: None)
    monkeypatch.setattr(
        simple_pipeline,
        "generate_word_search_grid",
        lambda *args, **kwargs: GridGenerationResult(
            grid=[["C", "A", "T"]],
            placed_words=[PlacedWord("CAT", 0, 0, 0, 1)],
            attempts_used=1,
        ),
    )
    monkeypatch.setattr(simple_pipeline, "render_page", lambda *args, **kwargs: kwargs["filename"])
    monkeypatch.setattr(
        simple_pipeline,
        "render_solution_page",
        lambda *args, **kwargs: kwargs["filename"],
    )

    def fake_generate_pdf(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(simple_pipeline, "generate_pdf", fake_generate_pdf)

    assert simple_pipeline.generate_simple_book(make_options()) is None
