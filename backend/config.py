import os

from dotenv import load_dotenv

load_dotenv()

EMBEDDING_DIM = 384  # fixed by the database schema

DATABASE_URL = os.getenv("DATABASE_URL", "")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "hash")  # hash | openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))  # characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "5"))
