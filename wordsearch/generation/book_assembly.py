"""Render orchestration for thematic book image assets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.config.design import DEFAULT_LAYOUT, DEFAULT_THEME, LayoutConfig, ThemeConfig
from wordsearch.config.paths import build_output_file
from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.page_plan import PagePlan
from wordsearch.rendering.block_cover import render_block_cover
from wordsearch.rendering.front_matter import render_instructions_page, render_table_of_contents
from wordsearch.rendering.puzzle_page import render_page
from wordsearch.rendering.solution_page import render_solution_page
from wordsearch.rendering.title_page import render_title_page
from wordsearch.utils.slug import slugify

TocEntry = Tuple[str, int, bool]


@dataclass
class RenderedBookImages:
    """Rendered image paths ready for PDF assembly."""

    content_imgs: List[str] = field(default_factory=list)
    solution_imgs: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return bool(self.content_imgs and self.solution_imgs)


def build_toc_entries(page_plan: PagePlan) -> List[TocEntry]:
    toc_entries: List[TocEntry] = []
    for block_name in page_plan.blocks_in_order:
        toc_entries.append((block_name, page_plan.block_first_page.get(block_name, 1), True))
    toc_entries.append(("Solutions", page_plan.first_solution_page, True))
    return toc_entries


def _layout_kwargs(layout: LayoutConfig) -> dict:
    """Pass layout only for opt-in non-default formats to preserve historical call shapes."""
    return {"layout": layout} if layout != DEFAULT_LAYOUT else {}


def _global_background(asset_manifest: AssetManifest | None) -> str | None:
    return asset_manifest.resolve_asset_path("book_default_background") if asset_manifest else None


def _block_background(asset_manifest: AssetManifest | None, block_name: str, fallback: str | None) -> str | None:
    return asset_manifest.background_for_block(block_name, fallback=fallback) if asset_manifest else fallback


def _block_cover_background(asset_manifest: AssetManifest | None, block_name: str, fallback: str | None) -> str | None:
    return asset_manifest.cover_background_for_block(block_name, fallback=fallback) if asset_manifest else fallback


def render_thematic_book_images(
    *,
    book_title: str,
    generated_puzzles: List[GeneratedPuzzle],
    page_plan: PagePlan,
    output_dir: str,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
    asset_manifest: AssetManifest | None = None,
) -> RenderedBookImages:
    """Render all PNG page assets for the thematic book."""
    rendered = RenderedBookImages()
    layout_kwargs = _layout_kwargs(layout)
    global_background = _global_background(asset_manifest)

    title_page_filename = build_output_file(output_dir, "00_title_page.png")
    rendered.content_imgs.append(
        render_title_page(
            book_title,
            filename=title_page_filename,
            background_path=global_background,
            theme=theme,
            **layout_kwargs,
        )
    )

    rendered.content_imgs.extend(
        render_table_of_contents(
            build_toc_entries(page_plan),
            output_dir=output_dir,
            background_path=global_background,
            theme=theme,
            **layout_kwargs,
        )
    )

    instr_filename = build_output_file(output_dir, "02_instructions.png")
    rendered.content_imgs.append(
        render_instructions_page(
            book_title,
            filename=instr_filename,
            background_path=global_background,
            theme=theme,
            **layout_kwargs,
        )
    )

    current_block_name = ""
    block_index = 0
    total_puzzles = len(generated_puzzles)

    for generated in generated_puzzles:
        spec = generated.spec
        print(f"Renderizando puzzle {spec.index + 1}/{total_puzzles}: {spec.title}")

        block_name = getattr(spec, "block_name", "") or ""
        declared_bg_path = getattr(spec, "block_background", None)
        bg_path = _block_background(asset_manifest, block_name, declared_bg_path)

        if block_name and block_name != current_block_name:
            current_block_name = block_name
            block_index += 1
            block_cover_filename = build_output_file(
                output_dir,
                f"block_{block_index:02d}_{slugify(block_name)}.png",
            )
            rendered.content_imgs.append(
                render_block_cover(
                    block_name=block_name,
                    block_index=block_index,
                    filename=block_cover_filename,
                    background_path=_block_cover_background(asset_manifest, block_name, declared_bg_path),
                    theme=theme,
                    **layout_kwargs,
                )
            )

        solution_page_number = page_plan.first_solution_page + spec.index
        puzzle_filename = build_output_file(output_dir, f"puzzle_{spec.index + 1}.png")
        solution_filename = build_output_file(output_dir, f"puzzle_{spec.index + 1}_sol.png")

        rendered.content_imgs.append(
            render_page(
                generated.grid,
                spec.words,
                spec.index + 1,
                filename=puzzle_filename,
                puzzle_title=spec.title,
                fun_fact=spec.fact,
                solution_page_number=solution_page_number,
                background_path=bg_path,
                theme=theme,
                **layout_kwargs,
            )
        )

        rendered.solution_imgs.append(
            render_solution_page(
                generated.grid,
                spec.words,
                spec.index + 1,
                filename=solution_filename,
                placed_words=generated.placed_words,
                puzzle_title=spec.title,
                background_path=bg_path,
                theme=theme,
                **layout_kwargs,
            )
        )

    return rendered
