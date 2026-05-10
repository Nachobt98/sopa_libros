import json

from wordsearch.asset_generation.manifest import AssetManifest, ManifestAsset
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


class StubReviewSummary:
    recommendation = "review"

    def print_summary(self) -> None:
        pass


def make_options() -> ThematicGenerationOptions:
    return ThematicGenerationOptions(
        book_title="Manifest Pipeline Book",
        puzzles_txt_path="wordlists/book.txt",
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
        theme_manifest_path="assets/generated/book/asset_manifest.json",
    )


def make_spec() -> PuzzleSpec:
    return PuzzleSpec(
        index=0,
        title="Puzzle 1",
        fact="Fact",
        words=["WORD"],
        block_name="Block",
    )


def make_generated() -> GeneratedPuzzle:
    return GeneratedPuzzle(
        spec=make_spec(),
        words_for_grid=["WORD"],
        grid=[["W"]],
        placed_words=[PlacedWord("WORD", 0, 0, 0, 1)],
    )


def make_manifest() -> AssetManifest:
    return AssetManifest(
        book_title="Manifest Pipeline Book",
        theme_id="manifest-pipeline-book",
        assets={
            "book_default_background": ManifestAsset(
                type="background",
                path="processed/default_background.png",
            )
        },
        manifest_path="assets/generated/book/asset_manifest.json",
    )


def test_load_asset_manifest_returns_none_for_missing_file(capsys):
    manifest = thematic_pipeline._load_asset_manifest("missing/asset_manifest.json")

    captured = capsys.readouterr()
    assert manifest is None
    assert "Theme manifest not found" in captured.out


def test_load_asset_manifest_returns_none_for_invalid_json(tmp_path, capsys):
    manifest_path = tmp_path / "asset_manifest.json"
    manifest_path.write_text("{not json", encoding="utf-8")

    manifest = thematic_pipeline._load_asset_manifest(str(manifest_path))

    captured = capsys.readouterr()
    assert manifest is None
    assert "Could not read theme manifest" in captured.out


def test_load_asset_manifest_reads_valid_manifest(tmp_path):
    manifest_path = tmp_path / "asset_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "book_title": "Book",
                "theme_id": "book-theme",
                "assets": {
                    "book_default_background": {
                        "type": "background",
                        "path": "processed/default.png",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    manifest = thematic_pipeline._load_asset_manifest(str(manifest_path))

    assert manifest is not None
    assert manifest.theme_id == "book-theme"
    assert manifest.resolve_asset_path("book_default_background") == str(tmp_path / "processed/default.png")


def test_optional_progress_grid_wrapper_passes_callback_when_supported(monkeypatch):
    options = make_options()
    spec = make_spec()
    calls = {"progress": 0}

    def fake_generate_thematic_grids(specs, difficulty, grid_size, *, seed=None, progress_callback=None):
        assert specs == [spec]
        assert difficulty == options.difficulty
        assert grid_size == options.grid_size
        assert seed is None
        progress_callback()
        return GridBatchResult(generated_puzzles=[make_generated()])

    monkeypatch.setattr(thematic_pipeline, "generate_thematic_grids", fake_generate_thematic_grids)

    result = thematic_pipeline._generate_thematic_grids_with_optional_progress(
        [spec],
        options,
        progress_callback=lambda: calls.__setitem__("progress", calls["progress"] + 1),
    )

    assert result.generated_puzzles
    assert calls["progress"] == 1


def test_optional_render_wrapper_passes_callback_when_supported(monkeypatch):
    calls = {"progress": 0}

    def fake_render_thematic_book_images(*, progress_callback=None, **kwargs):
        assert kwargs == {"book_title": "Book"}
        progress_callback()
        return RenderedBookImages(content_imgs=["content.png"], solution_imgs=["solution.png"])

    monkeypatch.setattr(thematic_pipeline, "render_thematic_book_images", fake_render_thematic_book_images)

    result = thematic_pipeline._render_thematic_book_images_with_optional_progress(
        {"book_title": "Book"},
        progress_callback=lambda: calls.__setitem__("progress", calls["progress"] + 1),
    )

    assert result.is_complete
    assert calls["progress"] == 1


def test_generate_thematic_book_passes_loaded_manifest_to_validation_render_and_report(monkeypatch, tmp_path):
    options = make_options()
    manifest = make_manifest()
    spec = make_spec()
    generated = make_generated()
    rendered_images = RenderedBookImages(content_imgs=["content.png"], solution_imgs=["solution.png"])
    calls = {}

    monkeypatch.setattr(thematic_pipeline, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic_pipeline, "_load_asset_manifest", lambda path: manifest)
    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", lambda path: [spec])
    monkeypatch.setattr(thematic_pipeline, "validate_generation_assets", lambda **kwargs: AssetValidationReport())

    def fake_validate_asset_manifest_assets(received_manifest):
        calls["validated_manifest"] = received_manifest
        return AssetValidationReport()

    monkeypatch.setattr(thematic_pipeline, "validate_asset_manifest_assets", fake_validate_asset_manifest_assets)
    monkeypatch.setattr(thematic_pipeline, "validate_thematic_specs", lambda *args, **kwargs: StubValidationReport())
    monkeypatch.setattr(
        thematic_pipeline,
        "generate_thematic_grids",
        lambda specs, difficulty, grid_size, *, seed=None: GridBatchResult(generated_puzzles=[generated]),
    )
    monkeypatch.setattr(thematic_pipeline, "build_page_plan", lambda generated_puzzles: "page-plan")

    def fake_render_thematic_book_images(**kwargs):
        calls["render_kwargs"] = kwargs
        return rendered_images

    monkeypatch.setattr(thematic_pipeline, "render_thematic_book_images", fake_render_thematic_book_images)
    monkeypatch.setattr(thematic_pipeline, "build_render_quality_report", lambda **kwargs: StubRenderQualityReport())
    monkeypatch.setattr(thematic_pipeline, "generate_pdf", lambda *args, **kwargs: kwargs["outname"])
    monkeypatch.setattr(thematic_pipeline, "build_kdp_preflight_report", lambda **kwargs: StubValidationReport())
    monkeypatch.setattr(thematic_pipeline, "write_kdp_preflight_report", lambda *args, **kwargs: "preflight.json")

    def fake_build_thematic_generation_report(**kwargs):
        calls["report_kwargs"] = kwargs
        return "report"

    monkeypatch.setattr(thematic_pipeline, "build_thematic_generation_report", fake_build_thematic_generation_report)
    monkeypatch.setattr(thematic_pipeline, "write_generation_report", lambda *args, **kwargs: "report.json")
    monkeypatch.setattr(thematic_pipeline, "build_production_review_summary", lambda **kwargs: StubReviewSummary())
    monkeypatch.setattr(thematic_pipeline, "write_production_review_summary", lambda *args, **kwargs: "review.json")
    monkeypatch.setattr(thematic_pipeline, "print_completion_animation", lambda: None)

    pdf_path = thematic_pipeline.generate_thematic_book(options)

    assert pdf_path is not None
    assert calls["validated_manifest"] is manifest
    assert calls["render_kwargs"]["asset_manifest"] is manifest
    assert calls["report_kwargs"]["asset_manifest"] is manifest


def test_generate_thematic_book_stops_when_manifest_path_is_invalid(monkeypatch):
    options = make_options()
    calls = {"parse": False}
    monkeypatch.setattr(thematic_pipeline, "_load_asset_manifest", lambda path: None)

    def fake_parse_puzzle_file(path):
        calls["parse"] = True
        raise AssertionError("parser should not run when manifest loading fails")

    monkeypatch.setattr(thematic_pipeline, "parse_puzzle_file", fake_parse_puzzle_file)

    assert thematic_pipeline.generate_thematic_book(options) is None
    assert calls["parse"] is False
