from indexing.chunking import chunk_text


def test_chunking_is_stable():
    text = "a" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 3
    assert chunks[0] == "a" * 500
    assert chunks[1].startswith("a" * 50)
