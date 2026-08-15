import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from shek_common_utility.logging import configure_logging, get_logger

from model_engine import __version__
from model_engine.api.routes import router
from model_engine.providers.ollama import OllamaProvider
from model_engine.router.locks import ModelLocks
from model_engine.router.warmup import warm_loop
from model_engine.settings import Settings, load_settings
from model_engine.tasks.registry import TaskRegistry, load_registry


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings

    configure_logging(
        service=settings.service_name, level=settings.log_level, json=settings.log_json
    )
    logger = get_logger("model_engine.lifespan")
    logger.info("startup", version=__version__, ollama=settings.ollama_base_url)

    ollama = OllamaProvider(
        base_url=settings.ollama_base_url, keep_alive=settings.ollama_keep_alive
    )
    registry: TaskRegistry = load_registry(config_path=settings.task_config_path, ollama=ollama)
    locks = ModelLocks()

    app.state.ollama = ollama
    app.state.registry = registry
    app.state.locks = locks

    stop_event = asyncio.Event()
    warm_task: asyncio.Task[None] | None = None
    if settings.warm_on_startup and registry.warm_model:
        warm_task = asyncio.create_task(
            warm_loop(
                ollama=ollama,
                model=registry.warm_model,
                stop_event=stop_event,
            )
        )

    try:
        yield
    finally:
        logger.info("shutdown")
        stop_event.set()
        if warm_task is not None:
            with_timeout = asyncio.wait_for(warm_task, timeout=5.0)
            try:
                await with_timeout
            except (TimeoutError, asyncio.CancelledError):
                warm_task.cancel()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(
        title="model_engine",
        version=__version__,
        description="Task-routed LLM gateway backed by Ollama.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.include_router(router)
    return app


app = create_app()
