# app/core/commands.py — the write side's model (4.2, after the 4.4 refactor)
from dataclasses import dataclass


@dataclass
class IngestDocumentCommand:
    doc_id: str
    text: str


@dataclass
class IngestResult:
    doc_id: str
    chunks_ingested: int
    succeeded: bool
    # No answer data, no candidates, no chunks returned.
    # Only confirmation that the write happened.
