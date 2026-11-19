# Expense Tracker CLI

## Project overview
Command-line expense tracker. Add, list, edit, delete and summarise
expenses. Data is stored in a local JSON file at `data/expenses.json`.

## Tech stack
- Python 3.14.6
- argparse (standard library) for the CLI
- pytest for tests, ruff for lint and format
- No other runtime dependencies

## Commands
- Run: `python -m expense_tracker <command>`
- Test: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .`

## Folder structure
- `expense_tracker/` – app code (cli.py, storage.py, models.py, validation.py, summary.py)
- `tests/` – pytest tests, one test file per module
- `data/` – local JSON storage (gitignored)
- `.githooks/` – versioned git hooks; pre-commit runs `ruff format --check .`. Enable once per clone with `git config core.hooksPath .githooks`
- `.agents/skills/` – add-feature and commit-message-writer skills

## Key decisions
- Decimal in memory, "12.50" strings in JSON
- CLI entrypoint: `main(argv=None, data_file=None) -> int` in cli.py
- Summary & aggregation logic lives in summary.py
- IDs: dynamic `max(remaining) + 1`; deleting highest ID allows it to be reused

## Code style
- Type hints on all functions
- Small functions, one job each
- Use `Decimal` for money, never float
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