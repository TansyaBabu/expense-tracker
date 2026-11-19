import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

from expense_tracker.models import Expense
from expense_tracker.storage import (
    DEFAULT_STORAGE_PATH,
    load_expenses,
    next_id,
    save_expenses,
)
from expense_tracker.summary import total_by_category, total_by_month
from expense_tracker.validation import (
    validate_amount,
    validate_category,
    validate_date,
    validate_date_range,
)

# Ensure Expense.from_dict validates date with validate_date
_orig_from_dict = Expense.from_dict


@classmethod
def _validated_from_dict(cls: type[Expense], data: dict[str, Any]) -> Expense:
    expense = _orig_from_dict(data)
    validate_date(expense.date)
    return expense


Expense.from_dict = _validated_from_dict


def load_and_validate_expenses(data_file: Path) -> list[Expense]:
    expenses = load_expenses(data_file)
    for i, e in enumerate(expenses):
        try:
            validate_date(e.date)
        except ValueError as err:
            raise ValueError(f"Corrupted data file: record {i} is invalid.") from err
    return expenses


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

    # summary
    summary_parser = subparsers.add_parser("summary", help="Summarise expenses")
    summary_parser.add_argument(
        "--by",
        choices=["category", "month"],
        default="category",
        help="Group summary by category or month (default: category)",
    )

    # edit
    edit_parser = subparsers.add_parser("edit", help="Edit an existing expense")
    edit_parser.add_argument("id", type=int, help="Expense ID to edit")
    edit_parser.add_argument("--amount", default=None, help="New amount")
    edit_parser.add_argument("--category", default=None, help="New category")
    edit_parser.add_argument("--date", default=None, help="New date (YYYY-MM-DD)")
    edit_parser.add_argument("--note", default=None, help="New note")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete an existing expense")
    delete_parser.add_argument("id", type=int, help="Expense ID to delete")

    return parser


def handle_add(args: argparse.Namespace, data_file: Path) -> int:
    amount = validate_amount(args.amount)
    category = validate_category(args.category)
    date_str = validate_date(
        args.date if args.date is not None else date.today().isoformat()
    )

    expenses = load_and_validate_expenses(data_file)
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

    expenses = load_and_validate_expenses(data_file)
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


def handle_summary(args: argparse.Namespace, data_file: Path) -> int:
    expenses = load_and_validate_expenses(data_file)
    if not expenses:
        return 0

    if args.by == "month":
        totals = total_by_month(expenses)
    else:
        totals = total_by_category(expenses)

    for key in sorted(totals.keys()):
        print(f"{key}: {totals[key]:.2f}")
    return 0


def handle_edit(args: argparse.Namespace, data_file: Path) -> int:
    if args.id <= 0:
        raise ValueError("Expense ID must be a positive integer.")

    if (
        args.amount is None
        and args.category is None
        and args.date is None
        and args.note is None
    ):
        raise ValueError("Nothing to change.")

    new_amount = validate_amount(args.amount) if args.amount is not None else None
    new_category = (
        validate_category(args.category) if args.category is not None else None
    )
    new_date = validate_date(args.date) if args.date is not None else None
    new_note = None
    if args.note is not None:
        new_note = None if args.note == "" else args.note

    expenses = load_and_validate_expenses(data_file)
    target = next((e for e in expenses if e.id == args.id), None)
    if target is None:
        raise ValueError(f"Expense with ID {args.id} not found.")

    if new_amount is not None:
        target.amount = new_amount
    if new_category is not None:
        target.category = new_category
    if new_date is not None:
        target.date = new_date
    if args.note is not None:
        target.note = new_note

    save_expenses(data_file, expenses)
    print(f"Expense {args.id} updated.")
    return 0


def handle_delete(args: argparse.Namespace, data_file: Path) -> int:
    if args.id <= 0:
        raise ValueError("Expense ID must be a positive integer.")

    expenses = load_and_validate_expenses(data_file)
    target = next((e for e in expenses if e.id == args.id), None)
    if target is None:
        raise ValueError(f"Expense with ID {args.id} not found.")

    expenses = [e for e in expenses if e.id != args.id]
    save_expenses(data_file, expenses)
    print(f"Expense {args.id} deleted.")
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
        if args.command == "summary":
            return handle_summary(args, target_data_file)
        if args.command == "edit":
            return handle_edit(args, target_data_file)
        if args.command == "delete":
            return handle_delete(args, target_data_file)
        return 0
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    except OSError as e:
        sys.stderr.write(f"Could not access data file: {e}\n")
        return 1
