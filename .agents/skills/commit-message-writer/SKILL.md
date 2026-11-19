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
3. **Identify scope**: Name the module being touched, e.g. `(storage)`, `(validation)`, `(cli)`, `(models)`, `(summary)`. Omit the scope only if the change spans unrelated files, and say so in the log.
4. **Formulate subject line**:
   - Imperative, lower case, no trailing period.
   - Max 50 characters: `<type>(<scope>): <action>`
5. **Add bulleted body (if non-trivial)**:
   - Explain what was changed and why.
   - Wrap at 72 characters.
6. **Rule check**: Confirm no secrets, data files, or skipped tests are included.
7. **Output only the message**: Do not add an audit, checklist, labels, or commentary. The output is the commit message text and nothing else.

## Example Output
```text
feat(storage): add JSON persistence and next_id

- load_expenses returns [] for a missing file
- save_expenses writes via a temp file and os.replace
- next_id returns max id + 1, or 1 when empty
```