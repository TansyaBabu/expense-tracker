# Permissions note

## Approval mode
Ask first. Antigravity proposed a plan for each feature, I reviewed it, and I approved it before any code was written. Each file write also required my approval.

## Why
The brief asks me to review every change and explain every line I commit. Ask-first kept each diff small and reviewable before it reached the repository. It was slower than auto-edit, but plan review caught real bugs before code existed, including NaN and float input, bool as an amount, validation order, and the `--note ""` clear.

## What I did not use
I did not use auto-edit or a sandboxed mode.