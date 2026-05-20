# app/hindsight_client.py
import httpx
from app.config import settings

BANK_ID = "portfolio"


def _headers():
    return {
        "Authorization": f"Bearer {settings.hindsight_api_key}",
        "Content-Type": "application/json",
    }


def _base_url():
    return f"{settings.hindsight_url}/v1/default/banks/{BANK_ID}/memory"


async def retain(content: str, context: str, metadata: dict, document_id: str, tags: list[str] | None = None):
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "content": content,
            "context": context,
            "metadata": metadata,
            "document_id": document_id,
        }
        if tags:
            payload["tags"] = tags
        response = await client.post(
            f"{_base_url()}/retain",
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
                "chunks": True,
                "source_facts": True,
                "entities": True,
            },
        }
        response = await client.post(
            f"{_base_url()}/recall",
            json=payload,
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


def chunk_text(text: str, max_tokens: int = 250, overlap_tokens: int = 50) -> list[str]:
    """Keep chunking for ingestion — Hindsight handles long content but
    we want to retain with reasonable document sizes and good metadata."""
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
