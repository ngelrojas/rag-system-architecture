# tests/test_ingest_service_client.py — 3.7, the seam already exists
import httpx

from app.adapters.ingest_service_client import IngestServiceClient
from app.core.commands import IngestDocumentCommand


def test_remote_ingestion_has_the_same_call_shape() -> None:
    def remote_service(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/ingest"
        return httpx.Response(200, json={"doc_id": "doc-9", "chunks_ingested": 4, "succeeded": True})

    transport = httpx.MockTransport(remote_service)
    client = IngestServiceClient("http://ingest.internal", client=httpx.Client(transport=transport))
    result = client.handle(IngestDocumentCommand(doc_id="doc-9", text="..."))

    assert result.succeeded and result.chunks_ingested == 4
