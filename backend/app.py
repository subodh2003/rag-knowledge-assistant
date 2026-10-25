from contextlib import asynccontextmanager
from pathlib import Path

import db
import httpx
import rag
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from llm import generate_answer
from pydantic import BaseModel, Field


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.open_pool()
    yield
    db.close_pool()


app = FastAPI(title="RAG Knowledge Assistant", lifespan=lifespan)


class DocumentIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=500_000)


class QueryIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        with db.get_pool().connection() as conn:
            conn.execute("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready"}


@app.post("/documents", status_code=201)
def add_document(doc: DocumentIn):
    try:
        return rag.ingest_document(doc.title, doc.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="embedding provider error") from exc


@app.post("/documents/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), title: str = Form("")):
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=415, detail="only UTF-8 text/markdown files") from exc
    return add_document(DocumentIn(title=title or file.filename or "untitled", text=text))


@app.get("/documents")
def get_documents():
    return rag.list_documents()


@app.delete("/documents/{doc_id}", status_code=204)
def remove_document(doc_id: int):
    if not rag.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="document not found")


@app.post("/query")
def query(q: QueryIn):
    try:
        passages = rag.retrieve(q.question, q.top_k)
        result = generate_answer(q.question, passages)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="upstream model error") from exc
    return {"question": q.question, **result, "sources": passages}


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
