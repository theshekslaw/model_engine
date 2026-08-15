import asyncio

from shek_common_utility.logging import get_logger

from model_engine.providers.ollama import OllamaProvider

logger = get_logger(__name__)


async def warm_loop(
    *,
    ollama: OllamaProvider,
    model: str,
    interval_seconds: float = 240.0,
    stop_event: asyncio.Event,
) -> None:
    """Periodically ping the warm model so Ollama keeps it in VRAM.

    Ollama unloads models after `OLLAMA_KEEP_ALIVE` (default 5m). We re-ping every
    4 minutes to keep the warm model resident indefinitely (as long as this task runs).
    """
    logger.info("warm_loop_started", model=model, interval_seconds=interval_seconds)
    try:
        await ollama.warm(model)
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
                break
            except TimeoutError:
                await ollama.warm(model)
    finally:
        logger.info("warm_loop_stopped", model=model)
