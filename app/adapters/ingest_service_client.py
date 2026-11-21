# app/adapters/ingest_service_client.py — 3.7, "the option is already paid for"
#
# Today the composition root wires IngestDocumentHandler in-process. If
# ingestion load ever justifies a separate service, this adapter takes its
# place: same call shape, forwarded over HTTP. IngestDocumentHandler itself
# never changes — it just runs inside the other service.
from dataclasses import asdict

import httpx

from app.core.commands import IngestDocumentCommand, IngestResult


class IngestServiceClient:
    """Implements the same call shape IngestDocumentHandler exposes,
    but forwards over the network to a separately deployed service."""

    def __init__(self, ingest_service_url: str, client: httpx.Client | None = None) -> None:
        self._ingest_service_url = ingest_service_url.rstrip("/")
        self._client = client or httpx.Client(timeout=30.0)

    def handle(self, command: IngestDocumentCommand) -> IngestResult:
        response = self._client.post(f"{self._ingest_service_url}/ingest", json=asdict(command))
        response.raise_for_status()
        return IngestResult(**response.json())
