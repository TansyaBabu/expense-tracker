from decimal import Decimal

from expense_tracker.models import Expense


def test_expense_creation() -> None:
    expense = Expense(
        id=1,
        amount=Decimal("12.50"),
        category="food",
        date="2026-11-19",
    )
    assert expense.id == 1
    assert expense.amount == Decimal("12.50")
    assert expense.category == "food"
    assert expense.date == "2026-11-19"
    assert expense.note is None

    expense_with_note = Expense(
        id=2,
        amount=Decimal("45.00"),
        category="transport",
        date="2026-11-20",
        note="taxi to airport",
    )
    assert expense_with_note.note == "taxi to airport"


def test_expense_to_dict_stores_amount_as_string() -> None:
    expense = Expense(
        id=1,
        amount=Decimal("12.50"),
        category="food",
        date="2026-11-19",
        note="lunch",
    )
    data = expense.to_dict()
    assert data == {
        "id": 1,
        "amount": "12.50",
        "category": "food",
        "date": "2026-11-19",
        "note": "lunch",
    }

    # Ensure whole numbers are formatted with two decimals
    expense_whole = Expense(
        id=2,
        amount=Decimal("5"),
        category="groceries",
        date="2026-11-19",
    )
    assert expense_whole.to_dict()["amount"] == "5.00"


def test_expense_from_dict_parses_amount_to_decimal() -> None:
    data = {
        "id": 1,
        "amount": "12.50",
        "category": "food",
        "date": "2026-11-19",
        "note": "lunch",
    }
    expense = Expense.from_dict(data)
    assert expense.id == 1
    assert expense.amount == Decimal("12.50")
    assert isinstance(expense.amount, Decimal)
    assert expense.category == "food"
    assert expense.date == "2026-11-19"
    assert expense.note == "lunch"

    # Verify round-trip conversion
    assert Expense.from_dict(expense.to_dict()) == expense
