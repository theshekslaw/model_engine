from pathlib import Path
from textwrap import dedent

import pytest

from model_engine.providers.ollama import OllamaProvider
from model_engine.tasks.registry import load_registry


@pytest.fixture
def ollama() -> OllamaProvider:
    return OllamaProvider(base_url="http://localhost:11434", keep_alive="5m")


def _write_yaml(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "tasks.yaml"
    path.write_text(dedent(body), encoding="utf-8")
    return path


def test_load_registry_parses_tasks(tmp_path: Path, ollama: OllamaProvider) -> None:
    path = _write_yaml(
        tmp_path,
        """
        warm_model: qwen2.5:3b
        tasks:
          chat:
            provider: ollama
            model: qwen2.5:3b
            system_prompt: hello
            output_schema: null
          summarize_paper:
            provider: ollama
            model: qwen2.5:7b
            system_prompt: sum
            output_schema: PaperSummary
        """,
    )
    registry = load_registry(config_path=path, ollama=ollama)

    assert registry.warm_model == "qwen2.5:3b"
    names = {c.name for c in registry.all()}
    assert names == {"chat", "summarize_paper"}
    assert registry.models() == {"qwen2.5:3b", "qwen2.5:7b"}

    chat = registry.get("chat")
    assert chat.config.output_schema is None
    assert chat.output_type is None

    summarize = registry.get("summarize_paper")
    assert summarize.config.output_schema == "PaperSummary"
    assert summarize.output_type is not None
    assert summarize.output_type.__name__ == "PaperSummary"


def test_load_registry_missing_file(tmp_path: Path, ollama: OllamaProvider) -> None:
    with pytest.raises(FileNotFoundError):
        load_registry(config_path=tmp_path / "nope.yaml", ollama=ollama)


def test_load_registry_empty_tasks(tmp_path: Path, ollama: OllamaProvider) -> None:
    path = _write_yaml(tmp_path, "warm_model: x\ntasks: {}\n")
    with pytest.raises(ValueError, match="No tasks defined"):
        load_registry(config_path=path, ollama=ollama)


def test_load_registry_unknown_provider(tmp_path: Path, ollama: OllamaProvider) -> None:
    path = _write_yaml(
        tmp_path,
        """
        warm_model: qwen2.5:3b
        tasks:
          x:
            provider: openai
            model: gpt-4
        """,
    )
    with pytest.raises(ValueError, match="only 'ollama' is implemented"):
        load_registry(config_path=path, ollama=ollama)


def test_load_registry_unknown_schema(tmp_path: Path, ollama: OllamaProvider) -> None:
    path = _write_yaml(
        tmp_path,
        """
        warm_model: qwen2.5:3b
        tasks:
          x:
            provider: ollama
            model: qwen2.5:3b
            output_schema: NotARealSchema
        """,
    )
    with pytest.raises(ValueError, match="Unknown output_schema"):
        load_registry(config_path=path, ollama=ollama)


def test_bundled_config_loads(ollama: OllamaProvider) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    registry = load_registry(config_path=repo_root / "config" / "tasks.yaml", ollama=ollama)
    assert registry.warm_model == "qwen2.5:3b"
    names = {c.name for c in registry.all()}
    assert {"chat", "summarize_paper", "mindmap", "code"} <= names
