import os

import pytest
from fastapi.testclient import TestClient

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("TEST_DATABASE_URL not set", allow_module_level=True)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["EMBEDDING_PROVIDER"] = "hash"
os.environ["ANTHROPIC_API_KEY"] = ""

import config  # noqa: E402

config.DATABASE_URL = TEST_DATABASE_URL
config.EMBEDDING_PROVIDER = "hash"
config.ANTHROPIC_API_KEY = ""

import db  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        with db.get_pool().connection() as conn:
            conn.execute("TRUNCATE chunks, documents RESTART IDENTITY CASCADE")
        yield c
