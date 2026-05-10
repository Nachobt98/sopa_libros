"""CLI entry point for generated asset manifest bootstrapping."""

from __future__ import annotations

import argparse

from wordsearch.asset_generation.pipeline import DEFAULT_ASSET_STYLE, generate_local_assets_for_book
from wordsearch.config.paths import DEFAULT_THEMATIC_WORDLIST
from wordsearch.parsing.thematic import PuzzleParseError


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate local placeholder assets and asset_manifest.json for a thematic word search book."
    )
    parser.add_argument("--title", "-t", required=True, help="Book title used for generated asset metadata and default output naming.")
    parser.add_argument("--input", "-i", dest="input_path", default=DEFAULT_THEMATIC_WORDLIST, help="Path to the thematic TXT file.")
    parser.add_argument("--output", "-o", dest="output_dir", help="Output directory. Defaults to assets/generated/<book_slug>.")
    parser.add_argument("--style", default=DEFAULT_ASSET_STYLE, help="Visual style label stored in prompts and manifest metadata.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        result = generate_local_assets_for_book(
            title=args.title,
            input_path=args.input_path,
            output_dir=args.output_dir,
            style=args.style,
        )
    except FileNotFoundError:
        print(f"ERROR: No se encuentra el fichero: {args.input_path}")
        return
    except PuzzleParseError as exc:
        print(f"ERROR de parseo: {exc}")
        return

    print("\n=== Assets generados ===")
    print(f"Output dir: {result.output_dir}")
    print(f"Manifest: {result.manifest_path}")
    print(f"Prompts: {result.prompt_plan_path}")
    print(f"Bloques: {result.block_count}")
    print(f"Assets PNG: {result.asset_count}")
    print("\nUsa el manifest con:")
    print(f"sopa-libros-thematic --theme-manifest {result.manifest_path} ...")


if __name__ == "__main__":
    main()
