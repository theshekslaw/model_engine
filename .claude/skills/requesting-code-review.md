# Skill: Requesting Code Review

**When to use:** Before you open a PR or ask a human/agent to look at your diff.

**Adapted from:** [obra/superpowers/requesting-code-review](https://github.com/obra/superpowers/tree/main/skills/requesting-code-review)

## Pre-review self-checklist

Run this before asking anyone to look. Every failure = fix before requesting.

- [ ] `make check` passes (ruff + mypy strict + pytest).
- [ ] `git status` shows only intended files. No accidental `.env`, `.venv`, model weights, or IDE settings.
- [ ] `git diff --stat` — is the diff scope-matched to the task? If not, split.
- [ ] Each commit is coherent (one logical change). Squash noisy WIP commits.
- [ ] The PR description explains **why**, not just what. Link the plan/task if applicable.
- [ ] Test coverage is proportional to risk (new logic + non-trivial edge cases have tests).
- [ ] No `TODO`/`FIXME`/`XXX` without a linked ticket or dated note.
- [ ] No commented-out code. If it's dead, delete it — git remembers.
- [ ] Public API changes have docstrings or README updates.
- [ ] Migrations (if any) are reversible OR justified as irreversible in the PR body.

## The PR description template

```
## What
1-2 sentences on the change.

## Why
Link to the plan / issue / incident. Explain the pressure driving this change.

## How
The design decision you made and the alternative you rejected.

## Verify
Concrete steps the reviewer can run to see it works:
- `curl -X POST ... | jq`
- `docker compose up -d && sleep 5 && ...`

## Risk
What could break. What's covered by tests. What isn't and why.
```

## Anti-patterns

- **"WIP, don't review yet"** on a large PR — split or hide behind a draft.
- **"Fix everything"** PRs — scope creep destroys reviewability.
- **Empty description** — force the reviewer to reverse-engineer intent.
- **Force-pushing over review feedback** without noting what changed — reviewer loses context.
