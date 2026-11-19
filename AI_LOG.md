# AI Usage Log

Tool: Google Antigravity (App). Approval mode: Request Review.
Model for all entries unless noted: Gemini 3.8 Flash (High).

## Entry 1: Implementation plan
- Model: Gemini 3.8 Flash (High)
- Prompt: Read AGENTS.md and SPEC.md, give a step-by-step implementation plan where each step is small enough to commit, listing files touched and tests added, and state assumptions. Do not write code yet.
- What the AI produced: A 9-step plan with files and tests per step, standard library only, Decimal for money, and a friendly-error CLI design.
- What was wrong or missing: It reported that AGENTS.md and SPEC.md were inside .venv/ as an "assumption" instead of flagging it as a bug, and .venv/ had been committed to git in the first commit. It guessed Python 3.14 without checking. Money storage in JSON was left as either strings or cents. It did not say what happens to IDs after deleting the highest one. It had no step for skills or the hook, and it had no tests for edit with no fields, amount 0, or malformed --from/--to dates.
- What I changed: Moved both files to the repo root, removed .venv/ from git tracking (`git rm -r --cached .venv`), added a proper .gitignore, and sent a correction prompt with the decisions and the missing items.

## Entry 2: Revised plan
- Model: Gemini 3.8 Flash (High)
- Prompt: Revise the plan with nine corrections: files at the repo root, ignore only data/expenses.json, money as "12.50" strings in JSON and Decimal in memory, summary logic in summary.py, main(argv) -> int for testability, a storage path parameter, a decided ID-reuse rule with a test, extra edge-case tests, and a step for the add-feature skill and a formatting hook.
- What the AI produced: An 11-step plan applying the corrections, a second skill (commit-message-writer), a hook config, and main(argv, data_file=None).
- What was wrong or missing: Step 1 repeated work I had already done by hand. Installing pytest and ruff was not planned. AGENTS.md was not updated with the new decisions. The add-feature skill described a TDD flow rather than the steps in the brief. It also added tests for config files, which are not meaningful tests of the app.
- What I changed: Told it Step 1 was partly done, asked it to install dev tools and update AGENTS.md, set the skill steps from the brief (restate, plan, wait for approval, implement, test, run, summarise), and had the config-file tests removed.

## Entry 3: Step 1 and Step 2 execution (project config, skills, hook)
- Model: Gemini 3.8 Flash (High)
- Prompt: Execute Step 1 (pyproject.toml, requirements-dev.txt, README, AGENTS.md update) and Step 2 (add-feature skill, commit-message-writer skill, format hook), one at a time, showing each file before writing it.
- What the AI produced: pyproject.toml, requirements-dev.txt, a README skeleton, an AGENTS.md update with key decisions, both SKILL.md files, `.agents/hooks/format.py` and `.agents/hooks.json`.
- What was wrong or missing: The hook matcher used guessed tool names (`edit_file|write_file`). The Antigravity hooks docs list `write_to_file`, `replace_file_content` and `multi_replace_file_content`, so the hook never fired. The AI said the files were "verified" and that the hook "executed safely", but it had only repeated the file content I asked for, and ruff had not been installed in the venv. A copied .gitignore from the venv folder was also mentioned as a possible problem, so I checked it by hand.
- What I changed: Corrected the matcher to the real tool names, installed the dev dependencies into .venv, and checked the result with `cat` on the file instead of trusting the AI's report. I then ran `format.py` by hand on a badly written file (`x=1;y   =  2` became `x = 1` and `y = 2` on separate lines). That showed the script works, but it did not show Antigravity runs the hook. See Entry 4.

## Entry 4: Hook verification in Antigravity
- Model: Gemini 3.8 Flash (High)
- Prompt: Create a file scratch.py with exactly this content: `x=1;y   =  2`. Then the same request with a trace-file diagnostic in the hook command.
- What the AI produced: A file containing the raw text, and a note that the hook did not run because `python` on PATH had no ruff.
- What was wrong or missing: The hook did not fire. The diagnostic wrote no trace file. The Installed tab in Customizations showed no `ruff-auto-format` entry, so this version of Antigravity does not load `.agents/hooks.json`. The AI's explanation was a guess, and it proposed changing `format.py` to search for `.venv`, which I rejected because it would have hidden the real problem.
- What I changed: Restored the committed config, and added a git `pre-commit` hook (see Entry 10). I did not change `format.py`.

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
- Commits were checked with git status and git diff --cached before committing, except where noted (placeholder messages were amended afterwards).
- Rules file and hook re-check: I re-checked AGENTS.md and the hook config against the brief. `.agents/hooks.json` was committed but never loaded by Antigravity, so I removed it in `2aaef39`, and the formatter check runs from the git pre-commit hook in `.githooks/` instead.

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
- Verified: I read the `handle_add` ordering and the `SystemExit`, `ValueError` and `OSError` handling in `cli.py` from a screenshot of the code. `grep -n "float" expense_tracker/cli.py` returned no matches.

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