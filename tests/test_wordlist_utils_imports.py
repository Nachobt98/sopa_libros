from wordsearch.cli.simple import main as simple_cli_main
from wordsearch.cli.thematic import main as thematic_cli_main
from wordsearch.cli.wordlist_prompts import prompt_wordlists
from wordsearch.io.wordlists import load_wordlists_from_txt
from wordsearch.utils.slug import slugify
from wordsearch.validation.simple_wordlists import validate_wordlists_for_grid


def test_new_wordlist_modules_are_importable():
    assert callable(load_wordlists_from_txt)
    assert callable(prompt_wordlists)
    assert callable(simple_cli_main)
    assert callable(thematic_cli_main)
    assert callable(slugify)
    assert callable(validate_wordlists_for_grid)


def test_load_wordlists_from_txt_splits_blank_line_blocks(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("cat\ndog\n\nsun\nmoon\n", encoding="utf-8")

    assert load_wordlists_from_txt(str(path)) == [["cat", "dog"], ["sun", "moon"]]


def test_slugify_builds_safe_name():
    assert slugify(" Black History: Vol. 1 ") == "black_history_vol_1"
    assert slugify("") == "book"
    assert slugify(None) == "book"


def test_validate_wordlists_for_grid_reports_oversized_words_without_mutating_input():
    wordlists = [["small", "too long"], ["fitted"]]

    problems = validate_wordlists_for_grid(wordlists, grid_size=6)

    assert wordlists == [["small", "too long"], ["fitted"]]
    assert problems == [
        {
            "list_index": 0,
            "word": "too long",
            "clean_word": "toolong",
            "length": 7,
        }
    ]
