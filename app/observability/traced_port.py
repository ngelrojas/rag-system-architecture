# app/observability/traced_port.py — 6.2
#
# A decorator-style wrapper, not a new abstraction. It wraps an existing
# port implementation and logs a span around every call — the port's
# callers (the domain core) never know this wrapping exists.
#
# The core has exactly three outbound chokepoints on the answer path —
# EmbeddingPort, RetrievalPort, LLMPort — so wrapping each once gives
# complete coverage of every request.
import time
import uuid
from collections.abc import Callable

import structlog

from app.ports import EmbeddingPort, LLMPort, RetrievalPort, RetrievedChunk

log = structlog.get_logger()

def _span[T](trace_id: str, port: str, call: Callable[[], T], **start_fields: object) -> T:
    span_id = str(uuid.uuid4())
    start = time.monotonic()
    log.info("port_call_start", trace_id=trace_id, span_id=span_id, port=port, **start_fields)
    try:
        result = call()
    except Exception as e:
        log.error("port_call_end", trace_id=trace_id, span_id=span_id, port=port,
                  latency_ms=(time.monotonic() - start) * 1000, status="error", error=str(e))
        raise
    log.info("port_call_end", trace_id=trace_id, span_id=span_id, port=port,
             latency_ms=(time.monotonic() - start) * 1000, status="success")
    return result


class TracedLLMPort(LLMPort):
    """Wraps any LLMPort implementation with structured span logging.
    Composition, not inheritance — this can wrap OpenAILLM, a local
    model adapter, anything satisfying LLMPort."""

    def __init__(self, inner: LLMPort, trace_id: str):
        self._inner = inner
        self._trace_id = trace_id

    def complete(self, prompt: str) -> str:
        return _span(self._trace_id, "LLMPort", lambda: self._inner.complete(prompt), prompt_chars=len(prompt))


class TracedEmbeddingPort(EmbeddingPort):
    def __init__(self, inner: EmbeddingPort, trace_id: str):
        self._inner = inner
        self._trace_id = trace_id

    def embed(self, text: str) -> list[float]:
        return _span(self._trace_id, "EmbeddingPort", lambda: self._inner.embed(text), text_chars=len(text))


class TracedRetrievalPort(RetrievalPort):
    def __init__(self, inner: RetrievalPort, trace_id: str):
        self._inner = inner
        self._trace_id = trace_id

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        results = _span(self._trace_id, "RetrievalPort", lambda: self._inner.search(embedding, top_k), top_k=top_k)
        # Provenance (6.2): what came back, with scores, under the same trace_id.
        log.info("retrieval_results", trace_id=self._trace_id, count=len(results),
                 top_score=max((r.score for r in results), default=None))
        return results
