import json
import os
from decimal import Decimal
from pathlib import Path

import pytest

from expense_tracker.models import Expense
from expense_tracker.storage import (
    DEFAULT_STORAGE_PATH,
    load_expenses,
    next_id,
    save_expenses,
)


def test_default_storage_path() -> None:
    assert DEFAULT_STORAGE_PATH == Path("data/expenses.json")


def test_load_expenses_missing_file(tmp_path: Path) -> None:
    non_existent = tmp_path / "expenses.json"
    assert load_expenses(non_existent) == []


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    expenses = [
        Expense(
            id=1,
            amount=Decimal("12.50"),
            category="food",
            date="2026-11-19",
            note="lunch",
        ),
        Expense(
            id=2,
            amount=Decimal("45.00"),
            category="transport",
            date="2026-11-20",
            note=None,
        ),
    ]

    save_expenses(expenses_file, expenses)
    loaded = load_expenses(expenses_file)

    assert loaded == expenses
    assert isinstance(loaded[0].amount, Decimal)
    assert isinstance(loaded[1].amount, Decimal)
    assert loaded[0].amount == Decimal("12.50")
    assert loaded[1].amount == Decimal("45.00")


def test_amounts_stored_as_strings_in_json(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    expenses = [
        Expense(
            id=1,
            amount=Decimal("12.50"),
            category="food",
            date="2026-11-19",
        ),
        Expense(
            id=2,
            amount=Decimal("5.00"),
            category="coffee",
            date="2026-11-19",
        ),
    ]

    save_expenses(expenses_file, expenses)

    # Inspect raw file content directly
    raw_content = expenses_file.read_text(encoding="utf-8")
    assert '"amount": "12.50"' in raw_content
    assert '"amount": "5.00"' in raw_content

    # Inspect parsed json values
    raw_json = json.loads(raw_content)
    assert isinstance(raw_json[0]["amount"], str)
    assert isinstance(raw_json[1]["amount"], str)
    assert raw_json[0]["amount"] == "12.50"
    assert raw_json[1]["amount"] == "5.00"


def test_next_id_empty_and_non_empty() -> None:
    assert next_id([]) == 1

    expenses = [
        Expense(
            id=1,
            amount=Decimal("10.00"),
            category="food",
            date="2026-11-19",
        ),
        Expense(
            id=5,
            amount=Decimal("20.00"),
            category="transport",
            date="2026-11-19",
        ),
    ]
    assert next_id(expenses) == 6


def test_load_expenses_corrupt_json(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    expenses_file.write_text("{this is not valid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Corrupted data file: invalid JSON."):
        load_expenses(expenses_file)


def test_load_expenses_non_list_top_level(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    expenses_file.write_text('{"expenses": []}', encoding="utf-8")

    with pytest.raises(
        ValueError, match="Corrupted data file: expected a list of expenses."
    ):
        load_expenses(expenses_file)


def test_load_expenses_non_dict_item(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    raw_data = [
        {"id": 1, "amount": "12.50", "category": "food", "date": "2026-11-19"},
        "not a dict item",
    ]
    expenses_file.write_text(json.dumps(raw_data), encoding="utf-8")

    with pytest.raises(ValueError, match="Corrupted data file: record 1 is invalid."):
        load_expenses(expenses_file)


def test_load_expenses_invalid_amount_record(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    raw_data = [{"id": 1, "amount": "abc", "category": "food", "date": "2026-11-19"}]
    expenses_file.write_text(json.dumps(raw_data), encoding="utf-8")

    with pytest.raises(ValueError, match="Corrupted data file: record 0 is invalid."):
        load_expenses(expenses_file)


def test_failed_save_leaves_existing_file_loadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expenses_file = tmp_path / "expenses.json"
    initial_expenses = [
        Expense(
            id=1,
            amount=Decimal("10.00"),
            category="food",
            date="2026-11-19",
        )
    ]
    save_expenses(expenses_file, initial_expenses)
    assert load_expenses(expenses_file) == initial_expenses

    def broken_replace(src: str | Path, dst: str | Path) -> None:
        raise OSError("Simulated disk replacement failure")

    monkeypatch.setattr(os, "replace", broken_replace)

    new_expenses = [
        Expense(
            id=2,
            amount=Decimal("99.99"),
            category="electronics",
            date="2026-11-20",
        )
    ]
    with pytest.raises(OSError, match="Simulated disk replacement failure"):
        save_expenses(expenses_file, new_expenses)

    # Existing file must remain unmodified and fully loadable
    assert load_expenses(expenses_file) == initial_expenses

    # Ensure no leftover temp files remained
    temp_files = list(tmp_path.glob("expenses_*.tmp"))
    assert temp_files == []


def test_delete_highest_id_and_reuse(tmp_path: Path) -> None:
    expenses_file = tmp_path / "expenses.json"
    expenses = [
        Expense(id=1, amount=Decimal("10.00"), category="c1", date="2026-11-19"),
        Expense(id=2, amount=Decimal("20.00"), category="c2", date="2026-11-19"),
        Expense(id=3, amount=Decimal("30.00"), category="c3", date="2026-11-19"),
    ]

    # Save [1, 2, 3]
    save_expenses(expenses_file, expenses)

    # Remove ID 3
    expenses = [e for e in expenses if e.id != 3]

    # Save [1, 2]
    save_expenses(expenses_file, expenses)

    # Reload from disk
    reloaded = load_expenses(expenses_file)

    # Assert next_id == 3
    assert next_id(reloaded) == 3

    # Add an expense with ID generated by next_id
    new_expense = Expense(
        id=next_id(reloaded),
        amount=Decimal("40.00"),
        category="c3_new",
        date="2026-11-20",
    )
    assert new_expense.id == 3

    reloaded.append(new_expense)
    save_expenses(expenses_file, reloaded)

    final_reloaded = load_expenses(expenses_file)
    assert [e.id for e in final_reloaded] == [1, 2, 3]


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    nested_file = tmp_path / "deeply" / "nested" / "dir" / "expenses.json"
    expenses = [
        Expense(id=1, amount=Decimal("15.00"), category="books", date="2026-11-19")
    ]
    save_expenses(nested_file, expenses)
    assert nested_file.is_file()
    assert load_expenses(nested_file) == expenses
