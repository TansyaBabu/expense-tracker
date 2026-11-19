import json
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from expense_tracker.cli import main
from expense_tracker.models import Expense
from expense_tracker.storage import load_expenses, save_expenses


def test_cli_add_creates_expense(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(
        ["add", "--amount", "12.50", "--category", "food", "--note", "lunch"],
        data_file=data_file,
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Expense added with ID 1." in captured.out
    assert captured.err == ""
    assert "Traceback" not in captured.out
    assert "Traceback" not in captured.err

    expenses = load_expenses(data_file)
    assert len(expenses) == 1
    assert expenses[0].id == 1
    assert expenses[0].amount == Decimal("12.50")
    assert expenses[0].category == "food"
    assert expenses[0].date == date.today().isoformat()
    assert expenses[0].note == "lunch"


def test_cli_add_with_explicit_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(
        [
            "add",
            "--amount",
            "45.00",
            "--category",
            "travel",
            "--date",
            "2026-11-19",
        ],
        data_file=data_file,
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Expense added with ID 1." in captured.out
    assert "Traceback" not in captured.out
    assert "Traceback" not in captured.err

    expenses = load_expenses(data_file)
    assert expenses[0].date == "2026-11-19"


def test_cli_add_bad_amount_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(
        ["add", "--amount", "-5.00", "--category", "food"],
        data_file=data_file,
    )
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Amount must be a positive number." in captured.err
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out

    # Failed validation must not read or create/write data file
    assert not data_file.exists()


def test_cli_add_bad_date_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(
        ["add", "--amount", "10.00", "--category", "food", "--date", "2026-1-1"],
        data_file=data_file,
    )
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Invalid date format '2026-1-1'. Expected YYYY-MM-DD." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out
    assert not data_file.exists()


def test_cli_add_bad_category_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(
        ["add", "--amount", "10.00", "--category", "   "],
        data_file=data_file,
    )
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Category cannot be empty." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out
    assert not data_file.exists()


def test_cli_list_all_and_filter_by_category(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(
                id=1,
                amount=Decimal("12.50"),
                category="food",
                date="2026-11-19",
                note="lunch",
            ),
            Expense(
                id=2,
                amount=Decimal("50.00"),
                category="transport",
                date="2026-11-19",
            ),
        ],
    )

    # List all
    exit_code = main(["list"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "1 | 2026-11-19 | food | 12.50 | lunch" in captured.out
    assert "2 | 2026-11-19 | transport | 50.00" in captured.out
    assert captured.err == ""
    assert "Traceback" not in captured.out

    # Filter by category
    exit_code = main(["list", "--category", "food"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "1 | 2026-11-19 | food | 12.50 | lunch" in captured.out
    assert "transport" not in captured.out


def test_cli_list_category_empty_or_whitespace_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(["list", "--category", "  "], data_file=data_file)
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Category cannot be empty." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_list_filter_date_range(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(id=1, amount=Decimal("10.00"), category="c", date="2026-11-01"),
            Expense(id=2, amount=Decimal("20.00"), category="c", date="2026-11-15"),
            Expense(id=3, amount=Decimal("30.00"), category="c", date="2026-11-30"),
        ],
    )

    exit_code = main(
        ["list", "--from", "2026-11-10", "--to", "2026-11-20"],
        data_file=data_file,
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().splitlines() if line]
    assert len(lines) == 1
    assert "2 | 2026-11-15 | c | 20.00" in lines[0]


def test_cli_list_inverted_date_range_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(
        ["list", "--from", "2026-11-30", "--to", "2026-11-01"],
        data_file=data_file,
    )
    assert exit_code == 1

    captured = capsys.readouterr()
    assert (
        "--from date ('2026-11-30') cannot be after --to date ('2026-11-01')."
        in captured.err
    )
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_list_no_matches_prints_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(
                id=1,
                amount=Decimal("10.00"),
                category="food",
                date="2026-11-19",
            )
        ],
    )

    exit_code = main(["list", "--category", "nonexistent"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_cli_usage_error_returns_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    # Missing required --category
    exit_code = main(["add", "--amount", "10.00"], data_file=data_file)
    assert exit_code == 2

    captured = capsys.readouterr()
    assert "usage: expense_tracker" in captured.err
    assert "the following arguments are required: --category" in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_catches_oserror(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    data_file = tmp_path / "expenses.json"

    def fail_load(path: Path | str) -> list[Expense]:
        raise PermissionError("Access denied")

    from expense_tracker import cli

    monkeypatch.setattr(cli, "load_expenses", fail_load)

    exit_code = main(
        ["add", "--amount", "10.00", "--category", "food"],
        data_file=data_file,
    )
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Could not access data file: Access denied" in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_module_execution_help() -> None:
    res = subprocess.run(
        [sys.executable, "-m", "expense_tracker", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "usage: expense_tracker" in res.stdout
    assert "add" in res.stdout
    assert "list" in res.stdout
    assert "summary" in res.stdout
    assert "edit" in res.stdout
    assert "delete" in res.stdout
    assert "Traceback" not in res.stderr
    assert "Traceback" not in res.stdout


def test_cli_summary_by_category_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(id=1, amount=Decimal("12.50"), category="food", date="2026-11-19"),
            Expense(id=2, amount=Decimal("10.00"), category="food", date="2026-11-20"),
            Expense(id=3, amount=Decimal("5.00"), category="books", date="2026-11-21"),
        ],
    )

    exit_code = main(["summary"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().splitlines() if line]
    # Keys must be printed sorted: books before food
    assert lines == ["books: 5.00", "food: 22.50"]
    assert captured.err == ""
    assert "Traceback" not in captured.out


def test_cli_summary_by_month(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(id=1, amount=Decimal("50.00"), category="c", date="2026-10-15"),
            Expense(id=2, amount=Decimal("12.50"), category="c", date="2026-11-01"),
            Expense(id=3, amount=Decimal("10.00"), category="c", date="2026-11-19"),
        ],
    )

    exit_code = main(["summary", "--by", "month"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().splitlines() if line]
    assert lines == ["2026-10: 50.00", "2026-11: 22.50"]


def test_cli_summary_empty_prints_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    exit_code = main(["summary"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_cli_edit_amount_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(
                id=1,
                amount=Decimal("10.00"),
                category="food",
                date="2026-11-19",
                note="lunch",
            )
        ],
    )

    exit_code = main(["edit", "1", "--amount", "19.99"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Expense 1 updated." in captured.out

    expenses = load_expenses(data_file)
    assert expenses[0].amount == Decimal("19.99")
    # All other fields must be preserved
    assert expenses[0].category == "food"
    assert expenses[0].date == "2026-11-19"
    assert expenses[0].note == "lunch"


def test_cli_edit_note_empty_string_sets_none(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(
                id=1,
                amount=Decimal("10.00"),
                category="food",
                date="2026-11-19",
                note="existing note",
            )
        ],
    )

    exit_code = main(["edit", "1", "--note", ""], data_file=data_file)
    assert exit_code == 0

    expenses = load_expenses(data_file)
    assert expenses[0].note is None


def test_cli_edit_no_fields_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [Expense(id=1, amount=Decimal("10.00"), category="c", date="2026-11-19")],
    )

    exit_code = main(["edit", "1"], data_file=data_file)
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Nothing to change." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_edit_invalid_id_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    for bad_id in ("0", "-1"):
        exit_code = main(["edit", bad_id, "--amount", "10.00"], data_file=data_file)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Expense ID must be a positive integer." in captured.err
        assert "Traceback" not in captured.err
        assert "Traceback" not in captured.out


def test_cli_edit_unknown_id_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [Expense(id=1, amount=Decimal("10.00"), category="c", date="2026-11-19")],
    )

    exit_code = main(["edit", "999", "--amount", "20.00"], data_file=data_file)
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Expense with ID 999 not found." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_edit_invalid_amount_or_category_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [Expense(id=1, amount=Decimal("10.00"), category="c", date="2026-11-19")],
    )

    # Invalid amount
    exit_code = main(["edit", "1", "--amount", "-5.00"], data_file=data_file)
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Amount must be a positive number." in captured.err
    assert "Traceback" not in captured.err

    # Empty category
    exit_code = main(["edit", "1", "--category", "  "], data_file=data_file)
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Category cannot be empty." in captured.err
    assert "Traceback" not in captured.err

    # File should be completely unmodified
    expenses = load_expenses(data_file)
    assert expenses[0].amount == Decimal("10.00")
    assert expenses[0].category == "c"


def test_cli_delete_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(id=1, amount=Decimal("10.00"), category="c1", date="2026-11-19"),
            Expense(id=2, amount=Decimal("20.00"), category="c2", date="2026-11-19"),
        ],
    )

    exit_code = main(["delete", "1"], data_file=data_file)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Expense 1 deleted." in captured.out

    remaining = load_expenses(data_file)
    assert len(remaining) == 1
    assert remaining[0].id == 2


def test_cli_delete_invalid_id_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    for bad_id in ("0", "-2"):
        exit_code = main(["delete", bad_id], data_file=data_file)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Expense ID must be a positive integer." in captured.err
        assert "Traceback" not in captured.err
        assert "Traceback" not in captured.out


def test_cli_delete_unknown_id_does_not_write_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    initial_expenses = [
        Expense(id=1, amount=Decimal("10.00"), category="c1", date="2026-11-19"),
        Expense(id=2, amount=Decimal("20.00"), category="c2", date="2026-11-19"),
    ]
    save_expenses(data_file, initial_expenses)

    content_before = data_file.read_bytes()

    exit_code = main(["delete", "999"], data_file=data_file)
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Expense with ID 999 not found." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out

    # Assert file contents are completely unchanged
    content_after = data_file.read_bytes()
    assert content_before == content_after


def test_cli_delete_highest_id_reuses_on_next_add(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    save_expenses(
        data_file,
        [
            Expense(id=1, amount=Decimal("10.00"), category="c1", date="2026-11-19"),
            Expense(id=2, amount=Decimal("20.00"), category="c2", date="2026-11-19"),
            Expense(id=3, amount=Decimal("30.00"), category="c3", date="2026-11-19"),
        ],
    )

    # Delete highest ID (3)
    exit_code = main(["delete", "3"], data_file=data_file)
    assert exit_code == 0

    # Next add must reuse ID 3
    exit_code = main(
        ["add", "--amount", "40.00", "--category", "c4"], data_file=data_file
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Expense added with ID 3." in captured.out

    expenses = load_expenses(data_file)
    assert [e.id for e in expenses] == [1, 2, 3]


def test_cli_bad_date_in_json_raises_value_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_file = tmp_path / "expenses.json"
    raw_bad_data = [{"id": 1, "amount": "10.00", "category": "c", "date": "2026-1-1"}]
    data_file.write_text(json.dumps(raw_bad_data), encoding="utf-8")

    exit_code = main(["list"], data_file=data_file)
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Corrupted data file: record 0 is invalid." in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out
