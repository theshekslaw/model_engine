from pathlib import Path
from textwrap import dedent
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from model_engine.main import create_app
from model_engine.settings import Settings
from model_engine.tasks.schemas import PaperSummary


@pytest.fixture
def tasks_yaml(tmp_path: Path) -> Path:
    path = tmp_path / "tasks.yaml"
    path.write_text(
        dedent(
            """
            warm_model: qwen2.5:3b
            tasks:
              chat:
                provider: ollama
                model: qwen2.5:3b
                system_prompt: Say hi.
                output_schema: null
              summarize_paper:
                provider: ollama
                model: qwen2.5:7b
                system_prompt: Summarize.
                output_schema: PaperSummary
            """
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def client(tasks_yaml: Path) -> TestClient:
    settings = Settings(
        service_name="test",
        auth_token="test-token",
        warm_on_startup=False,
        task_config_path=tasks_yaml,
        log_json=False,
    )
    # Skip real Ollama probing on startup.
    with patch(
        "model_engine.providers.ollama.OllamaProvider.health", new=AsyncMock(return_value=True)
    ):
        app = create_app(settings=settings)
        with TestClient(app) as c:
            yield c


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["warm_model"] == "qwen2.5:3b"


def test_tasks_requires_auth(client: TestClient) -> None:
    response = client.get("/tasks")
    assert response.status_code == 401


def test_tasks_lists(client: TestClient) -> None:
    response = client.get("/tasks", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    names = {t["name"] for t in response.json()}
    assert names == {"chat", "summarize_paper"}


def test_unknown_task_404(client: TestClient) -> None:
    response = client.post(
        "/task/nope",
        headers={"Authorization": "Bearer test-token"},
        json={"input": "hi"},
    )
    assert response.status_code == 404


def test_run_task_structured_output(client: TestClient) -> None:
    fake_summary = PaperSummary(
        tldr="tldr",
        contributions=["c1"],
        methodology="m",
        limitations=[],
        keywords=["k"],
    )

    class FakeResult:
        output: Any = fake_summary

    with patch("pydantic_ai.Agent.run", new=AsyncMock(return_value=FakeResult())):
        response = client.post(
            "/task/summarize_paper",
            headers={"Authorization": "Bearer test-token"},
            json={"input": "some paper text"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["task"] == "summarize_paper"
    assert body["model"] == "qwen2.5:7b"
    assert body["output"]["tldr"] == "tldr"
    assert body["output"]["contributions"] == ["c1"]


def test_run_task_free_form(client: TestClient) -> None:
    class FakeResult:
        output: Any = "hello world"

    with patch("pydantic_ai.Agent.run", new=AsyncMock(return_value=FakeResult())):
        response = client.post(
            "/task/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"input": "hi"},
        )
    assert response.status_code == 200
    assert response.json()["output"] == "hello world"
