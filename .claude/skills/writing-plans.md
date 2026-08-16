# Skill: Writing Plans

**When to use:** Before starting any change larger than a single-file edit or 30-minute task.

**Adapted from:** [obra/superpowers/writing-plans](https://github.com/obra/superpowers/tree/main/skills/writing-plans)

## Plan format (for `.claude/plan/NN-<topic>.md`)

```markdown
# NN — <short title>

## Context (why now)
1-3 sentences. What problem or opportunity triggers this. Link a session note or issue.

## Non-goals
What we're *not* doing this pass. Bounds the diff.

## Design
The recommended approach — not the alternatives you considered. Include:
- Files to be created / modified (paths).
- Public API shape (endpoint, function signature, DB schema).
- Data flow (one diagram or ASCII sketch if non-trivial).
- Reused pieces (existing utils, other services, external libs) with paths.

## Milestones (2-6 checkpoints)
Each milestone leaves the repo green — deployable, tests pass.

- [ ] M1 — describe the smallest useful outcome
- [ ] M2 — next capability
- ...

## Verification
How you'll know each milestone worked (see the verification-before-completion skill).

## Risks / open questions
Anything you're unsure of. Better a written unknown than a hidden one.
```

## Rules

- **One file per plan**, numbered sequentially. Never edit an old plan; supersede it with a new one that links back.
- **Concise.** A good plan fits on one screen. Ambition sits in the milestone count, not the prose.
- **Written before code**, revised as reality intrudes. Update the plan file when you learn something that would change the design.
- **The plan is the source of truth for the current change.** If the PR diverges from the plan, either update the plan or narrow the PR.

## Anti-patterns

- **Novel-length plans** — nobody reads them.
- **Plans that list alternatives** — that's for the design discussion, not the plan file.
- **Plans without milestones** — becomes a wish, not a route.
- **Ignoring the plan mid-flight** — the plan is a commitment device; break it deliberately if at all.

## When you don't need a plan

Typo fixes. Version bumps. Adding a single test. Changes < 20 LOC in a well-understood area. Don't ceremony-tax small work.
