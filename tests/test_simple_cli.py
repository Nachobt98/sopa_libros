import builtins

from wordsearch.cli import simple
from wordsearch.generation.difficulty import DifficultyLevel


def _mock_inputs(monkeypatch, values):
    answers = iter(values)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(answers))


def test_ask_book_title_uses_default_when_empty(monkeypatch):
    _mock_inputs(monkeypatch, [""])

    assert simple._ask_book_title() == "Wordsearch Book"


def test_ask_book_title_strips_custom_value(monkeypatch):
    _mock_inputs(monkeypatch, ["  Sharks Vol 1  "])

    assert simple._ask_book_title() == "Sharks Vol 1"


def test_ask_difficulty_returns_selected_level(monkeypatch):
    _mock_inputs(monkeypatch, ["2"])

    assert simple._ask_difficulty() is DifficultyLevel.MEDIUM


def test_ask_difficulty_falls_back_to_easy_on_invalid_input(monkeypatch):
    _mock_inputs(monkeypatch, ["not-a-number"])

    assert simple._ask_difficulty() is DifficultyLevel.EASY


def test_ask_total_puzzles_uses_wordlist_count_for_txt_source():
    assert simple._ask_total_puzzles(source_type="txt", wordlist_count=4) == 4


def test_ask_total_puzzles_uses_default_when_empty(monkeypatch):
    _mock_inputs(monkeypatch, [""])

    assert simple._ask_total_puzzles(source_type="manual", wordlist_count=1) == 10


def test_ask_total_puzzles_retries_until_positive_integer(monkeypatch):
    _mock_inputs(monkeypatch, ["0", "abc", "6"])

    assert simple._ask_total_puzzles(source_type="manual", wordlist_count=1) == 6


def test_main_builds_options_and_delegates_generation(monkeypatch):
    generated_options = []

    _mock_inputs(monkeypatch, ["Animals", "3", "8"])
    monkeypatch.setattr(simple, "ask_grid_size", lambda _settings: 15)
    monkeypatch.setattr(
        simple,
        "prompt_wordlists",
        lambda predefined_wordlists: ([predefined_wordlists[0]], "manual"),
    )
    monkeypatch.setattr(simple, "generate_simple_book", generated_options.append)

    simple.main()

    assert len(generated_options) == 1
    options = generated_options[0]
    assert options.book_title == "Animals"
    assert options.difficulty is DifficultyLevel.HARD
    assert options.grid_size == 15
    assert options.wordlists == [["gato", "perro", "casa", "luna", "sol", "arbol", "cielo", "mar"]]
    assert options.total_puzzles == 8
