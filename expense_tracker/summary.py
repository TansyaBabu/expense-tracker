from decimal import Decimal

from expense_tracker.models import Expense


def total_by_category(expenses: list[Expense]) -> dict[str, Decimal]:
    """Calculate total expenses grouped by category."""
    totals: dict[str, Decimal] = {}
    for expense in expenses:
        totals[expense.category] = (
            totals.get(expense.category, Decimal("0")) + expense.amount
        )
    return totals


def total_by_month(expenses: list[Expense]) -> dict[str, Decimal]:
    """Calculate total expenses grouped by month (YYYY-MM)."""
    totals: dict[str, Decimal] = {}
    for expense in expenses:
        month = expense.date[:7]
        totals[month] = totals.get(month, Decimal("0")) + expense.amount
    return totals
