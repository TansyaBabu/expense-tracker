# Expense Tracker CLI

A lightweight command-line expense tracker using Python's standard library.

## Requirements
- Python 3.14+
- Dev dependencies: `pytest`, `ruff`

## Setup
```bash
pip install -r requirements-dev.txt
```

## Usage
```bash
python -m expense_tracker <command> [options]
```

### Commands
- `add --amount <amount> --category <category> --date <YYYY-MM-DD> [--note <note>]`
- `list [--category <category>] [--from <YYYY-MM-DD>] [--to <YYYY-MM-DD>]`
- `summary`
- `edit <id> [--amount <amount>] [--category <category>] [--date <date>] [--note <note>]`
- `delete <id>`

## Development
- Run tests: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .`
