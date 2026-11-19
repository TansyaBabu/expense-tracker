import argparse
import sys
from datetime import date
from pathlib import Path

from expense_tracker.models import Expense
from expense_tracker.storage import (
    DEFAULT_STORAGE_PATH,
    load_expenses,
    next_id,
    save_expenses,
)
from expense_tracker.validation import (
    validate_amount,
    validate_category,
    validate_date,
    validate_date_range,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense_tracker",
        description="Command-line expense tracker",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument(
        "--amount", required=True, help="Expense amount (e.g. 12.50)"
    )
    add_parser.add_argument("--category", required=True, help="Expense category")
    add_parser.add_argument(
        "--date",
        default=None,
        help="Expense date (YYYY-MM-DD, defaults to today)",
    )
    add_parser.add_argument("--note", default=None, help="Optional note")

    # list
    list_parser = subparsers.add_parser("list", help="List expenses")
    list_parser.add_argument("--category", default=None, help="Filter by category")
    list_parser.add_argument(
        "--from",
        dest="from_date",
        default=None,
        help="Filter from date (YYYY-MM-DD)",
    )
    list_parser.add_argument(
        "--to",
        dest="to_date",
        default=None,
        help="Filter to date (YYYY-MM-DD)",
    )

    return parser


def handle_add(args: argparse.Namespace, data_file: Path) -> int:
    amount = validate_amount(args.amount)
    category = validate_category(args.category)
    date_str = validate_date(
        args.date if args.date is not None else date.today().isoformat()
    )

    expenses = load_expenses(data_file)
    new_id = next_id(expenses)
    new_expense = Expense(
        id=new_id,
        amount=amount,
        category=category,
        date=date_str,
        note=args.note,
    )
    expenses.append(new_expense)
    save_expenses(data_file, expenses)
    print(f"Expense added with ID {new_id}.")
    return 0


def handle_list(args: argparse.Namespace, data_file: Path) -> int:
    category_filter = None
    if args.category is not None:
        category_filter = validate_category(args.category)

    validate_date_range(args.from_date, args.to_date)

    expenses = load_expenses(data_file)
    if category_filter is not None:
        expenses = [e for e in expenses if e.category == category_filter]
    if args.from_date is not None:
        expenses = [e for e in expenses if e.date >= args.from_date]
    if args.to_date is not None:
        expenses = [e for e in expenses if e.date <= args.to_date]

    for e in expenses:
        note_part = f" | {e.note}" if e.note else ""
        print(f"{e.id} | {e.date} | {e.category} | {e.amount:.2f}{note_part}")
    return 0


def main(argv: list[str] | None = None, data_file: Path | str | None = None) -> int:
    target_data_file = (
        Path(data_file) if data_file is not None else DEFAULT_STORAGE_PATH
    )
    parser = build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2

    try:
        if args.command == "add":
            return handle_add(args, target_data_file)
        if args.command == "list":
            return handle_list(args, target_data_file)
        return 0
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    except OSError as e:
        sys.stderr.write(f"Could not access data file: {e}\n")
        return 1
