import argparse
import sys

from wordsearch.asset_generation.pipeline import GeneratedAssetSet
from wordsearch.asset_generation.providers import LOCAL_PLACEHOLDER_PROVIDER, OPENAI_PROVIDER
from wordsearch.cli import assets
from wordsearch.parsing.thematic import PuzzleParseError


def test_parse_args_accepts_assets_cli_options(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sopa-libros-assets",
            "--title",
            "Ancient Egypt Word Search",
            "--input",
            "wordlists/egypt.txt",
            "--output",
            "assets/generated/egypt",
            "--style",
            "premium-historical",
            "--provider",
            OPENAI_PROVIDER,
        ],
    )

    args = assets._parse_args()

    assert args.title == "Ancient Egypt Word Search"
    assert args.input_path == "wordlists/egypt.txt"
    assert args.output_dir == "assets/generated/egypt"
    assert args.style == "premium-historical"
    assert args.provider == OPENAI_PROVIDER


def test_main_prints_generated_asset_summary(monkeypatch, capsys):
    monkeypatch.setattr(
        assets,
        "_parse_args",
        lambda: argparse.Namespace(
            title="Book",
            input_path="wordlists/book.txt",
            output_dir="assets/generated/book",
            style="mock-editorial",
            provider=LOCAL_PLACEHOLDER_PROVIDER,
        ),
    )

    def fake_generate_local_assets_for_book(**kwargs):
        assert kwargs == {
            "title": "Book",
            "input_path": "wordlists/book.txt",
            "output_dir": "assets/generated/book",
            "style": "mock-editorial",
            "provider_name": LOCAL_PLACEHOLDER_PROVIDER,
        }
        return GeneratedAssetSet(
            output_dir="assets/generated/book",
            manifest_path="assets/generated/book/asset_manifest.json",
            prompt_plan_path="assets/generated/book/prompts.json",
            asset_count=3,
            block_count=1,
        )

    monkeypatch.setattr(assets, "generate_local_assets_for_book", fake_generate_local_assets_for_book)

    assets.main()

    captured = capsys.readouterr()
    assert "Assets generados" in captured.out
    assert "assets/generated/book/asset_manifest.json" in captured.out
    assert "Assets PNG: 3" in captured.out


def test_main_handles_missing_input_file(monkeypatch, capsys):
    monkeypatch.setattr(
        assets,
        "_parse_args",
        lambda: argparse.Namespace(
            title="Book",
            input_path="missing.txt",
            output_dir=None,
            style="mock-editorial",
            provider=LOCAL_PLACEHOLDER_PROVIDER,
        ),
    )
    monkeypatch.setattr(
        assets,
        "generate_local_assets_for_book",
        lambda **kwargs: (_ for _ in ()).throw(FileNotFoundError),
    )

    assets.main()

    captured = capsys.readouterr()
    assert "ERROR: No se encuentra el fichero: missing.txt" in captured.out


def test_main_handles_parse_errors(monkeypatch, capsys):
    monkeypatch.setattr(
        assets,
        "_parse_args",
        lambda: argparse.Namespace(
            title="Book",
            input_path="bad.txt",
            output_dir=None,
            style="mock-editorial",
            provider=LOCAL_PLACEHOLDER_PROVIDER,
        ),
    )
    monkeypatch.setattr(
        assets,
        "generate_local_assets_for_book",
        lambda **kwargs: (_ for _ in ()).throw(PuzzleParseError("bad puzzle")),
    )

    assets.main()

    captured = capsys.readouterr()
    assert "ERROR de parseo: bad puzzle" in captured.out
