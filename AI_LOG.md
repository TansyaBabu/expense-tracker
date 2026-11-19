# AI Usage Log

## Entry 1: [paste your original text]

## Entry 2: [paste your original text]

## Entry 3: [paste your original text]

## Entry 4: Skills and ruff hook (Step 2)
- Model: Gemini 3.8 Flash (High)
- Prompt: Execute Step 2: add-feature skill with the brief's 7 steps, commit-message-writer skill, ruff format hook.
- What the AI produced: Two SKILL.md files (add-feature, commit-message-writer), format.py, and hooks.json.
- What was wrong or missing:
  - The hook matcher used guessed tool names (`edit_file|write_file`). The real tool names in the Antigravity hooks docs are `write_to_file`, `replace_file_content`, and `multi_replace_file_content`, so the hook never fired. The assistant said it followed the spec but had not shown it.
  - After the matcher fix, the test file stayed unformatted because ruff was not installed in the venv. [confirm]
  - The hook command used whichever `python` was on PATH, which may not have the venv's ruff. I changed it to point at `.venv/Scripts/python.exe`. [confirm the final command]
- What I changed: Fixed the matcher, installed dev dependencies, pinned the hook to the venv's Python, and retested with a badly formatted `scratch.py`. [state whether the agent-created file came out formatted without a manual run]

## Entry 5: Domain model (Step 3) with add-feature skill
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the add-feature skill for plan Step 3 (Expense model); restate, plan, wait for approval.
- What the AI produced: Restated the goal and proposed a 4-file plan with 3 tests and edge cases (`5` becomes `"5.00"`, note omitted or `None`). It waited for approval as the skill requires, then wrote the code and tests.
- What was wrong or missing: The plan did not address rounding in `to_dict` (`f"{amount:.2f}"` rounds silently), whether `date` should be a string, or whether `__init__.py` should export `Expense`.
- What I changed: Approved with these choices: `date` stays a YYYY-MM-DD string, plain (non-frozen) `@dataclass`, both `__init__.py` files empty, and a comment in `to_dict` noting that validation rejects amounts with more than 2 decimals. I checked `from_dict` builds `Decimal` from the string, not from a number. [confirm after reading models.py]
- Commit: `feat(models): add Expense model and serialization`, message written with the commit-message-writer skill from `git diff --cached`.

## Entry 6: Validation (Step 4) with add-feature skill
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the add-feature skill for plan Step 4 (validation.py); restate, plan, wait for approval.
- What the AI produced: A 2-file plan with 10 tests, then after my approval `validate_amount`, `validate_date`, `validate_category`, `validate_date_range`, and the tests. It reported 13 passed, which is the 10 new tests plus the 3 model tests.
- What was wrong or missing:
  - Plan review: the plan did not handle NaN, Infinity, float input, or `decimal.InvalidOperation` for bad strings. I caught these before any code was written, and the approved reply required them.
  - Edge-case checks (run after the commit): `validate_date('2026-1-1')` and `validate_date('2025-02-29')` raise clean `ValueError`s. [record the rest: `12.50 12.50`, `12.5`, `'NaN'`, `'9'*30`, grep for float]
  - `validate_amount(True)` returned `Decimal('1.00')` because `bool` subclasses `int`. This was found by running the checks, not by the plan or the summary.
- What I changed: Added a `bool` rejection before the int check, with an assertion in `test_validate_amount_invalid_format`. After the fix, `validate_amount(True)` raises `ValueError`.
- Commits: `feat(validation): add input validators` (a7dd28e, 2 files, 184 insertions) and `fix(validation): reject bool as amount`.

## Entry 7: Process notes
- The brief's add-feature skill (plan, approve, implement) worked as intended for Steps 3 and 4. The assistant did not write code before approval.
- Each commit was checked with `git status` and `git diff --cached` before committing, and the message was written with the commit-message-writer skill.
- Gap I still need to close: the rules file (AGENTS.md) and hook were not re-verified against the brief in this log. [update after step 2 check]