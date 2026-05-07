import os
import tempfile
import shutil
import pytest
from PIL import Image
from wordsearch.rendering import front_matter

def test_render_table_of_contents_creates_image(tmp_path):
    toc_entries = [
        ("Section 1", 5, True),
        ("Section 2", 10, True),
        ("Solutions", 20, True),
    ]
    output_dir = tmp_path
    result = front_matter.render_table_of_contents(toc_entries, str(output_dir))
    assert isinstance(result, list)
    assert result[0].endswith(".png")
    assert os.path.exists(result[0])
    img = Image.open(result[0])
    assert img.size[0] > 0 and img.size[1] > 0

def test_render_instructions_page_creates_image(tmp_path):
    filename = tmp_path / "instructions.png"
    result = front_matter.render_instructions_page("Test Book", filename=str(filename))
    assert result == str(filename)
    assert os.path.exists(result)
    img = Image.open(result)
    assert img.size[0] > 0 and img.size[1] > 0

def test_render_table_of_contents_with_custom_background(tmp_path):
    # Create a dummy background image
    bg_path = tmp_path / "bg.png"
    img = Image.new("RGBA", (300, 400), (123, 222, 111, 255))
    img.save(bg_path)
    toc_entries = [("Section", 1, True)]
    result = front_matter.render_table_of_contents(toc_entries, str(tmp_path), background_path=str(bg_path))
    assert os.path.exists(result[0])
    img2 = Image.open(result[0])
    assert img2.size[0] > 0 and img2.size[1] > 0

def test_render_instructions_page_with_custom_background(tmp_path):
    bg_path = tmp_path / "bg2.png"
    img = Image.new("RGBA", (300, 400), (10, 20, 30, 255))
    img.save(bg_path)
    filename = tmp_path / "instructions2.png"
    result = front_matter.render_instructions_page("Book", filename=str(filename), background_path=str(bg_path))
    assert os.path.exists(result)
    img2 = Image.open(result)
    assert img2.size[0] > 0 and img2.size[1] > 0
