"""Slug helpers for filesystem-safe output names."""

from __future__ import annotations

import re


def slugify(name: str) -> str:
    """Convert a title into a safe folder/file name."""
    if not name or not isinstance(name, str):
        return "book"
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-]", "", name)
    return name or "book"
