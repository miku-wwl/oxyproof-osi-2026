import pytest
from fastapi.testclient import TestClient

from backend.app.data.ingest import Repository


@pytest.fixture(scope="session")
def repo():
    return Repository(fixture_only=True)


@pytest.fixture
def client(repo, monkeypatch):
    import backend.app.main as module

    monkeypatch.setattr(module, "repository", lambda: repo)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OXYPROOF_LLM_MODEL", raising=False)
    with TestClient(module.app) as client:
        yield client
