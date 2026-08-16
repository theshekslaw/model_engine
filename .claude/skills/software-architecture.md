# Skill: Software Architecture (SOLID + Clean layering)

**When to use:** Designing a new service, adding a major subsystem, or considering a refactor across module boundaries.

**Adapted from:** [NeoLabHQ/context-engineering-kit — software-architecture](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/ddd/skills/software-architecture)

## SOLID — pragmatic take

**S — Single Responsibility.** A class/module has one reason to change. If your PR description has "and" in it, likely two responsibilities.

**O — Open/Closed.** Add features without editing the innards. In Python, this is the Protocol / dependency-injection pattern (see `providers/base.py` in `model_engine` — new provider = new class, no route edits).

**L — Liskov substitution.** Anywhere you accept a `BaseX`, any subclass must work without surprise. Applies to Protocols too.

**I — Interface segregation.** Prefer many small Protocols to one god-interface. `ModelProvider` (build+warm) is one; a separate `EmbeddingProvider` is another.

**D — Dependency inversion.** Business logic depends on abstractions, not concrete infra. Storage adapters implement Protocols; ingestion pipeline talks to Protocols only.

## Clean layering (adapted to FastAPI + polyrepo)

```
┌─ API layer ───────────────────────────────────┐  routes.py, deps.py
│    HTTP concerns only: parsing, validation,   │
│    auth, response shaping                     │
└──────────────┬────────────────────────────────┘
               │ calls
┌──────────────▼────────────────────────────────┐  services/
│  Application layer                            │  ingest.py, search.py
│    Orchestrates use cases across domain +    │
│    infra. No HTTP knowledge.                  │
└──────────────┬────────────────────────────────┘
               │ calls
┌──────────────▼────────────────────────────────┐  domain/
│  Domain layer                                 │  models, invariants,
│    Pure Python. No I/O. Fully unit-testable  │  policies
│    without any DB or network.                 │
└──────────────┬────────────────────────────────┘
               │ uses Protocols
┌──────────────▼────────────────────────────────┐  db/, providers/
│  Infrastructure                                │
│    SurrealDB adapter, MinIO adapter, Ollama  │
│    provider, etc. Concrete implementations.   │
└───────────────────────────────────────────────┘
```

**Direction of dependencies:** always **inward**. Infra depends on Domain; API depends on Application; Application depends on Domain. **Domain depends on nothing.**

## Practical rules for our services

- **`src/<service>/domain/`** exists in `shek_brain` and any service with real business logic; not in shim services like `model_engine` (that's mostly infra).
- **No `httpx` imports in `domain/`.** No `sqlalchemy`. No `pydantic-ai`. Only stdlib + pydantic models.
- **Cross-service calls go through `shek_common_utility` clients** (`ModelEngineClient`, `BrainClient`). Never construct URLs by hand in a service.
- **Each service has one docker-compose** with `mem_limit`. No mystery containers.
- **Adding a new task or storage backend** = adding a class implementing an existing Protocol. If you find yourself adding an `if provider == "x"` branch, you're violating O.

## Anti-patterns

- **God-service** — one repo doing 4 responsibilities. Split, or accept the tech debt in writing.
- **Anemic domain** — all logic in `services/`, domain is bare dataclasses. Fine for CRUD; suspicious for anything with invariants.
- **Cross-layer imports** — `domain/` importing `db/` is a red flag. Fix with a Protocol.
- **Hidden coupling via shared globals** — every dep passes explicitly (FastAPI `Depends`, constructor injection).
- **Premature ports and adapters** — don't apply full hexagonal for a 100-line service. This whole doc is a *guide*, not a mandate.

## When to break these rules

- **Prototyping** — skip layering. Note it in the PR.
- **A truly narrow shim** — `model_engine` is 95% infra; a formal domain layer would be ceremony.
- **You've measured a perf cost** — abstractions have runtime price. Only in hot paths.
