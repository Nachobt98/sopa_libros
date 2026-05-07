import builtins
import os
import tempfile
import types
import pytest
from wordsearch.cli import wordlist_prompts

def _mock_inputs(monkeypatch, values):
    answers = iter(values)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(answers))

def test_prompt_wordlists_predefined(monkeypatch):
    predefined = [["cat", "dog"]]
    _mock_inputs(monkeypatch, [""])
    wordlists, source = wordlist_prompts.prompt_wordlists(predefined)
    assert wordlists == predefined
    assert source == "predefined"

def test_prompt_wordlists_manual(monkeypatch):
    predefined = [["cat", "dog"]]
    _mock_inputs(monkeypatch, ["2", "apple, banana, cherry"])
    wordlists, source = wordlist_prompts.prompt_wordlists(predefined)
    assert wordlists == [["apple", "banana", "cherry"]]
    assert source == "manual"

def test_prompt_wordlists_manual_empty(monkeypatch):
    predefined = [["cat", "dog"]]
    _mock_inputs(monkeypatch, ["2", "   "])
    wordlists, source = wordlist_prompts.prompt_wordlists(predefined)
    assert wordlists == predefined
    assert source == "predefined"

def test_prompt_wordlists_txt(monkeypatch, tmp_path):
    predefined = [["cat", "dog"]]
    base_dir = tmp_path / "wordlists"
    base_dir.mkdir()
    file_path = base_dir / "mywords.txt"
    file_path.write_text("apple\nbanana\n\ncarrot\ndate\n", encoding="utf-8")
    monkeypatch.setattr(os, "makedirs", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(os, "listdir", lambda _dir: ["mywords.txt"])
    _mock_inputs(monkeypatch, ["3", "1"])
    monkeypatch.setattr(wordlist_prompts, "load_wordlists_from_txt", lambda path: [["apple", "banana"], ["carrot", "date"]] if "mywords.txt" in path else [])
    wordlists, source = wordlist_prompts.prompt_wordlists(predefined)
    assert wordlists == [["apple", "banana"], ["carrot", "date"]]
    assert source == "txt"

def test_prompt_wordlists_txt_invalid(monkeypatch, tmp_path):
    predefined = [["cat", "dog"]]
    base_dir = tmp_path / "wordlists"
    base_dir.mkdir()
    file_path = base_dir / "bad.txt"
    file_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(os, "makedirs", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(os, "listdir", lambda _dir: ["bad.txt"])
    _mock_inputs(monkeypatch, ["3", "1"])
    monkeypatch.setattr(wordlist_prompts, "load_wordlists_from_txt", lambda path: [])
    wordlists, source = wordlist_prompts.prompt_wordlists(predefined)
    assert wordlists == predefined
    assert source == "predefined"

def test_prompt_wordlists_txt_exception(monkeypatch, tmp_path):
    predefined = [["cat", "dog"]]
    base_dir = tmp_path / "wordlists"
    base_dir.mkdir()
    file_path = base_dir / "fail.txt"
    file_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(os, "makedirs", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(os, "listdir", lambda _dir: ["fail.txt"])
    _mock_inputs(monkeypatch, ["3", "1"])
    def fail_load(path):
        raise Exception("fail")
    monkeypatch.setattr(wordlist_prompts, "load_wordlists_from_txt", fail_load)
    wordlists, source = wordlist_prompts.prompt_wordlists(predefined)
    assert wordlists == predefined
    assert source == "predefined"
