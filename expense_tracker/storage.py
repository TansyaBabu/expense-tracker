import json
import os
import tempfile
from decimal import InvalidOperation
from pathlib import Path

from expense_tracker.models import Expense

DEFAULT_STORAGE_PATH = Path("data/expenses.json")


def next_id(expenses: list[Expense]) -> int:
    """Return max existing id + 1, or 1 if empty."""
    return max((e.id for e in expenses), default=0) + 1


def load_expenses(path: Path | str = DEFAULT_STORAGE_PATH) -> list[Expense]:
    """Load expenses from a JSON file. Returns [] if the file does not exist."""
    path = Path(path)
    if not path.is_file():
        return []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError("Corrupted data file: invalid JSON.") from e

    if not isinstance(data, list):
        raise ValueError("Corrupted data file: expected a list of expenses.")

    expenses: list[Expense] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Corrupted data file: record {i} is invalid.")
        try:
            expenses.append(Expense.from_dict(item))
        except (ValueError, TypeError, KeyError, InvalidOperation) as e:
            raise ValueError(f"Corrupted data file: record {i} is invalid.") from e

    return expenses


def save_expenses(path: Path | str, expenses: list[Expense]) -> None:
    """Atomically save expenses using a temporary file in the same directory."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = [e.to_dict() for e in expenses]
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent, prefix="expenses_", suffix=".tmp", text=True
    )
    replaced = False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temp_path, path)
        replaced = True
    finally:
        if not replaced and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
