from pathlib import Path

from PIL import Image

from wordsearch.validation import assets


def test_collect_background_paths_deduplicates_and_skips_empty_values():
    assert assets.collect_background_paths(
        ["assets/world.png", None, "", "custom.png", "assets/world.png"]
    ) == ["assets/world.png", "custom.png"]


def test_validate_output_directory_creates_and_checks_writable_path(tmp_path):
    output_dir = tmp_path / "nested" / "output"

    report = assets.validate_output_directory(str(output_dir))

    assert output_dir.is_dir()
    assert not report.has_errors


def test_validate_generation_assets_reports_missing_required_font(monkeypatch, tmp_path):
    monkeypatch.setattr(assets, "FONT_PATH", str(tmp_path / "missing.ttf"))
    monkeypatch.setattr(assets, "FONT_PATH_BOLD", str(tmp_path / "bold.ttf"))
    monkeypatch.setattr(assets, "FONT_TITLE", str(tmp_path / "title.ttf"))
    monkeypatch.setattr(assets, "BACKGROUND_PATH", str(tmp_path / "missing_background.png"))

    report = assets.validate_generation_assets(output_dir=str(tmp_path / "out"))

    assert report.has_errors
    assert len(report.errors) == 3
    assert len(report.warnings) == 1
    assert "fuente requerida" in report.errors[0].message
    assert "fondo" in report.warnings[0].message


def test_validate_generation_assets_accepts_fonts_and_warns_on_background_extension(
    monkeypatch,
    tmp_path,
):
    font = tmp_path / "font.ttf"
    font.write_text("fake-font", encoding="utf-8")
    background = tmp_path / "background.txt"
    Image.new("RGB", (1, 1), "white").save(background, format="PNG")

    monkeypatch.setattr(assets, "FONT_PATH", str(font))
    monkeypatch.setattr(assets, "FONT_PATH_BOLD", str(font))
    monkeypatch.setattr(assets, "FONT_TITLE", str(font))
    monkeypatch.setattr(assets, "BACKGROUND_PATH", str(background))

    report = assets.validate_generation_assets(
        output_dir=str(tmp_path / "out"),
        optional_backgrounds=[str(background), str(Path("other.png"))],
    )

    assert not report.has_errors
    assert [warning.path for warning in report.warnings] == [
        str(background),
        str(Path("other.png")),
    ]


def test_validate_generation_assets_errors_on_corrupt_existing_background(monkeypatch, tmp_path):
    font = tmp_path / "font.ttf"
    font.write_text("fake-font", encoding="utf-8")
    background = tmp_path / "background.png"
    background.write_text("not an image", encoding="utf-8")

    monkeypatch.setattr(assets, "FONT_PATH", str(font))
    monkeypatch.setattr(assets, "FONT_PATH_BOLD", str(font))
    monkeypatch.setattr(assets, "FONT_TITLE", str(font))
    monkeypatch.setattr(assets, "BACKGROUND_PATH", str(background))

    report = assets.validate_generation_assets(output_dir=str(tmp_path / "out"))

    assert report.has_errors
    assert report.errors[0].path == str(background)
