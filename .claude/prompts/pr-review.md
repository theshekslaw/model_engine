# Prompt: PR review

Use this prompt when asking an agent (or human) to review a diff before merge.

---

Review the diff below with the following priorities, in order:

1. **Correctness.** Does it do what the PR description claims? Are there edge cases missed?
2. **Contract respect.** Does it break any documented interface — REST endpoint, function signature, DB schema, MCP tool signature, git-dep-consumer contract?
3. **Style compliance.** Does it match the repo's `.claude/coding_style/*.md`? Flag deviations.
4. **Testing proportional to risk.** New logic + edge cases have tests. Refactors have coverage of the changed path.
5. **Layer discipline.** Does it respect the layering in `.claude/architecture/overview.md`? Cross-layer imports, hidden coupling, God-modules — call out.
6. **Anti-patterns.** Reference `.claude/skills/*.md` — TDD, verification, systematic debugging. Was the fix root-caused? Was verification real or "should work"?
7. **Scope.** Diff matches the PR title? Sprawl → split.

**Output format:**

```
## Verdict
APPROVE | REQUEST CHANGES | COMMENT

## Must-fix (blocks merge)
- ...

## Nice-to-have
- ...

## Ship-blocker questions
- ...
```

Be direct. Say "wrong" when it's wrong. No hedging fluff.
