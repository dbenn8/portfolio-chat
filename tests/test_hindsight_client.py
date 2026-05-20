# tests/test_hindsight_client.py


def test_chunk_text_basic():
    from app.hindsight_client import chunk_text
    text = "Word " * 100
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    assert len(chunks) >= 2
    assert all(len(c.split()) <= 55 for c in chunks)


def test_chunk_text_short():
    from app.hindsight_client import chunk_text
    text = "Short text."
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunk_text_preserves_content():
    from app.hindsight_client import chunk_text
    words = [f"word{i}" for i in range(200)]
    text = " ".join(words)
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    reassembled = set()
    for chunk in chunks:
        for w in chunk.split():
            reassembled.add(w)
    for w in words:
        assert w in reassembled, f"Lost word: {w}"
