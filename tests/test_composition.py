# tests/test_composition.py — the composition root wires real adapters (3.4)
from app.composition import build_application
from app.config import Settings


def test_composition_root_builds_the_application() -> None:
    settings = Settings(openai_api_key="sk-test-not-used", qdrant_url=":memory:")
    application = build_application(settings)
    assert application.query_handler is not None
    assert application.ingest_handler is not None
