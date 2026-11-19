# Expense Tracker CLI

A lightweight command-line expense tracker built with Python's standard library. Expense data is stored locally in `data/expenses.json`.

## Setup (Windows, Git Bash)

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements-dev.txt
git config core.hooksPath .githooks
```

Run the last command once after cloning to enable the pre-commit formatting check.

## Usage

Run commands with `python -m expense_tracker <command> [options]`:

- `python -m expense_tracker add --amount 12.50 --category food --date 2026-11-19 --note lunch`
- `python -m expense_tracker list [--category food] [--from 2026-11-01] [--to 2026-11-30]`
- `python -m expense_tracker summary [--by category|month]`
- `python -m expense_tracker edit 1 --amount 15.00`
- `python -m expense_tracker edit 1 --note ""` (clears the note)
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

- `--note` cannot start with a dash, because argparse reads it as an option.
- The pre-commit hook lives in `.githooks/` and is enabled per clone with `git config core.hooksPath .githooks`.
- The `.venv/Scripts/python.exe` path in the hook is Windows-specific.
- Antigravity did not load `.agents/hooks.json` in this environment, so the formatter check runs through the git pre-commit hook instead.

## AI Workflow

- **`AGENTS.md`**: Project rules: tech stack, commands, code style, never-rules, and definition of done.
- **`add-feature` skill**: Restate the goal, propose a plan, wait for approval, implement in small steps, test, and summarise.
- **`commit-message-writer` skill**: Writes a conventional commit message from the staged diff.
- **Pre-commit hook (`.githooks/pre-commit`)**: Runs `ruff format --check .` before each commit and blocks the commit if formatting fails.

The permissions note and reflection are submitted as `Permissions_Note.docx` and `Reflection.docx`.
