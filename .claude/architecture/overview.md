# Architecture — model_engine

## Purpose

A task-routed HTTP gateway in front of Ollama. Downstream services call `POST /task/{name}` and never encode a model name.

## Non-purposes

- Not a general LLM library. Providers are pluggable but the API is task-first, not model-first.
- Not a caching layer (yet). Add later if needed.
- Not a rate limiter (yet). Bearer token is the only gate.

## Layered view

```
┌────────────────────────────────────────────────┐
│  API      routes.py, deps.py                   │  HTTP + auth
├────────────────────────────────────────────────┤
│  Router   router/locks.py, router/warmup.py    │  serialize per-model, keep warm
├────────────────────────────────────────────────┤
│  Tasks    tasks/registry.py, tasks/schemas.py  │  YAML → pydantic-ai Agents
├────────────────────────────────────────────────┤
│  Provider providers/base.py, providers/ollama  │  swap Ollama ↔ Claude ↔ OpenAI here
└────────────────────────────────────────────────┘
```

**Dependency direction is downward:** API imports Tasks + Router; Tasks import Provider; Provider is standalone. Nothing above knows an Ollama URL.

## Key design decisions

1. **YAML task registry.** Adding a task doesn't touch code. `config/tasks.yaml` maps `{task_name: (provider, model, prompt, output_schema)}`. Schema names resolve to Pydantic classes in `tasks/schemas.py`.
2. **One `pydantic_ai.Agent` per task.** Built at startup from the YAML. Structured outputs land as `BaseModel` instances the route serializes.
3. **Provider = Protocol.** Ollama today, Claude/OpenAI tomorrow. `OllamaProvider` wraps `pydantic_ai.models.openai.OpenAIChatModel` pointed at Ollama's `/v1` endpoint (Ollama is OpenAI-compatible).
4. **Per-model asyncio lock.** Concurrent requests to the same model queue in FIFO to avoid Ollama swap thrashing on 4 GB VRAM.
5. **Anti-thrash window.** A model that was just used stays "hot" — the router won't pre-emptively unload it within 30 s of last use.
6. **Warm loop.** A background asyncio task pings the `warm_model` (default `qwen2.5:3b`) every 4 min so Ollama's `keep_alive` (5 min) never expires.
7. **Bearer auth from `shek_common_utility.BaseServiceSettings`** — no auth logic in this repo.

## Files → responsibilities

| File | Owns |
|---|---|
| `main.py` | FastAPI app factory + lifespan. Wires state onto `app.state`. |
| `settings.py` | Settings subclass with Ollama + task-config config. |
| `providers/base.py` | `ModelProvider` Protocol. |
| `providers/ollama.py` | Ollama-backed provider (build_model / warm / unload / health). |
| `tasks/schemas.py` | Pydantic classes for structured outputs; `SCHEMAS` registry. |
| `tasks/registry.py` | Parse YAML → build Agents → `TaskRegistry`. |
| `router/locks.py` | `ModelLocks` async context manager per model. |
| `router/warmup.py` | Background `warm_loop`. |
| `api/deps.py` | FastAPI deps + bearer verification. |
| `api/routes.py` | `/health`, `/tasks`, `POST /task/{name}`. |

## What changes when

- **New task** → edit `config/tasks.yaml`. If it needs structured output, add a class to `schemas.py` and its class name to `SCHEMAS`.
- **New provider** → add `providers/xyz.py`, implement `ModelProvider`, register in `registry.load_registry`.
- **New endpoint shape** → probably means we outgrew the task-based abstraction. Discuss first.

## Deferred to v0.2+

- Streaming (`POST /task/{name}/stream` SSE) — scaffolded but not tested.
- Metrics / traces.
- Batch endpoints (multi-task in one call).
- Cache layer keyed on `(model, system_prompt, input)`.
