# Expense Tracker CLI: Spec

## Commands
- `add --amount 12.50 --category food --date 2026-11-19 [--note "lunch"]`
- `list [--category food] [--from 2026-11-01] [--to 2026-11-30]`
- `summary` (total by category and by month)
- `edit <id> [--amount ...] [--category ...] [--date ...] [--note ...]`
- `delete <id>`

## Data
- Expense: id (int, auto-increment), amount, category, date (YYYY-MM-DD), note (optional)
- Stored in `data/expenses.json`; file is created if missing

## Validation (clear error messages, no tracebacks)
- Amount must be a positive number
- Date must be a valid YYYY-MM-DD date
- Category must not be empty
- Unknown ID on edit or delete gives an error
- `--from` must not be after `--to`

## Out of scope for now
- Stretch goals (CSV export, budgets, monthly report)

## Tests (at least 8)
- add, list filters, summary, edit, delete, plus edge cases:
  negative amount, bad date, unknown ID, empty file, corrupted JSON