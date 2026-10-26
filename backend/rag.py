import config
import numpy as np
from chunking import chunk_text
from db import get_pool
from embeddings import embed


def ingest_document(title: str, text: str) -> dict:
    chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    if not chunks:
        raise ValueError("document has no text")
    vectors = embed(chunks)  # embed before opening a transaction
    with get_pool().connection() as conn:
        with conn.transaction():
            # re-ingesting a title replaces the old copy instead of duplicating it
            conn.execute("DELETE FROM documents WHERE title = %s", (title,))
            doc_id = conn.execute(
                "INSERT INTO documents (title) VALUES (%s) RETURNING id", (title,)
            ).fetchone()[0]
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO chunks (document_id, chunk_index, content, embedding)"
                    " VALUES (%s, %s, %s, %s)",
                    [
                        (doc_id, i, content, np.array(vec))
                        for i, (content, vec) in enumerate(zip(chunks, vectors))
                    ],
                )
    return {"id": doc_id, "title": title, "chunks": len(chunks)}


def retrieve(question: str, top_k: int = 4) -> list[dict]:
    query_vec = np.array(embed([question])[0])
    with get_pool().connection() as conn:
        rows = conn.execute(
            """
            SELECT c.document_id, d.title, c.chunk_index, c.content,
                   1 - (c.embedding <=> %s) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %s
            LIMIT %s
            """,
            (query_vec, query_vec, top_k),
        ).fetchall()
    return [
        {
            "document_id": r[0],
            "title": r[1],
            "chunk_index": r[2],
            "content": r[3],
            "score": round(float(r[4]), 4),
        }
        for r in rows
    ]


def list_documents() -> list[dict]:
    with get_pool().connection() as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.title, d.created_at, count(c.id)
            FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id ORDER BY d.id
            """
        ).fetchall()
    return [
        {"id": r[0], "title": r[1], "created_at": r[2].isoformat(), "chunks": r[3]}
        for r in rows
    ]


def delete_document(doc_id: int) -> bool:
    with get_pool().connection() as conn:
        cur = conn.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
        return cur.rowcount > 0
