# Development setup

This project is a Python package with a small command-line surface for generating
KDP-ready word search books.

## Recommended local setup

From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e ".[dev]"
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The editable install keeps the local `wordsearch` package importable while
installing runtime and development dependencies from `pyproject.toml`.

## Quality checks

Run the same checks used by CI:

```powershell
py -m ruff check .
py -m pytest --cov=wordsearch --cov-report=term-missing
```

If `py` is not available on Windows, use the Python executable from the active
virtual environment:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest --cov=wordsearch --cov-report=term-missing
```

## Reference generation command

After changes that affect generation, rendering, page planning or output paths,
run the reference command from the manual regression checklist:

```powershell
py main_thematic.py --title "Black History Word Search Collection" --input wordlists/book_block.txt --difficulty medium --grid-size 14
```

Then follow `docs/manual_regression_checklist.md`.
