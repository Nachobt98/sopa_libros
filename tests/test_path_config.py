from pathlib import Path

from wordsearch.config.paths import (
    BASE_OUTPUT_DIR,
    DEFAULT_THEMATIC_WORDLIST,
    build_book_output_dir,
    build_default_output_file,
    build_output_file,
    build_wordlist_file,
    resolve_pdf_output_path,
    resolve_wordlist_input_path,
)


def test_build_book_output_dir_uses_base_output_root():
    assert build_book_output_dir("my_book") == str(Path(BASE_OUTPUT_DIR) / "my_book")


def test_build_book_output_dir_accepts_custom_base_path(tmp_path):
    assert build_book_output_dir("my_book", tmp_path) == str(tmp_path / "my_book")


def test_build_output_file_joins_inside_selected_output_dir(tmp_path):
    assert build_output_file(tmp_path / "book", "puzzle_1.png") == str(tmp_path / "book" / "puzzle_1.png")


def test_build_default_output_file_uses_default_output_root():
    assert build_default_output_file("preview.png") == str(Path(BASE_OUTPUT_DIR) / "preview.png")


def test_resolve_pdf_output_path_keeps_explicit_directory(tmp_path):
    explicit_pdf = tmp_path / "book.pdf"

    assert resolve_pdf_output_path(explicit_pdf) == str(explicit_pdf)


def test_resolve_pdf_output_path_uses_default_root_for_bare_filename():
    assert resolve_pdf_output_path("book.pdf") == str(Path(BASE_OUTPUT_DIR) / "book.pdf")


def test_default_thematic_wordlist_points_to_wordlists_folder():
    assert DEFAULT_THEMATIC_WORDLIST == str(Path("wordlists") / "book_thematic.txt")


def test_build_wordlist_file_uses_configured_wordlists_folder():
    assert build_wordlist_file("animals.txt") == str(Path("wordlists") / "animals.txt")


def test_resolve_wordlist_input_path_keeps_absolute_path(tmp_path):
    explicit_path = tmp_path / "animals.txt"

    assert resolve_wordlist_input_path(str(explicit_path)) == str(explicit_path)


def test_resolve_wordlist_input_path_uses_wordlists_folder_for_relative_name():
    assert resolve_wordlist_input_path("animals.txt") == str(Path("wordlists") / "animals.txt")
