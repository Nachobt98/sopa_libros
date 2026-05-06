"""Word list file loading helpers."""

from __future__ import annotations


def load_wordlists_from_txt(path: str) -> list[list[str]]:
    """
    Load word lists from a TXT file.

    Blank lines separate independent word lists. Each non-blank line is treated
    as one display word.
    """
    wordlists: list[list[str]] = []
    current: list[str] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if current:
                    wordlists.append(current)
                    current = []
            else:
                current.append(line)

    if current:
        wordlists.append(current)

    return wordlists
