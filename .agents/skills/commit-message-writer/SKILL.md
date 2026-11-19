---
name: commit-message-writer
description: Standard instructions and conventions for writing concise, conventional git commit messages.
---

# Commit Message Writer

Generate conventional, informative git commit messages adhering to project guidelines.

## Steps
1. **Inspect changes**: Review `git status` and staged diff (`git diff --cached`).
2. **Select type**:
   - `feat`: New feature or command
   - `fix`: Bug fix or validation fix
   - `test`: Adding or updating tests
   - `refactor`: Code change that neither fixes a bug nor adds a feature
   - `chore`: Tooling, configuration, or documentation
3. **Identify scope**: Name the module being touched, e.g. `(storage)`, `(validation)`, `(cli)`, `(models)`, `(summary)`.
4. **Formulate subject line**:
   - Imperative, lower case, no trailing period.
   - Max 50 characters: `<type>(<scope>): <action>`
5. **Add bulleted body (if non-trivial)**:
   - Explain what was changed and why.
   - Wrap at 72 characters.
6. **Rule check**: Confirm no secrets, data files, or skipped tests are included.

## Example Output
```text
feat(storage): add auto-increment ID generation and JSON persistence

- Implement ExpenseStorage with configurable file path parameter
- Auto-create missing data directory and initialize empty expenses file
- Reclaim highest deleted ID dynamically via max(remaining) + 1
```
