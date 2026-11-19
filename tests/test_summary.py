from decimal import Decimal

from expense_tracker.models import Expense
from expense_tracker.summary import total_by_category, total_by_month


def test_total_by_category_empty() -> None:
    assert total_by_category([]) == {}


def test_total_by_category_multiple() -> None:
    expenses = [
        Expense(
            id=1,
            amount=Decimal("12.50"),
            category="food",
            date="2026-11-19",
        ),
        Expense(
            id=2,
            amount=Decimal("10.00"),
            category="food",
            date="2026-11-20",
        ),
        Expense(
            id=3,
            amount=Decimal("50.00"),
            category="transport",
            date="2026-11-21",
        ),
        Expense(
            id=4,
            amount=Decimal("5.25"),
            category="entertainment",
            date="2026-11-21",
        ),
    ]

    totals = total_by_category(expenses)
    assert totals == {
        "food": Decimal("22.50"),
        "transport": Decimal("50.00"),
        "entertainment": Decimal("5.25"),
    }
    for val in totals.values():
        assert isinstance(val, Decimal)


def test_total_by_month_empty() -> None:
    assert total_by_month([]) == {}


def test_total_by_month_multiple() -> None:
    expenses = [
        Expense(
            id=1,
            amount=Decimal("50.00"),
            category="electronics",
            date="2026-10-15",
        ),
        Expense(
            id=2,
            amount=Decimal("12.50"),
            category="food",
            date="2026-11-01",
        ),
        Expense(
            id=3,
            amount=Decimal("10.00"),
            category="food",
            date="2026-11-19",
        ),
        Expense(
            id=4,
            amount=Decimal("100.00"),
            category="travel",
            date="2026-12-25",
        ),
    ]

    totals = total_by_month(expenses)
    assert totals == {
        "2026-10": Decimal("50.00"),
        "2026-11": Decimal("22.50"),
        "2026-12": Decimal("100.00"),
    }
    for val in totals.values():
        assert isinstance(val, Decimal)
