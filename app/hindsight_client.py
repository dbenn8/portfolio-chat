# app/hindsight_client.py
import httpx
from app.config import settings

BANK_ID = "portfolio"


def _headers():
    return {
        "Authorization": f"Bearer {settings.hindsight_api_key}",
        "Content-Type": "application/json",
    }


def _bank_url():
    return f"{settings.hindsight_url}/v1/default/banks/{BANK_ID}"


async def retain(content: str, context: str, metadata: dict, document_id: str, tags: list[str] | None = None):
    async with httpx.AsyncClient(timeout=120.0) as client:
        item = {
            "content": content,
            "context": context,
            "metadata": metadata,
            "document_id": document_id,
        }
        if tags:
            item["tags"] = tags
        payload = {"items": [item]}
        response = await client.post(
            f"{_bank_url()}/memories",
            json=payload,
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


async def recall(query: str, budget: str = "mid", max_tokens: int = 4096) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "query": query,
            "budget": budget,
            "max_tokens": max_tokens,
            "include": {
                "chunks": {},
                "source_facts": {},
                "entities": {"max_tokens": 500},
            },
        }
        response = await client.post(
            f"{_bank_url()}/memories/recall",
            json=payload,
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


def chunk_text(text: str, max_tokens: int = 250, overlap_tokens: int = 50) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_tokens
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap_tokens
    return chunks
