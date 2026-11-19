# Expense Tracker CLI

## Project overview
Command-line expense tracker. Add, list, edit, delete and summarise
expenses. Data is stored in a local JSON file.

## Tech stack
- Python <your version>
- argparse (standard library) for the CLI
- pytest for tests, ruff for lint and format
- No other runtime dependencies

## Commands
- Run: `python -m expense_tracker <command>`
- Test: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .`

## Folder structure
- `expense_tracker/` – app code (cli.py, storage.py, models.py, validation.py)
- `tests/` – pytest tests, one test file per module
- `data/` – local JSON storage (gitignored)

## Code style
- Type hints on all functions
- Small functions, one job each
- Use `Decimal` or integer cents for money, never float
- Validation errors raise `ValueError` with a clear message; the CLI
  catches them and prints a friendly error, never a traceback

## Never
- Never commit secrets, tokens or the data file
- Never add a dependency without asking first
- Never change code outside the requested feature
- Never skip or delete a failing test to make the suite pass

## Definition of done
- Feature works from the CLI
- Tests added and `pytest -q` passes
- `ruff check .` and `ruff format --check .` are clean
- README updated if usage changed