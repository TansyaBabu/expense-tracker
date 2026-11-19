from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class Expense:
    id: int
    amount: Decimal
    category: str
    date: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        # Validation (a later step) rejects amounts with more than 2 decimals.
        return {
            "id": self.id,
            "amount": f"{self.amount:.2f}",
            "category": self.category,
            "date": self.date,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Expense":
        return cls(
            id=int(data["id"]),
            amount=Decimal(str(data["amount"])),
            category=str(data["category"]),
            date=str(data["date"]),
            note=data.get("note"),
        )
