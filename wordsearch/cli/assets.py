"""CLI entry point for generated asset manifest bootstrapping."""

from __future__ import annotations

import argparse

from wordsearch.asset_generation.pipeline import DEFAULT_ASSET_STYLE, generate_local_assets_for_book
from wordsearch.asset_generation.providers import AVAILABLE_IMAGE_PROVIDERS, LOCAL_PLACEHOLDER_PROVIDER
from wordsearch.asset_generation.user_assets import build_user_asset_manifest_for_book
from wordsearch.config.paths import DEFAULT_THEMATIC_WORDLIST
from wordsearch.parsing.thematic import PuzzleParseError


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate local assets and asset_manifest.json for a thematic word search book."
    )
    parser.add_argument("--title", "-t", required=True, help="Book title used for generated asset metadata and default output naming.")
    parser.add_argument("--input", "-i", dest="input_path", default=DEFAULT_THEMATIC_WORDLIST, help="Path to the thematic TXT file.")
    parser.add_argument("--output", "-o", dest="output_dir", help="Output directory. Defaults to assets/generated/<book_slug>.")
    parser.add_argument("--style", default=DEFAULT_ASSET_STYLE, help="Visual style label stored in prompts and manifest metadata.")
    parser.add_argument(
        "--user-assets-dir",
        help="Directory with user-supplied images to normalize into asset_manifest.json instead of generating placeholders.",
    )
    parser.add_argument(
        "--provider",
        choices=AVAILABLE_IMAGE_PROVIDERS,
        default=LOCAL_PLACEHOLDER_PROVIDER,
        help="Image provider used to create raw assets before normalization.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        if getattr(args, "user_assets_dir", None):
            result = build_user_asset_manifest_for_book(
                title=args.title,
                input_path=args.input_path,
                user_assets_dir=args.user_assets_dir,
                output_dir=args.output_dir,
                style=args.style,
            )
            _print_user_asset_summary(result)
            return

        generated = generate_local_assets_for_book(
            title=args.title,
            input_path=args.input_path,
            output_dir=args.output_dir,
            style=args.style,
            provider_name=args.provider,
        )
    except FileNotFoundError as exc:
        missing_path = exc.filename or (getattr(args, "user_assets_dir", None) or args.input_path)
        print(f"ERROR: No se encuentra el fichero: {missing_path}")
        return
    except NotADirectoryError as exc:
        print(f"ERROR: La ruta de assets no es una carpeta: {exc.filename or getattr(args, 'user_assets_dir', '')}")
        return
    except PuzzleParseError as exc:
        print(f"ERROR de parseo: {exc}")
        return

    print("\n=== Assets generados ===")
    print(f"Output dir: {generated.output_dir}")
    print(f"Manifest: {generated.manifest_path}")
    print(f"Prompts: {generated.prompt_plan_path}")
    print(f"Bloques: {generated.block_count}")
    print(f"Assets PNG: {generated.asset_count}")
    print("\nUsa el manifest con:")
    print(f"sopa-libros-thematic --theme-manifest {generated.manifest_path} ...")


def _print_user_asset_summary(result) -> None:
    print("\n=== Assets de usuario normalizados ===")
    print(f"Output dir: {result.output_dir}")
    print(f"Manifest: {result.manifest_path}")
    print(f"Source map: {result.source_map_path}")
    print(f"Bloques: {result.block_count}")
    print(f"Assets PNG: {result.asset_count}")
    print(f"Avisos: {result.warning_count}")
    print("\nUsa el manifest con:")
    print(f"sopa-libros-thematic --theme-manifest {result.manifest_path} ...")


if __name__ == "__main__":
    main()
