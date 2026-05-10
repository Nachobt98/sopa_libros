"""Content-aware visual brief extraction for generated book assets.

This module is deliberately deterministic. It does not call an LLM yet; it
extracts a compact, reusable brief from the parsed thematic TXT so later image
providers can consume stronger prompts without coupling rendering to AI.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Iterable

from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.utils.slug import slugify

MAX_KEYWORDS = 12
MAX_BLOCK_KEYWORDS = 10

_GENERIC_STOPWORDS = {
    "about",
    "across",
    "after",
    "also",
    "and",
    "are",
    "book",
    "can",
    "collection",
    "each",
    "fact",
    "for",
    "from",
    "has",
    "have",
    "into",
    "its",
    "make",
    "more",
    "page",
    "puzzle",
    "puzzles",
    "search",
    "section",
    "short",
    "that",
    "the",
    "their",
    "theme",
    "themed",
    "this",
    "through",
    "title",
    "was",
    "were",
    "when",
    "while",
    "with",
    "word",
    "words",
}

_LAYOUT_TEST_STOPWORDS = {
    "answer",
    "baseline",
    "balance",
    "canvas",
    "check",
    "checks",
    "column",
    "columns",
    "default",
    "dense",
    "design",
    "deliberately",
    "enough",
    "fixture",
    "fun",
    "grid",
    "included",
    "includes",
    "keeping",
    "keeps",
    "layout",
    "lengths",
    "letters",
    "lines",
    "list",
    "longer",
    "margin",
    "medium",
    "mixed",
    "multiple",
    "needs",
    "normalized",
    "output",
    "panel",
    "phrases",
    "preflight",
    "preview",
    "print",
    "readable",
    "regression",
    "regressions",
    "renderer",
    "rhythm",
    "run",
    "solution",
    "spacing",
    "stressing",
    "test",
    "testing",
    "text",
    "typography",
    "validation",
    "vertical",
    "verifies",
    "verify",
    "visible",
    "without",
    "wrapping",
}

_STYLE_HINTS = {
    "premium-historical": [
        "premium historical editorial style",
        "subtle archival paper texture",
        "warm muted palette",
        "fine ornamental line work",
    ],
    "mock-editorial": [
        "subtle editorial placeholder style",
        "low-contrast paper texture",
        "clean printable background",
    ],
    "kids": [
        "friendly activity book style",
        "soft playful shapes",
        "clear high-readability layout",
    ],
    "premium-neutral": [
        "premium neutral editorial style",
        "minimal paper texture",
        "quiet refined ornaments",
    ],
}


@dataclass(frozen=True)
class BlockVisualBrief:
    """Visual summary for a thematic block."""

    slug: str
    name: str
    puzzle_count: int
    keywords: list[str] = field(default_factory=list)
    sample_titles: list[str] = field(default_factory=list)
    visual_direction: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class BookVisualBrief:
    """Book-level visual summary derived from parsed puzzle content."""

    book_title: str
    style: str
    subject: str
    tone: str
    keywords: list[str] = field(default_factory=list)
    visual_keywords: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    blocks: list[BlockVisualBrief] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["blocks"] = [block.to_dict() for block in self.blocks]
        return payload


def build_book_visual_brief(
    *,
    book_title: str,
    specs: list[PuzzleSpec],
    style: str,
) -> BookVisualBrief:
    """Build a deterministic visual brief from book title, block titles, facts and words."""
    subject = _derive_subject(book_title, [])
    subject_keywords = _subject_keywords(subject)
    blocks = _group_specs_by_block(specs)
    all_text_parts = [book_title]
    for spec in specs:
        all_text_parts.extend([spec.title, spec.fact, *spec.words])
        if spec.block_name:
            all_text_parts.append(spec.block_name)

    content_keywords = [] if _looks_like_qa_fixture(all_text_parts) else _rank_keywords(
        all_text_parts,
        limit=MAX_KEYWORDS,
        suppress_layout_terms=True,
    )
    keywords = _merge_keywords(subject_keywords, content_keywords, limit=MAX_KEYWORDS)
    style_hints = _STYLE_HINTS.get(style, _STYLE_HINTS["mock-editorial"])
    tone = _derive_tone(style)

    block_briefs: list[BlockVisualBrief] = []
    for block_name, block_specs in blocks:
        block_text_parts = [block_name]
        for spec in block_specs:
            block_text_parts.extend([spec.title, spec.fact, *spec.words])
        block_content_keywords = [] if _looks_like_qa_fixture(block_text_parts) else _rank_keywords(
            block_text_parts,
            limit=MAX_BLOCK_KEYWORDS,
            suppress_layout_terms=True,
        )
        block_keywords = _merge_keywords(subject_keywords, block_content_keywords, limit=MAX_BLOCK_KEYWORDS)
        block_briefs.append(
            BlockVisualBrief(
                slug=slugify(block_name),
                name=block_name,
                puzzle_count=len(block_specs),
                keywords=block_keywords,
                sample_titles=[spec.title for spec in block_specs[:3]],
                visual_direction=_build_visual_direction(
                    subject=subject,
                    block_name=block_name,
                    keywords=block_keywords,
                    style_hints=style_hints,
                ),
            )
        )

    return BookVisualBrief(
        book_title=book_title,
        style=style,
        subject=subject,
        tone=tone,
        keywords=keywords,
        visual_keywords=[*style_hints, *_visual_keywords_from_content(keywords)],
        avoid=[
            "readable text",
            "letters or numbers",
            "logos",
            "watermarks",
            "busy center area",
            "high contrast pattern behind puzzle grid",
            "photorealistic faces",
            "copyrighted characters",
        ],
        blocks=block_briefs,
    )


def _group_specs_by_block(specs: list[PuzzleSpec]) -> list[tuple[str, list[PuzzleSpec]]]:
    grouped: list[tuple[str, list[PuzzleSpec]]] = []
    index_by_name: dict[str, int] = {}
    for spec in specs:
        block_name = spec.block_name or "default"
        if block_name not in index_by_name:
            index_by_name[block_name] = len(grouped)
            grouped.append((block_name, []))
        grouped[index_by_name[block_name]][1].append(spec)
    return grouped


def _rank_keywords(text_parts: Iterable[str], *, limit: int, suppress_layout_terms: bool = False) -> list[str]:
    counter: Counter[str] = Counter()
    first_seen: dict[str, int] = {}
    order = 0
    ignored = _GENERIC_STOPWORDS | (_LAYOUT_TEST_STOPWORDS if suppress_layout_terms else set())
    for part in text_parts:
        for token in _tokenize(part):
            if token in ignored or len(token) < 3:
                continue
            counter[token] += 1
            first_seen.setdefault(token, order)
            order += 1
    ranked = sorted(counter, key=lambda token: (-counter[token], first_seen[token], token))
    return ranked[:limit]


def _looks_like_qa_fixture(text_parts: Iterable[str]) -> bool:
    tokens = _tokenize(" ".join(text_parts))
    if not tokens:
        return False
    qa_hits = sum(1 for token in tokens if token in _LAYOUT_TEST_STOPWORDS)
    return qa_hits >= 3


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())


def _derive_subject(book_title: str, keywords: list[str]) -> str:
    clean_title = re.sub(r"\b(word|search|puzzle|puzzles|collection|book)\b", "", book_title, flags=re.IGNORECASE)
    clean_title = re.sub(r"\s+", " ", clean_title).strip(" -:|")
    if clean_title:
        return clean_title
    return " ".join(keywords[:3]) or "general knowledge"


def _subject_keywords(subject: str) -> list[str]:
    return _rank_keywords([subject], limit=6, suppress_layout_terms=False)


def _merge_keywords(primary: list[str], secondary: list[str], *, limit: int) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for keyword in [*primary, *secondary]:
        if keyword in seen:
            continue
        seen.add(keyword)
        merged.append(keyword)
        if len(merged) >= limit:
            break
    return merged


def _derive_tone(style: str) -> str:
    if "historical" in style:
        return "educational, elegant, historical, print-friendly"
    if "kids" in style:
        return "educational, playful, clear, print-friendly"
    if "premium" in style:
        return "educational, refined, calm, print-friendly"
    return "educational, clean, low-contrast, print-friendly"


def _visual_keywords_from_content(keywords: list[str]) -> list[str]:
    return [f"subtle motif inspired by {keyword}" for keyword in keywords[:5]]


def _build_visual_direction(
    *,
    subject: str,
    block_name: str,
    keywords: list[str],
    style_hints: list[str],
) -> str:
    keyword_text = ", ".join(keywords[:5]) if keywords else "general themed concepts"
    style_text = ", ".join(style_hints[:3])
    return (
        f"Create a visual direction for '{block_name}' within a '{subject}' word search book: "
        f"{style_text}; subtle motifs based on {keyword_text}; low contrast and clear center area."
    )
