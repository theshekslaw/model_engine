from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_ai import Agent
from shek_common_utility.logging import get_logger

from model_engine.providers.ollama import OllamaProvider
from model_engine.tasks.schemas import get_schema

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class TaskConfig:
    name: str
    provider: str
    model: str
    system_prompt: str
    output_schema: str | None


@dataclass(slots=True)
class TaskEntry:
    config: TaskConfig
    agent: Agent[None, Any]
    output_type: type[BaseModel] | None


class TaskRegistry:
    def __init__(self, entries: dict[str, TaskEntry], warm_model: str | None) -> None:
        self._entries = entries
        self._warm_model = warm_model

    @property
    def warm_model(self) -> str | None:
        return self._warm_model

    def all(self) -> list[TaskConfig]:
        return [e.config for e in self._entries.values()]

    def get(self, name: str) -> TaskEntry:
        try:
            return self._entries[name]
        except KeyError as exc:
            raise KeyError(f"Unknown task: {name}") from exc

    def models(self) -> set[str]:
        return {e.config.model for e in self._entries.values()}


def load_registry(*, config_path: Path, ollama: OllamaProvider) -> TaskRegistry:
    if not config_path.is_file():
        raise FileNotFoundError(f"Task config not found: {config_path}")

    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    warm_model = raw.get("warm_model")

    tasks_raw: dict[str, Any] = raw.get("tasks") or {}
    if not tasks_raw:
        raise ValueError(f"No tasks defined in {config_path}")

    entries: dict[str, TaskEntry] = {}
    for task_name, cfg in tasks_raw.items():
        provider_name = cfg.get("provider", "ollama")
        if provider_name != "ollama":
            raise ValueError(
                f"Task '{task_name}' uses provider '{provider_name}', "
                f"but only 'ollama' is implemented in v0.1."
            )

        model_name: str = cfg["model"]
        system_prompt: str = cfg.get("system_prompt", "")
        schema_name: str | None = cfg.get("output_schema")
        output_type = get_schema(schema_name)

        model = ollama.build_model(model_name)
        agent: Agent[None, Any] = Agent(
            model=model,
            system_prompt=system_prompt,
            output_type=output_type if output_type is not None else str,
        )

        entries[task_name] = TaskEntry(
            config=TaskConfig(
                name=task_name,
                provider=provider_name,
                model=model_name,
                system_prompt=system_prompt,
                output_schema=schema_name,
            ),
            agent=agent,
            output_type=output_type,
        )
        logger.info("task_registered", task=task_name, model=model_name, schema=schema_name)

    return TaskRegistry(entries=entries, warm_model=warm_model)
