# Expense Tracker CLI

A lightweight command-line expense tracker built with Python's standard library. Expense data is stored locally in `data/expenses.json`.

## Setup (Windows, Git Bash)

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements-dev.txt
```

## Usage

Run commands with `python -m expense_tracker <command> [options]`:

### Commands
- `python -m expense_tracker add --amount 12.50 --category food --date 2026-11-19 --note lunch`
- `python -m expense_tracker list [--category food] [--from 2026-11-01] [--to 2026-11-30]`
- `python -m expense_tracker summary [--by category|month]`
- `python -m expense_tracker edit 1 --amount 15.00`
- `python -m expense_tracker edit 1 --note ""   (clears the note)`
- `python -m expense_tracker delete 1`

## Exit Codes

- `0`: Success.
- `1`: Validation or data error (message on stderr).
- `2`: Usage error.

## Testing and Checks

- `pytest -q`
- `ruff check .`
- `ruff format --check .`

## Known Limitations

- `--note` cannot start with a dash (argparse reads it as an option).
- The git pre-commit hook is not versioned; re-create it from the README if you clone the repo.
- `.venv/Scripts/python.exe` paths are Windows-specific.
- Antigravity did not load `.agents/hooks.json` in this environment; the formatter runs through the git pre-commit hook instead.

## AI Workflow

- **`AGENTS.md`**: Project rules, tech stack constraints, code style standards, and definition of done for coding agents.
- **`add-feature` skill**: Step-by-step workflow for restating goals, proposing plans, awaiting approval, and implementing features with tests.
- **`commit-message-writer` skill**: Conventions and rules for generating concise, conventional git commit messages.
- **Git pre-commit hook**: Automated script running `ruff format .` and `ruff check .` before each commit to enforce code quality.
