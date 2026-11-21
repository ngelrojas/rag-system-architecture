# app/core/chunking.py — 2.2, moved into the core in 3.3
#
# In the naive pipeline, chunk size was a literal 500 on line one of
# ingest_document: a decision that changes what can ever be retrieved,
# made by nobody in particular. Here it becomes an explicit, named,
# testable domain decision. Later chapters pass chunk_size in from Settings.

DEFAULT_CHUNK_SIZE = 500


def split_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """Split text into fixed-size character windows.

    Deliberately simple. The point of 2.2 is not a cleverer splitter, it is
    that the strategy now lives in one place the domain owns.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
