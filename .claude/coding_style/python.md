# Python style — model_engine

Canonical style lives in `shek_common_utility`:

<https://github.com/theshekslaw/shek_common_utility/blob/main/.claude/coding_style/python.md>

Any conventions specific to this repo go **below** this section.

## model_engine-specific rules

- Tasks are declared in `config/tasks.yaml`; adding a task never requires editing route code.
- Output schemas live in `src/model_engine/tasks/schemas.py` and are looked up by class name from YAML.
- The provider abstraction (`src/model_engine/providers/base.py`) is a `Protocol`; add new backends by implementing it, then wire them in `tasks/registry.py`.
- Never bind Ollama-specific concepts (e.g. `keep_alive`) into route code — they live in the provider.
