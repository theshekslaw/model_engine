from typing import Any

import httpx
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from shek_common_utility.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider:
    """Provider backed by an Ollama server via its OpenAI-compatible endpoint (`/v1`).

    We treat Ollama as OpenAI-compatible chat completions. Model warming and unloading
    are done through Ollama's native `/api/generate` endpoint with `keep_alive` set.
    """

    name: str = "ollama"

    def __init__(self, *, base_url: str, keep_alive: str = "5m") -> None:
        self._base_url = base_url.rstrip("/")
        self._keep_alive = keep_alive
        self._provider = OpenAIProvider(base_url=f"{self._base_url}/v1", api_key="ollama")

    def build_model(self, model_name: str) -> Model:
        return OpenAIChatModel(model_name=model_name, provider=self._provider)

    async def warm(self, model_name: str) -> None:
        """Force Ollama to load a model into memory. Uses a tiny generate call with keep_alive."""
        payload: dict[str, Any] = {
            "model": model_name,
            "prompt": "",
            "keep_alive": self._keep_alive,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                await client.post(f"{self._base_url}/api/generate", json=payload)
                logger.info("model_warmed", model=model_name)
            except httpx.HTTPError as e:
                logger.warning("model_warm_failed", model=model_name, err=str(e))

    async def unload(self, model_name: str) -> None:
        """Ask Ollama to unload a model by setting keep_alive to 0."""
        payload: dict[str, Any] = {
            "model": model_name,
            "prompt": "",
            "keep_alive": 0,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                await client.post(f"{self._base_url}/api/generate", json=payload)
                logger.info("model_unloaded", model=model_name)
            except httpx.HTTPError as e:
                logger.warning("model_unload_failed", model=model_name, err=str(e))

    async def health(self) -> bool:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self._base_url}/api/tags")
                return response.status_code == 200
            except httpx.HTTPError:
                return False
