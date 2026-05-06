from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.grid import PlacedWord
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.generation import thematic_pipeline
from wordsearch.generation.book_assembly import RenderedBookImages
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.grid_batch import GridBatchResult
from wordsearch.parsing.thematic import PuzzleParseError


class StubValidationReport:
    def __init__(self, *, has_errors: bool):
        self.has_errors = has_errors
        self.summary_printed = False

    def print_summary(self) -> None:
        self.summary_printed = True


def make_options() -> ThematicGenerationOptions:
    return ThematicGenerationOptions(
        book_title="Thematic Test Book",
        puzzles_txt_path="wordlists/book.txt",
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
    )


def make_spec(index: int = 0) -> PuzzleSpec:
    return PuzzleSpec(
        index=index,
        title=f"Puzzle {index + 1}",
        fact="Fact",
        words=["WORD"],
        block_name="Block",
    )


def make_generated(index: int = 0) -> GeneratedPuzzle:
    return GeneratedPuzzle(
        spec=make_spec(index),
        words_for_grid=["WORD"],
        grid=[["W"]],
        placed_words=[PlacedWord("WORD", 0, 0, 0, 1)],
    )


def test_generate_thematic_book_returns_none_when_input_file_is_missing(monkeypatch):
    monkeypatch.setattr(
        thematic_pipeline,
        "parse_puzzle_file",
        lambda path: (_ for _ in ()).throw(FileNotFoundError),
    )

    assert thematic_pipeline.generate_thematic_book(make_options()) is None


def test_generate_thematic_book_returns_none_on_parse_error(monkeypatch):
    monkeypatch.setattr(
        thematic_pipeline,
        "parse_puzzle_file",
        lambda path: (_ for _ in ()).throw(PuzzleParseError("bad input")),
    )

    assert thematic_pipeline.generate_thematic_book(make_options()) is None


def test_generate_thematic_book_returns_none_when_file_has_no_puzzles(monkeypatch):
    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: [])

    assert thematic_pipeline.generate_thematic_book(make_options()) is None


def test_generate_thematic_book_stops_on_validation_errors(monkeypatch):
    report = StubValidationReport(has_errors=True)
    called = {"grid": False}

    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: [make_spec()])
    monkeypatch.setattr(thematic_pipeline, "validate_thematic_specs", lambda specs, grid_size: report)

    def fake_generate_thematic_grids(*args, **kwargs):
        called["grid"] = True
        raise AssertionError("grid generation should not run after validation errors")

    monkeypatch.setattr(thematic_pipeline, "generate_thematic_grids", fake_generate_thematic_grids)

    assert thematic_pipeline.generate_thematic_book(make_options()) is None
    assert report.summary_printed
    assert called["grid"] is False


def test_generate_thematic_book_stops_on_grid_failures(monkeypatch):
    report = StubValidationReport(has_errors=False)
    grid_batch = GridBatchResult(failures=["Puzzle 1 failed"])

    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: [make_spec()])
    monkeypatch.setattr(thematic_pipeline, "validate_thematic_specs", lambda specs, grid_size: report)
    monkeypatch.setattr(
        thematic_pipeline,
        "generate_thematic_grids",
        lambda specs, difficulty, grid_size: grid_batch,
    )

    called = {"render": False}

    def fake_render_thematic_book_images(*args, **kwargs):
        called["render"] = True
        raise AssertionError("rendering should not run after grid failures")

    monkeypatch.setattr(thematic_pipeline, "render_thematic_book_images", fake_render_thematic_book_images)

    assert thematic_pipeline.generate_thematic_book(make_options()) is None
    assert called["render"] is False


def test_generate_thematic_book_returns_none_when_rendering_is_incomplete(monkeypatch, tmp_path):
    report = StubValidationReport(has_errors=False)
    grid_batch = GridBatchResult(generated_puzzles=[make_generated()])

    monkeypatch.setattr(thematic_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: [make_spec()])
    monkeypatch.setattr(thematic_pipeline, "validate_thematic_specs", lambda specs, grid_size: report)
    monkeypatch.setattr(
        thematic_pipeline,
        "generate_thematic_grids",
        lambda specs, difficulty, grid_size: grid_batch,
    )
    monkeypatch.setattr(
        thematic_pipeline,
        "render_thematic_book_images",
        lambda **kwargs: RenderedBookImages(content_imgs=[], solution_imgs=[]),
    )

    assert thematic_pipeline.generate_thematic_book(make_options()) is None


def test_generate_thematic_book_returns_none_when_pdf_is_locked(monkeypatch, tmp_path):
    report = StubValidationReport(has_errors=False)
    grid_batch = GridBatchResult(generated_puzzles=[make_generated()])

    monkeypatch.setattr(thematic_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: [make_spec()])
    monkeypatch.setattr(thematic_pipeline, "validate_thematic_specs", lambda specs, grid_size: report)
    monkeypatch.setattr(
        thematic_pipeline,
        "generate_thematic_grids",
        lambda specs, difficulty, grid_size: grid_batch,
    )
    monkeypatch.setattr(
        thematic_pipeline,
        "render_thematic_book_images",
        lambda **kwargs: RenderedBookImages(content_imgs=["content.png"], solution_imgs=["solution.png"]),
    )
    monkeypatch.setattr(
        thematic_pipeline,
        "generate_pdf",
        lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError),
    )

    assert thematic_pipeline.generate_thematic_book(make_options()) is None


def test_generate_thematic_book_generates_pdf_on_happy_path(monkeypatch, tmp_path):
    options = make_options()
    specs = [make_spec()]
    generated_puzzles = [make_generated()]
    report = StubValidationReport(has_errors=False)
    grid_batch = GridBatchResult(generated_puzzles=generated_puzzles)
    rendered_images = RenderedBookImages(content_imgs=["content.png"], solution_imgs=["solution.png"])
    calls = {}

    monkeypatch.setattr(thematic_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: specs)
    monkeypatch.setattr(thematic_pipeline, "validate_thematic_specs", lambda specs, grid_size: report)
    monkeypatch.setattr(
        thematic_pipeline,
        "generate_thematic_grids",
        lambda specs, difficulty, grid_size: grid_batch,
    )

    def fake_build_page_plan(received_generated_puzzles):
        calls["page_plan_generated"] = received_generated_puzzles
        return "page-plan"

    def fake_render_thematic_book_images(**kwargs):
        calls["render_kwargs"] = kwargs
        return rendered_images

    def fake_generate_pdf(content_imgs, solution_imgs, *, outname):
        calls["pdf"] = (content_imgs, solution_imgs, outname)
        return outname

    monkeypatch.setattr(thematic_pipeline, "build_page_plan", fake_build_page_plan)
    monkeypatch.setattr(thematic_pipeline, "render_thematic_book_images", fake_render_thematic_book_images)
    monkeypatch.setattr(thematic_pipeline, "generate_pdf", fake_generate_pdf)

    pdf_path = thematic_pipeline.generate_thematic_book(options)

    expected_output_dir = tmp_path / "thematic_test_book"
    expected_pdf_path = str(expected_output_dir / "thematic_test_book.pdf")
    assert pdf_path == expected_pdf_path
    assert calls["page_plan_generated"] == generated_puzzles
    assert calls["render_kwargs"] == {
        "book_title": options.book_title,
        "generated_puzzles": generated_puzzles,
        "page_plan": "page-plan",
        "output_dir": str(expected_output_dir),
    }
    assert calls["pdf"] == (["content.png"], ["solution.png"], expected_pdf_path)
