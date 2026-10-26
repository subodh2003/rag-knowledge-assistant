import pytest
from chunking import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_empty_text_gives_no_chunks():
    assert chunk_text("  \n\n  ") == []


def test_chunks_respect_size_limit():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 40 for i in range(20))
    chunks = chunk_text(text, size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)


def test_long_paragraph_splits_on_sentences():
    text = " ".join(f"Sentence number {i} is here." for i in range(60))
    chunks = chunk_text(text, size=200, overlap=0)
    assert all(len(c) <= 200 for c in chunks)
    assert "Sentence number 59 is here." in chunks[-1]


def test_overlap_repeats_tail_of_previous_chunk():
    text = "\n\n".join(f"Unique paragraph marker{i} " + "filler " * 20 for i in range(6))
    chunks = chunk_text(text, size=250, overlap=40)
    assert len(chunks) > 1
    last_word = chunks[0].split()[-1]
    assert last_word in chunks[1]
    for c in chunks[1:]:
        assert c.split()[0] in ("Unique", "paragraph", "filler") or c.split()[0].startswith("marker")


def test_invalid_parameters():
    with pytest.raises(ValueError):
        chunk_text("x", size=100, overlap=100)
