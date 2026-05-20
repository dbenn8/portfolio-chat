# tests/test_weaviate_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_chunk_text_basic():
    from app.weaviate_client import chunk_text
    text = "Word " * 100  # 100 words
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    assert len(chunks) >= 2
    assert all(len(c.split()) <= 55 for c in chunks)  # allow small overshoot


def test_chunk_text_short():
    from app.weaviate_client import chunk_text
    text = "Short text."
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunk_text_preserves_content():
    from app.weaviate_client import chunk_text
    words = [f"word{i}" for i in range(200)]
    text = " ".join(words)
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    reassembled = set()
    for chunk in chunks:
        for w in chunk.split():
            reassembled.add(w)
    for w in words:
        assert w in reassembled, f"Lost word: {w}"
