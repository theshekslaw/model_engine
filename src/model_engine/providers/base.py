from typing import Protocol

from pydantic_ai.models import Model


class ModelProvider(Protocol):
    """Abstract provider that produces `pydantic_ai.Model` instances for a given model name."""

    name: str

    def build_model(self, model_name: str) -> Model: ...

    async def warm(self, model_name: str) -> None:
        """Pre-load a model into memory. May be a no-op for cloud providers."""
