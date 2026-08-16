# Skill: Systematic Debugging

**When to use:** You've hit an error, unexpected behavior, or a failing test. Before "let me try a random fix".

**Adapted from:** [obra/superpowers/systematic-debugging](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging)

## The 4-phase process

### Phase 1 — Reproduce
Get a **deterministic**, **minimal**, **local** repro. If you can't reproduce it, you can't fix it.
- Write the failing case as a test if possible.
- Note the exact command, env, seed, request payload.
- If it's flaky, quantify — 1/100 vs 100/100 shifts the debug strategy.

### Phase 2 — Localize
Narrow the fault region. Do NOT skip to speculation.
- Read the error line, and the line above/below.
- Add print/log at the last known-good and first known-bad points.
- Bisect: last passing commit vs. current (`git bisect` is real, use it).
- Check assumptions: input types, DB row counts, container state.

### Phase 3 — Find root cause
The first bug you find is often a symptom, not the cause. Ask "but why?" three times.
- Symptom: "Test fails on empty list."
- Cause 1: "Because we call `list[0]`."
- Cause 2: "Because we assumed callers always pass a non-empty list."
- Cause 3: "Because the API signature doesn't document the constraint."
Fix at the deepest layer that's still your responsibility.

### Phase 4 — Fix + fence
- Fix the root cause.
- **Add a test** that catches this exact regression.
- If the fix touches a boundary (API contract, DB schema), update docs/adjacent tests.

## Anti-patterns

- **Random-mutation debugging** — changing lines until the test passes without understanding why.
- **Swallowing the error** — `except: pass` to make it "work". No.
- **Deleting the test** because it's inconvenient.
- **Fixing the symptom** and moving on when the root cause is one layer down.
- **Blaming the framework** before checking your code.

## For our repos

- Add repro instructions to any bug PR: "Reproduce with: `curl ... | jq`".
- Structlog + JSON logs → grep for `event=` names to trace flow.
- When a Temporal workflow misbehaves, the Temporal UI shows every activity's input+output — start there before code diving.
