# Skill: Test-Driven Development

**When to use:** Before you write or modify any non-trivial function.

**Adapted from:** [obra/superpowers/test-driven-development](https://github.com/obra/superpowers/tree/main/skills/test-driven-development)

## The loop

1. **RED** — Write a failing test that describes the smallest useful behavior.
2. **GREEN** — Write the minimum code to pass the test. Ugly is fine.
3. **REFACTOR** — Clean up now that the test guards you. Repeat.

Never skip the RED step. A test you didn't watch fail is a test you don't trust.

## Rules for our repos

- **Every service** ships with `tests/` at repo root, `pytest` + `pytest-asyncio` configured.
- Structure: `tests/unit/` (no I/O outside `tmp_path`), `tests/integration/` (may spin up containers).
- Test file mirrors module: `src/x/y.py` ↔ `tests/unit/test_y.py`.
- `asyncio_mode = "auto"` — no `@pytest.mark.asyncio` needed.
- Integration tests use `testcontainers-python`; skip if Docker unavailable.

## Anti-patterns to avoid

- **Testing implementation details** (private methods, exact SQL). Test *behavior* at the boundary.
- **`assert True`** or tautological asserts.
- **Mocking your own code** — mock at the network / process boundary, not internal calls.
- **One giant test with 15 asserts** — split it. Each test owns one behavior.
- **Skipping the failing-test step** because "I already know it'll fail" — no you don't, and now future-you won't either.

## Before shipping

Every PR: `make test` passes locally. No `pytest.mark.skip` without a linked ticket.
