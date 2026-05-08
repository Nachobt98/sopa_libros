import json
from pathlib import Path

import pytest
from PIL import Image

from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.validation.visual import (
    VISUAL_REGRESSION_REPORT_FILENAME,
    build_visual_regression_report,
    fingerprint_image,
    write_visual_regression_report,
)


def create_sample_png(path: Path, color: tuple[int, int, int]) -> str:
    Image.new("RGB", (PAGE_W_PX, PAGE_H_PX), color).save(path)
    return str(path)


def test_fingerprint_image_returns_stable_page_metadata(tmp_path):
    image_path = create_sample_png(tmp_path / "page.png", (240, 240, 240))

    fingerprint = fingerprint_image(image_path, fingerprint_size=8)

    assert fingerprint.path == image_path
    assert fingerprint.width == PAGE_W_PX
    assert fingerprint.height == PAGE_H_PX
    assert fingerprint.average_luma == 240
    assert fingerprint.luma_stddev == 0
    assert len(fingerprint.difference_hash) == 16


def test_fingerprint_image_changes_when_rendered_content_changes(tmp_path):
    light_path = create_sample_png(tmp_path / "light.png", (250, 250, 250))
    dark_path = create_sample_png(tmp_path / "dark.png", (80, 80, 80))

    light = fingerprint_image(light_path)
    dark = fingerprint_image(dark_path)

    assert light.average_luma != dark.average_luma


def test_build_visual_regression_report_contains_fingerprints(tmp_path):
    image_paths = [
        create_sample_png(tmp_path / "page_1.png", (255, 255, 255)),
        create_sample_png(tmp_path / "page_2.png", (230, 230, 230)),
    ]

    report = build_visual_regression_report(image_paths, fingerprint_size=8)

    assert report.expected_width == PAGE_W_PX
    assert report.expected_height == PAGE_H_PX
    assert report.fingerprint_size == 8
    assert [fingerprint.path for fingerprint in report.fingerprints] == image_paths


def test_write_visual_regression_report_writes_json(tmp_path):
    image_path = create_sample_png(tmp_path / "page.png", (240, 240, 240))
    report = build_visual_regression_report([image_path], fingerprint_size=8)

    report_path = write_visual_regression_report(report, output_dir=str(tmp_path))

    assert report_path == str(tmp_path / VISUAL_REGRESSION_REPORT_FILENAME)
    payload = json.loads((tmp_path / VISUAL_REGRESSION_REPORT_FILENAME).read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["fingerprint_size"] == 8
    assert payload["fingerprints"][0]["path"] == image_path


def test_fingerprint_rejects_non_positive_size(tmp_path):
    image_path = create_sample_png(tmp_path / "page.png", (240, 240, 240))

    with pytest.raises(ValueError, match="fingerprint_size"):
        fingerprint_image(image_path, fingerprint_size=0)
