from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from shek_common_utility.logging import get_logger

from model_engine.api.deps import (
    get_locks,
    get_ollama,
    get_registry,
    require_bearer,
)
from model_engine.providers.ollama import OllamaProvider
from model_engine.router.locks import ModelLocks
from model_engine.tasks.registry import TaskRegistry

logger = get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    warm_model: str | None


class TaskListItem(BaseModel):
    name: str
    provider: str
    model: str
    output_schema: str | None


class TaskInput(BaseModel):
    input: str
    context: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    task: str
    model: str
    output: Any


@router.get("/health", response_model=HealthResponse)
async def health(
    ollama: Annotated[OllamaProvider, Depends(get_ollama)],
    registry: Annotated[TaskRegistry, Depends(get_registry)],
) -> HealthResponse:
    reachable = await ollama.health()
    return HealthResponse(
        status="ok" if reachable else "degraded",
        ollama_reachable=reachable,
        warm_model=registry.warm_model,
    )


@router.get("/tasks", response_model=list[TaskListItem])
async def list_tasks(
    registry: Annotated[TaskRegistry, Depends(get_registry)],
    _: Annotated[None, Depends(require_bearer)],
) -> list[TaskListItem]:
    return [
        TaskListItem(
            name=c.name,
            provider=c.provider,
            model=c.model,
            output_schema=c.output_schema,
        )
        for c in registry.all()
    ]


@router.post("/task/{name}", response_model=TaskResponse)
async def run_task(
    name: str,
    payload: TaskInput,
    registry: Annotated[TaskRegistry, Depends(get_registry)],
    locks: Annotated[ModelLocks, Depends(get_locks)],
    _: Annotated[None, Depends(require_bearer)],
) -> TaskResponse:
    try:
        entry = registry.get(name)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    logger.info("task_invoked", task=name, model=entry.config.model)

    async with locks.acquire(entry.config.model):
        result = await entry.agent.run(payload.input)

    output: Any
    if entry.output_type is None:
        output = str(result.output)
    else:
        output = (
            result.output.model_dump() if isinstance(result.output, BaseModel) else result.output
        )

    return TaskResponse(task=name, model=entry.config.model, output=output)
