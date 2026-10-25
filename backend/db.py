import config
from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool

SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id           SERIAL PRIMARY KEY,
    document_id  INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  INTEGER NOT NULL,
    content      TEXT NOT NULL,
    embedding    vector({config.EMBEDDING_DIM}) NOT NULL
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_document_idx ON chunks (document_id);
"""

_pool: ConnectionPool | None = None


def init_schema(database_url: str) -> None:
    """Create the extension and tables. Runs on a plain connection first so the
    vector type exists before the pool registers it."""
    import psycopg

    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute(SCHEMA)


def open_pool() -> ConnectionPool:
    global _pool
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    init_schema(config.DATABASE_URL)
    _pool = ConnectionPool(
        conninfo=config.DATABASE_URL,
        min_size=1,
        max_size=config.DB_POOL_MAX_SIZE,
        configure=register_vector,
        open=True,
        timeout=10,
    )
    return _pool


def get_pool() -> ConnectionPool:
    if _pool is None:
        raise RuntimeError("database pool is not open")
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
