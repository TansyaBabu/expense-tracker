---
name: add-feature
description: Follow this workflow whenever adding a new feature or command to the expense tracker.
---

# Add Feature Workflow

When adding a new feature or command, execute the following steps in order:

## Steps
1. **Restate the goal**: Clearly state what feature or behavior is being added and what done looks like.
2. **Propose a plan**: Outline a step-by-step implementation plan specifying files to touch, tests to add, and edge cases.
3. **Wait for approval**: Present the plan to the user and wait for confirmation before writing code.
4. **Implement in small steps**: Make changes incrementally, adhering strictly to AGENTS.md (type hints, small single-responsibility functions, Decimal for money, ValueError on validation issues).
5. **Write tests**: Add comprehensive tests covering both happy path and edge cases.
6. **Run tests & linters**: Run `pytest -q` and `ruff check .` to verify that all tests pass and linting is clean.
7. **Summarise the change**: Conclude with a concise summary of the modifications and test results.
