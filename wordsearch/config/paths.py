"""Project path configuration helpers."""

from __future__ import annotations

from pathlib import Path

BASE_OUTPUT_DIR = "output_puzzles_kdp"
DEFAULT_WORDLISTS_DIR = "wordlists"
DEFAULT_THEMATIC_WORDLIST = str(Path(DEFAULT_WORDLISTS_DIR) / "book_thematic.txt")


def build_book_output_dir(book_slug: str, base_output_dir: str | Path = BASE_OUTPUT_DIR) -> str:
    """Return the output directory for a generated book slug."""
    return str(Path(base_output_dir) / book_slug)


def build_output_file(output_dir: str | Path, filename: str) -> str:
    """Return a file path inside an already selected output directory."""
    return str(Path(output_dir) / filename)


def build_default_output_file(filename: str) -> str:
    """Return a file path inside the default output root."""
    return build_output_file(BASE_OUTPUT_DIR, filename)


def build_wordlist_file(filename: str, base_dir: str | Path = DEFAULT_WORDLISTS_DIR) -> str:
    """Return a wordlist file path inside the configured wordlists directory."""
    return build_output_file(base_dir, filename)


def resolve_wordlist_input_path(user_input: str, base_dir: str | Path = DEFAULT_WORDLISTS_DIR) -> str:
    """Return an absolute user path as-is, or resolve a relative wordlist name inside base_dir."""
    path = Path(user_input)
    if path.is_absolute():
        return str(path)
    return build_wordlist_file(str(path), base_dir)


def resolve_pdf_output_path(outname: str | Path) -> str:
    """Return the final PDF path, preserving explicit directories."""
    outpath = Path(outname)
    if outpath.parent != Path("."):
        return str(outpath)
    return build_default_output_file(str(outpath))
