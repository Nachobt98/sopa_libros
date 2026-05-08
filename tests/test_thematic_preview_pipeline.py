from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.grid import PlacedWord
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.generation import thematic_pipeline
from wordsearch.generation.book_assembly import RenderedBookImages
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.grid_batch import GridBatchResult
from wordsearch.validation.assets import AssetValidationReport


class StubValidationReport:
    def __init__(self, *, has_errors: bool = False):
        self.has_errors = has_errors

    def print_summary(self) -> None:
        pass


class StubRenderQualityReport:
    def print_summary(self) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "warning_count": 0,
            "by_severity": {},
            "by_code": {},
            "warnings": [],
        }


def make_options() -> ThematicGenerationOptions:
    return ThematicGenerationOptions(
        book_title="Preview Test Book",
        puzzles_txt_path="wordlists/book.txt",
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
    )


def make_spec(index: int) -> PuzzleSpec:
    return PuzzleSpec(
        index=index,
        title=f"Puzzle {index + 1}",
        fact="Fact",
        words=["WORD"],
        block_name="Block",
    )


def make_generated(index: int) -> GeneratedPuzzle:
    return GeneratedPuzzle(
        spec=make_spec(index),
        words_for_grid=["WORD"],
        grid=[["W"]],
        placed_words=[PlacedWord("WORD", 0, 0, 0, 1)],
    )


def test_apply_preview_limit_returns_first_n_specs():
    specs = [make_spec(0), make_spec(1), make_spec(2)]

    limited = thematic_pipeline._apply_preview_limit(specs, 2)

    assert [spec.index for spec in limited] == [0, 1]


def test_apply_preview_limit_returns_all_specs_when_limit_is_none():
    specs = [make_spec(0), make_spec(1)]

    assert thematic_pipeline._apply_preview_limit(specs, None) is specs


def test_resolve_output_dir_prefers_explicit_output_dir(tmp_path):
    options = make_options()
    options.output_dir = str(tmp_path / "custom")

    assert thematic_pipeline._resolve_output_dir(options, "preview_test_book") == str(tmp_path / "custom")


def test_generate_thematic_book_applies_limit_and_writes_visual_report(monkeypatch, tmp_path):
    options = make_options()
    options.preview = True
    options.limit = 2
    options.output_dir = str(tmp_path / "preview_output")
    specs = [make_spec(0), make_spec(1), make_spec(2)]
    generated = [make_generated(0), make_generated(1)]
    rendered_images = RenderedBookImages(
        content_imgs=["title.png", "block.png", "puzzle_1.png", "puzzle_2.png"],
        solution_imgs=["solution_1.png", "solution_2.png"],
    )
    calls = {}

    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: specs)
    monkeypatch.setattr(
        thematic_pipeline,
        "validate_generation_assets",
        lambda **kwargs: AssetValidationReport(),
    )
    monkeypatch.setattr(
        thematic_pipeline,
        "validate_thematic_specs",
        lambda *args, **kwargs: StubValidationReport(),
    )

    def fake_generate_thematic_grids(received_specs, difficulty, grid_size, *, seed=None):
        calls["grid_specs"] = received_specs
        return GridBatchResult(generated_puzzles=generated)

    def fake_render_thematic_book_images(**kwargs):
        calls["render_kwargs"] = kwargs
        return rendered_images

    def fake_build_render_quality_report(**kwargs):
        calls["render_quality_kwargs"] = kwargs
        return StubRenderQualityReport()

    def fake_build_visual_regression_report(image_paths):
        calls["visual_image_paths"] = image_paths
        return "visual-report"

    def fake_write_visual_regression_report(report, *, output_dir):
        calls["visual_write"] = (report, output_dir)
        return f"{output_dir}/visual_regression_report.json"

    monkeypatch.setattr(thematic_pipeline, "generate_thematic_grids", fake_generate_thematic_grids)
    monkeypatch.setattr(thematic_pipeline, "build_page_plan", lambda generated: "page-plan")
    monkeypatch.setattr(thematic_pipeline, "render_thematic_book_images", fake_render_thematic_book_images)
    monkeypatch.setattr(thematic_pipeline, "build_render_quality_report", fake_build_render_quality_report)
    monkeypatch.setattr(thematic_pipeline, "build_visual_regression_report", fake_build_visual_regression_report)
    monkeypatch.setattr(thematic_pipeline, "write_visual_regression_report", fake_write_visual_regression_report)
    monkeypatch.setattr(thematic_pipeline, "generate_pdf", lambda *args, **kwargs: kwargs["outname"])
    monkeypatch.setattr(thematic_pipeline, "build_kdp_preflight_report", lambda **kwargs: StubValidationReport())
    monkeypatch.setattr(thematic_pipeline, "write_kdp_preflight_report", lambda *args, **kwargs: "preflight.json")
    monkeypatch.setattr(thematic_pipeline, "build_thematic_generation_report", lambda **kwargs: "report")
    monkeypatch.setattr(thematic_pipeline, "write_generation_report", lambda *args, **kwargs: "report.json")

    pdf_path = thematic_pipeline.generate_thematic_book(options)

    assert pdf_path == str(tmp_path / "preview_output" / "preview_test_book.pdf")
    assert [spec.index for spec in calls["grid_specs"]] == [0, 1]
    assert calls["render_kwargs"]["output_dir"] == str(tmp_path / "preview_output")
    assert calls["render_quality_kwargs"]["content_image_paths"] == rendered_images.content_imgs
    assert calls["visual_image_paths"] == [
        "title.png",
        "block.png",
        "puzzle_1.png",
        "puzzle_2.png",
        "solution_1.png",
        "solution_2.png",
    ]
    assert calls["visual_write"] == ("visual-report", str(tmp_path / "preview_output"))
