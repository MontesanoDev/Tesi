import pytest

from app.ingestion import chunk_text


@pytest.mark.parametrize("separator", [" ", "\n", "\r\n"])
def test_chunks_preserve_words_at_both_boundaries(separator):
    words = ["Professionisti", "proposti", "incarico", "qualifiche", "documentate"] * 12
    chunks = chunk_text(separator.join(words), chunk_size=70, overlap=17)
    assert len(chunks) > 1
    assert all(0 < len(chunk) <= 70 for chunk in chunks)
    assert all(word in words for chunk in chunks for word in chunk.split())
    # With unique tokens, the union also checks that adjusting overlap loses no words.
    unique = [f"parola{index:03d}" for index in range(100)]
    chunks = chunk_text(separator.join(unique), chunk_size=70, overlap=17)
    assert {word for chunk in chunks for word in chunk.split()} == set(unique)


def test_short_chunk_before_a_long_word_does_not_split_that_word():
    token = "x" * 60
    chunks = chunk_text(f"Inizio {token} fine", chunk_size=64, overlap=12)
    assert any(token in chunk.split() for chunk in chunks)
    assert {word for chunk in chunks for word in chunk.split()} == {"Inizio", token, "fine"}


def test_oversized_unbroken_text_still_progresses_with_a_bounded_chunk_size():
    text = "x" * 160
    chunks = chunk_text(text, chunk_size=64, overlap=12)
    assert all(0 < len(chunk) <= 64 for chunk in chunks)
    assert "".join(chunks) == text


@pytest.mark.parametrize("size,overlap", [(0, 0), (-1, 0), (10, -1), (10, 10), (10, 11)])
def test_invalid_chunk_parameters_are_rejected(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("Testo di prova", chunk_size=size, overlap=overlap)
