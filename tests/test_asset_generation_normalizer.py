from PIL import Image

from wordsearch.asset_generation.normalizer import normalize_generated_asset


def test_normalize_generated_asset_converts_resizes_and_writes_png(tmp_path):
    raw_path = tmp_path / "raw.png"
    output_path = tmp_path / "processed" / "asset.png"
    Image.new("RGBA", (20, 30), (255, 0, 0, 128)).save(raw_path)

    result = normalize_generated_asset(raw_path, output_path, (80, 100))

    assert result == str(output_path)
    with Image.open(output_path) as image:
        assert image.size == (80, 100)
        assert image.mode == "RGB"
