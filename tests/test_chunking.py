# tests/test_chunking.py — 2.2
import pytest

from app.core.chunking import split_into_chunks


def test_fixed_windows() -> None:
    assert split_into_chunks("a" * 500, chunk_size=100) == ["a" * 100] * 5


def test_last_chunk_may_be_short() -> None:
    assert split_into_chunks("abcdefg", chunk_size=3) == ["abc", "def", "g"]


def test_empty_text_has_no_chunks() -> None:
    assert split_into_chunks("") == []


def test_chunk_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        split_into_chunks("text", chunk_size=0)
