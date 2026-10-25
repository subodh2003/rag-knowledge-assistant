import config
import httpx

SYSTEM_PROMPT = (
    "You answer questions using only the provided context passages. "
    "Cite passages as [1], [2], etc. If the context does not contain the answer, "
    "say you don't know. Be concise."
)


def generate_answer(question: str, passages: list[dict]) -> dict:
    """Return {"answer": str, "mode": "llm" | "extractive"}.

    With ANTHROPIC_API_KEY set, the retrieved passages are sent to Claude.
    Without it, the best passage is returned as-is, so the service still works
    (and CI never needs a secret).
    """
    if not passages:
        return {"answer": "No documents have been ingested yet.", "mode": "extractive"}

    if not config.ANTHROPIC_API_KEY:
        return {"answer": passages[0]["content"], "mode": "extractive"}

    context = "\n\n".join(f"[{i}] {p['content']}" for i, p in enumerate(passages, 1))
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": config.LLM_MODEL,
            "max_tokens": 600,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                }
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    blocks = response.json()["content"]
    text = "".join(b["text"] for b in blocks if b["type"] == "text")
    return {"answer": text, "mode": "llm"}
