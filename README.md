# model_engine

Task-routed LLM gateway backed by Ollama. Downstream services call one endpoint per task and never touch a model directly.

## Quick start

```bash
cp .env.example .env
# edit .env: set AUTH_TOKEN, confirm OLLAMA_BASE_URL points at your Ollama
uv sync
make dev
```

Ollama must be reachable at `OLLAMA_BASE_URL`. On this laptop, it's bound to `http://100.74.195.97:11434` (Tailscale).

## Endpoints

- `GET  /health` — liveness + Ollama reachability + warm model
- `GET  /tasks` — list registered tasks
- `POST /task/{name}` — run a task; body `{"input": "..."}`; returns structured output per task schema

Example:

```bash
curl -X POST http://localhost:8000/task/summarize_paper \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": "Attention Is All You Need — the Transformer paper..."}'
```

## Task routing

Tasks live in `config/tasks.yaml`. Each task pins:

- `provider` — currently `ollama` only
- `model` — Ollama model name (e.g. `qwen2.5:7b`, `qwen2.5:3b`, `qwen2.5-coder:7b`)
- `system_prompt` — role definition
- `output_schema` — one of the class names in `src/model_engine/tasks/schemas.py` (or `null` for free-form text)

Adding a new task = edit `tasks.yaml` (+ add a Pydantic schema class if you need structured output). No code changes to routes.

## Model warming

`warm_model` in `tasks.yaml` (default `qwen2.5:3b`) is kept resident in Ollama VRAM by a background loop that pings it every 4 minutes. This keeps `chat` responses fast on 4 GB VRAM.

Cold models load on first request (~5 s on this hardware). A per-model asyncio lock serializes same-model requests to avoid thrashing.

## Development

```bash
make check    # ruff + mypy strict + pytest
make dev      # uvicorn with reload on :8000
```

## Docker

```bash
make build
make up       # docker compose up -d
make logs
```

## Repo conventions

- Python style: [`shek_common_utility/.claude/coding_style/python.md`](https://github.com/theshekslaw/shek_common_utility/blob/main/.claude/coding_style/python.md)
- All shared utilities (logging, HTTP, settings, model_engine/brain clients) come from `shek_common_utility` v0.1.0 (git dep)
