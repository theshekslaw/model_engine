from pathlib import Path

from pydantic import Field
from shek_common_utility.settings import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = Field(default="model_engine")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    ollama_base_url: str = Field(
        default="http://100.74.195.97:11434",
        description="Base URL of the Ollama server; OpenAI-compat endpoint is base_url + '/v1'.",
    )
    ollama_keep_alive: str = Field(
        default="5m",
        description="How long Ollama keeps a model in VRAM after last use.",
    )

    task_config_path: Path = Field(
        default=Path("config/tasks.yaml"),
        description="Path to the task-routing YAML.",
    )

    warm_on_startup: bool = Field(
        default=True,
        description="If true, load the warm model in lifespan startup.",
    )

    request_timeout_seconds: float = Field(default=300.0)


def load_settings() -> Settings:
    return Settings()
