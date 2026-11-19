# AI Usage Log

## Entry 1: Rules file (AGENTS.md)
- Model: Gemini 3.8 Flash (High) 
- Prompt: [unverified: paste the prompt from your chat history]
- What the AI produced: AGENTS.md with the tech stack, commands (run, test, lint), folder structure, code style, four "never" rules, and a definition of done.
- What was wrong or missing: The file listed cli.py, storage.py and summary.py as if they already existed, when they were planned. The Python version was stated without being checked. The plan for `python -m expense_tracker` did not include a `__main__.py`.
- What I changed: [unverified: list the edits you made, or delete this line]. Checked the Python version with `python --version`: [unverified: result]

## Entry 2: Project config and README skeleton
- Model: Gemini 3.8 Flash (High) 
- Prompt: [unverified: prompt for the project setup]
- What the AI produced: .gitignore, pyproject.toml, requirements-dev.txt, a README skeleton, and data/.gitkeep.
- What was wrong or missing: [unverified: what you found on review, or "No problems found on review of the diff."]
- What I changed: Reviewed the diff before committing. [unverified: list any change you made]

## Entry 3: Spec and key decisions
- Model: Gemini 3.8 Flash (High) 
- Prompt: [unverified: prompt for the spec or first plan]
- What the AI produced: A spec and key decisions in AGENTS.md, including Decimal for money (stored as strings in JSON), the `main(argv=None, data_file=None) -> int` signature, aggregation in summary.py, and ID reuse through max + 1.
- What was wrong or missing: [unverified: what you questioned, or delete this line]
- What I changed: [unverified: the decision you approved, and why]

## Entry 4: Skills and ruff hook (Step 2)
- Model: Gemini 3.8 Flash (High)
- Prompt: Execute Step 2: add-feature skill with the brief's 7 steps, commit-message-writer skill, ruff format hook.
- What the AI produced: Two SKILL.md files (add-feature, commit-message-writer), format.py, and hooks.json.
- What was wrong or missing:
  - The hook matcher used guessed tool names (`edit_file|write_file`). The real tool names in the Antigravity hooks docs are `write_to_file`, `replace_file_content`, and `multi_replace_file_content`. The assistant said it followed the spec but had not shown it.
  - The hook command used whichever `python` was on PATH, which did not have ruff. I changed it to `.venv/Scripts/python.exe .agents/hooks/format.py`. I confirmed this with `cat .agents/hooks.json`.
  - The hook still did not fire in Antigravity. A diagnostic that wrote a trace file produced no file, and the Installed tab showed no `ruff-auto-format` entry.
- What I changed: Fixed the matcher, installed dev dependencies, and pointed the hook at the venv's Python. The agent-created `scratch.py` was not formatted, so the hook did not fire in Antigravity. The formatter check now runs from the git pre-commit hook in `.githooks/`, enabled with `core.hooksPath` (see Entry 10).

## Entry 5: Domain model (Step 3) with add-feature skill
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the add-feature skill for plan Step 3 (Expense model); restate, plan, wait for approval.
- What the AI produced: Restated the goal and proposed a 4-file plan with 3 tests and edge cases (`5` becomes `"5.00"`, note omitted or `None`). It waited for approval, then wrote the code and tests.
- What was wrong or missing: The plan did not address rounding in `to_dict` (`f"{amount:.2f}"` rounds silently), whether `date` should be a string, or whether `__init__.py` should export `Expense`.
- What I changed: Approved with these choices: `date` stays a YYYY-MM-DD string, plain (non-frozen) `@dataclass`, both `__init__.py` files empty, and a comment in `to_dict` noting that validation rejects amounts with more than 2 decimals.
- Commit: `feat(models): add Expense model and serialization`, message written with the commit-message-writer skill from `git diff --cached`.

## Entry 6: Validation (Step 4) with add-feature skill
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the add-feature skill for plan Step 4 (validation.py); restate, plan, wait for approval.
- What the AI produced: A 2-file plan with 10 tests. After my approval it wrote `validate_amount`, `validate_date`, `validate_category`, `validate_date_range`, and the tests. It reported 13 passed, which is the 10 new tests plus the 3 model tests.
- What was wrong or missing:
  - Plan review: the plan did not handle NaN, Infinity, float input, or `decimal.InvalidOperation` for bad strings. I caught these before any code was written, and the approval reply required them.
  - Edge-case checks run after the commit: `validate_date('2026-1-1')` and `validate_date('2025-02-29')` both raised clean `ValueError`s.
  - `validate_amount(True)` returned `Decimal('1.00')`, because `bool` subclasses `int`. I found this by running the checks, not from the plan or the summary.
- What I changed: Added a `bool` rejection before the int check, with an assertion in `test_validate_amount_invalid_format`. After the fix, `validate_amount(True)` raises `ValueError`.
- Commits: `feat(validation): add input validators` (a7dd28e, 2 files, 184 insertions) and `fix(validation): reject bool as amount`.

## Entry 7: Process notes
- The add-feature skill (plan, approve, implement) worked as intended for Steps 3 and 4. The assistant did not write code before approval.
- Each commit was checked with `git status` and `git diff --cached` before committing.
- Rules file and hook re-check: I re-checked AGENTS.md and the hook config against the brief. `.agents/hooks.json` was committed but never loaded by Antigravity, so I removed it with `git rm`. [change this line if you kept the file instead]

## Entry 8: CLI core, add and list (Step 5b-i) with add-feature skill
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the add-feature skill for plan Step 5b-i (CLI core: add, list, main, `__main__.py`); wait for approval.
- What the AI produced: A plan with 3 files and 9 CLI tests. After my approval it wrote cli.py, `__main__.py`, and 13 CLI tests. It reported 38 passed (25 earlier + 13 new), with ruff check and ruff format clean.
- What was wrong or missing (plan review, before any code):
  - argparse calls `sys.exit` on bad input, so usage errors would not return 1. I asked for `SystemExit` to be converted to a return code of 2.
  - Only `ValueError` was caught. I asked for `OSError` handling too, so an unwritable data directory would not show a traceback.
  - Amount, category, and date had to be validated before the data file was read. I asked for that order so a bad add does not touch the file.
  - An empty `--category` on list was undefined. I chose to reject it with `validate_category`.
  - No-match output was undefined. I chose to print nothing and return 0.
  - I asked for a subprocess test of `python -m expense_tracker --help`.
- What was wrong during commit: The first commit (`9cedb4f`) used a placeholder message, "<paste the commit-message-writer output here>". I amended it to a real message (`526d32f`).
- What I changed: Approved the plan with the changes above. Final commit message:
  - `feat(cli): add add and list subcommands`
  - add validates amount, category and date before touching the data file
  - list filters by category and date range; empty category is rejected
  - ValueError and OSError print a clean message to stderr, never a traceback
  - adds `__main__.py` so `python -m expense_tracker` works
  - tests run against tmp_path and cover validation errors and no-match output
- Verified: I read the `handle_add` ordering and the `SystemExit`, `ValueError` and `OSError` handling in `cli.py` from a screenshot of the code. `grep -n "float" expense_tracker/cli.py`: [paste the result you saw]

## Entry 9: Summary, edit and delete (Step 5b-ii) with add-feature skill
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the add-feature skill for plan Step 5b-ii (summary, edit, delete); wait for approval.
- What the AI produced: A plan for 4 files and 11 CLI tests plus summary tests. After approval it wrote `summary.py`, the three subcommands, and tests. It reported 56 passed (38 earlier + 18 new), with ruff check and ruff format clean.
- What was wrong or missing (plan review, before any code):
  - IDs were not validated. I asked for `type=int` and rejection of `id <= 0`.
  - "Nothing to change" could run after loading the file. I asked for the check before any file read.
  - Empty values were undefined. I chose: `--note ""` clears the note, and empty `--category` or `--amount` goes through the validators.
  - Stored dates were trusted by `total_by_month`. I asked for `validate_date` on loaded records.
  - Summary output order and empty-data behaviour were undefined. I chose sorted keys and no output for empty data.
  - I asked that a delete of an unknown ID not write the file, and that the test check the file contents.
- What I checked in the code:
  - `grep -n "float"` on `summary.py` and `cli.py` returned no matches.
  - `handle_edit` runs the "Nothing to change." check at line 174, before `load_and_validate_expenses`.
  - `handle_delete` checks for the ID before `save_expenses`.
  - `validate_date` runs on every loaded record through `load_and_validate_expenses`.
- What was wrong during testing: I ran `edit 1 --note ""` by hand and confirmed the note was cleared (`list` shows no note). I also wrote a test entry into `data/expenses.json` by mistake and removed it.
- Commits: The first commit (`01e13ed`) used a placeholder message. I amended it to `3456877 feat(cli): add summary, edit and delete subcommands`.

## Entry 10: Commit message skill (Skill 2) and versioned hook
- Model: Gemini 3.8 Flash (High)
- Prompt: Use the commit-message-writer skill on the staged changes; write only the message text to a file.
- What the AI produced: The commit message below, written from the staged diff:

  ```
  chore: add pre-commit hook and update README

  - Add .githooks/pre-commit running ruff format --check . before each commit
  - Document `git config core.hooksPath .githooks` in setup instructions
  - Revise Known Limitations to reflect the versioned hook location
  - Tighten AI Workflow descriptions to match the actual skill steps
  ```

- What was wrong or missing: Earlier commits had hand-typed placeholder messages, which I amended. My first commit command also used a literal `<path>` placeholder, which bash rejected. The README had a stray line and two wrong claims (the hook description and the limitation text), which I corrected by hand.
- What I changed: Versioned the hook in `.githooks/` and enabled it with `core.hooksPath`. Committed from the skill's file with `git commit -F`. The hook blocked an unformatted test file ("Formatting check failed"), then passed on the real commits.
- Verified: `git log -1 --format=%B | grep -n "<[a-z ]*>"` returned no placeholders for this commit.

## Entry 11: Skill maintenance (commit-message-writer rules)
- Model: Gemini 3.8 Flash (High), and manual edits.
- Prompt: Use the skill on the permissions commit, then correct the output.
- What the AI produced: A commit message for `PERMISSIONS.md`, which included a "Skill audit" block with labels and commentary.
- What was wrong or missing: The audit block was not part of the message and would have been stored in history. The body also said "content is unchanged", which was false, because the file went from one line to a full note.
- What I changed: I wrote a corrected message by hand: `docs: expand permissions note with approval mode`. I added step 7 to `SKILL.md` ("Output only the message") and replaced the example with the real storage commit. I amended the rule commit to `9a1ddc0 chore(agents): forbid audit blocks in skill output`, with a 50-character subject.
- Skill coverage: The skill was used for `0601503` and for the permissions follow-up commit. Earlier commits (`9cedb4f`, `01e13ed`, `878868f`, and the first `31faf9a`) used hand-typed messages, and the skill was not run for them.