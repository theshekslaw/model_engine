from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from model_engine.providers.ollama import OllamaProvider
from model_engine.router.locks import ModelLocks
from model_engine.settings import Settings
from model_engine.tasks.registry import TaskRegistry

_bearer = HTTPBearer(auto_error=False)


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_registry(request: Request) -> TaskRegistry:
    registry: TaskRegistry = request.app.state.registry
    return registry


def get_ollama(request: Request) -> OllamaProvider:
    ollama: OllamaProvider = request.app.state.ollama
    return ollama


def get_locks(request: Request) -> ModelLocks:
    locks: ModelLocks = request.app.state.locks
    return locks


def require_bearer(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    expected = settings.auth_token
    if not expected:
        return  # dev mode: token unset ⇒ auth disabled
    if credentials is None or credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
