# Prompt: Refactor safety check

Use when you're about to move / rename / restructure code and want a sanity pass.

---

I want to <describe refactor>. Before I do it, answer these:

1. **Consumers.** Grep for every caller/importer of the symbols being renamed/moved. List them with file:line references.
2. **Public boundary.** Is any of this exported from the package's `__init__.py` (or npm entry point)? Renames there are breaking changes.
3. **Serialized shapes.** Does the refactor change any pydantic model / JSON-Schema / DB column name? That's a data migration, not a refactor.
4. **Test coverage.** Which tests exercise the affected code paths? Are they behavioral (safe under refactor) or implementation-coupled (will break)?
5. **Git-dep consumers.** Do other repos pin a tag that includes this code? Downstream `uv sync` / `pnpm install` behavior on the change?

Only after answering, propose the refactor plan as an ordered list of atomic edits that each leave the repo green.

If anything above surfaces "yes, breaks something," name it explicitly and propose either a deprecation window or a breaking-version bump.
