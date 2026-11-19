import re
from datetime import date
from decimal import Decimal, InvalidOperation

DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def validate_amount(val: str | Decimal | int) -> Decimal:
    """Validate and return amount as Decimal with up to 2 decimal places.

    Rejects floats, non-numeric values, NaN, Infinity, negative values,
    zero, and amounts with more than 2 decimal places.
    """
    if isinstance(val, bool):
        raise ValueError("Amount must be a valid number.")

    if isinstance(val, float):
        raise ValueError(
            "Float values are not allowed for money. Use Decimal, int, or str."
        )

    if isinstance(val, str):
        val = val.strip()
        if not val:
            raise ValueError("Amount must be a valid number.")

    try:
        amount = Decimal(val)
    except (InvalidOperation, TypeError) as e:
        raise ValueError("Amount must be a valid number.") from e

    if not amount.is_finite():
        raise ValueError("Amount must be a finite number.")

    if amount <= Decimal(0):
        raise ValueError("Amount must be a positive number.")

    normalized = amount.normalize()
    exponent = normalized.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -2:
        raise ValueError("Amount cannot have more than 2 decimal places.")

    return amount.quantize(Decimal("0.01"))


def validate_date(date_str: str) -> str:
    """Validate that date_str is strictly YYYY-MM-DD and a real calendar date."""
    if not isinstance(date_str, str) or not DATE_PATTERN.match(date_str):
        raise ValueError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
    try:
        date.fromisoformat(date_str)
    except ValueError as e:
        raise ValueError(f"Invalid calendar date '{date_str}': {e}") from e
    return date_str


def validate_category(category: str) -> str:
    """Validate that category is non-empty, returning the stripped string."""
    if not isinstance(category, str):
        raise ValueError("Category must be a string.")
    stripped = category.strip()
    if not stripped:
        raise ValueError("Category cannot be empty.")
    return stripped


def validate_date_range(from_date: str | None, to_date: str | None) -> None:
    """Validate date formats and ensure from_date is not after to_date."""
    if from_date is not None:
        validate_date(from_date)
    if to_date is not None:
        validate_date(to_date)
    if from_date is not None and to_date is not None and from_date > to_date:
        raise ValueError(
            f"--from date ('{from_date}') cannot be after --to date ('{to_date}')."
        )
