import re


def chunk_text(text: str, size: int = 600, overlap: int = 100) -> list[str]:
    """Split text into chunks of roughly `size` characters.

    Paragraphs are kept together where possible; a paragraph longer than
    `size` is split on sentence boundaries. Consecutive chunks share up to
    `overlap` characters so answers that straddle a boundary stay retrievable.
    """
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("require size > 0 and 0 <= overlap < size")

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    for para in paragraphs:
        if len(para) <= size:
            pieces.append(para)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", para)
        current = ""
        for sentence in sentences:
            while len(sentence) > size:  # a single huge sentence
                if current:
                    pieces.append(current)
                    current = ""
                pieces.append(sentence[:size])
                sentence = sentence[size:]
            if current and len(current) + 1 + len(sentence) > size:
                pieces.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            pieces.append(current)

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if current and len(current) + 2 + len(piece) > size:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{piece}".strip() if tail else piece
            if len(current) > size:  # overlap pushed us over; drop the tail
                current = piece
        else:
            current = f"{current}\n\n{piece}".strip()
    if current:
        chunks.append(current)
    return chunks
