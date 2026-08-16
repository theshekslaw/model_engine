# Skill: Verification Before Completion

**When to use:** You're about to say "done" or mark a task complete.

**Adapted from:** [obra/superpowers/verification-before-completion](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion)

## The rule

**"It compiles / it type-checks / the test passes" is not verification.**

A task is done when you have watched the actual end-to-end behavior happen — the request succeeded, the file appeared, the DB row was inserted, the UI rendered.

## Verification checklist (adapt per task)

| Task type | Verification |
|---|---|
| Added an endpoint | `curl` it with a real payload; check status + response body |
| Added a DB query | Run it against a live DB; check row count and content |
| Added a background job | Trigger it; wait; check output state (DB row, MinIO file, etc.) |
| Refactored code | Run the full test suite AND exercise the changed path manually once |
| Fixed a bug | Reproduce the ORIGINAL bug first — confirm it's gone — then confirm no regression |
| Added a config knob | Toggle it in both states; confirm behavior differs correctly |
| Removed code | `grep` the entire monorepo for references; confirm no orphan imports |

## What "verified" looks like in a status update

**Bad:** "Added the ingest endpoint, tests pass."
**Good:** "Added `POST /ingest`. Verified with `curl -X POST http://localhost:8001/ingest -d @sample.json` — returns 201, `psql` confirms row in `items` table, MinIO console shows the blob at `items/{id}/raw.pdf`. 12 tests pass."

## Anti-patterns

- **"Should work"** / **"probably fine"** — not verification, admission of uncertainty.
- **Cherry-picked test** — running only the new test in isolation and calling it done. Run the whole suite.
- **Mocked verification** — asserting on the mock's `call_args`, not the actual effect. Mocks lie by definition.
- **CI-only verification** — waiting to find out on CI what you could learn locally in 30 s.

## When you can't verify

Say so explicitly: *"I can't run this locally because X — needs Y environment. Best-effort static analysis: Z."* Never hide the gap.
