DOC_A = (
    "Refunds can be issued in full or in part within 180 days of the original payment. "
    "Card refunds appear on the statement within five to ten business days."
)
DOC_B = (
    "Webhook requests carry an HMAC signature in the Acme-Signature header. "
    "Verify the signature with your signing secret and reject old timestamps."
)


def ingest(client, title, text):
    r = client.post("/documents", json={"title": title, "text": text})
    assert r.status_code == 201, r.text
    return r.json()


def test_health_and_ready(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_ingest_and_list(client):
    doc = ingest(client, "refunds", DOC_A)
    assert doc["chunks"] >= 1
    docs = client.get("/documents").json()
    assert [d["title"] for d in docs] == ["refunds"]
    assert docs[0]["chunks"] == doc["chunks"]


def test_query_returns_most_relevant_source_first(client):
    ingest(client, "refunds", DOC_A)
    ingest(client, "webhooks", DOC_B)

    r = client.post("/query", json={"question": "How do I verify a webhook signature?"})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "extractive"  # no API key in tests
    assert body["sources"][0]["title"] == "webhooks"
    assert "HMAC" in body["answer"]

    r = client.post("/query", json={"question": "How long do I have to refund a payment?"})
    assert r.json()["sources"][0]["title"] == "refunds"


def test_query_with_no_documents(client):
    body = client.post("/query", json={"question": "anything?"}).json()
    assert body["sources"] == []
    assert "No documents" in body["answer"]


def test_delete_document_removes_its_chunks(client):
    doc = ingest(client, "refunds", DOC_A)
    assert client.delete(f"/documents/{doc['id']}").status_code == 204
    assert client.get("/documents").json() == []
    assert client.post("/query", json={"question": "refund"}).json()["sources"] == []
    assert client.delete(f"/documents/{doc['id']}").status_code == 404


def test_validation_errors(client):
    assert client.post("/documents", json={"title": "", "text": "x"}).status_code == 422
    assert client.post("/documents", json={"title": "t", "text": ""}).status_code == 422
    assert client.post("/query", json={"question": "q", "top_k": 99}).status_code == 422


def test_whitespace_only_document_rejected(client):
    r = client.post("/documents", json={"title": "blank", "text": "   \n\n  "})
    assert r.status_code == 422


def test_upload_text_file(client):
    r = client.post(
        "/documents/upload",
        files={"file": ("notes.md", DOC_A.encode(), "text/markdown")},
    )
    assert r.status_code == 201
    assert r.json()["title"] == "notes.md"


def test_upload_binary_rejected(client):
    r = client.post(
        "/documents/upload",
        files={"file": ("x.bin", b"\xff\xfe\x00\x01", "application/octet-stream")},
    )
    assert r.status_code == 415
