from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from app.llm_service import LLMService
from app.weaviate_client import search

router = APIRouter()

SYSTEM_PROMPT = """You are Dan Bennett's portfolio assistant. You help visitors learn about Dan's projects, technical skills, and professional background.

Rules:
- Answer based ONLY on the provided context. If the context doesn't contain the answer, say so honestly.
- Speak in third person about Dan ("Dan built...", "His approach was...")
- Do NOT add citations or source links — the system appends these automatically after your response.
- Be honest about what Dan built vs what teams/contractors built
- Keep responses concise — 2-3 paragraphs max unless asked for more detail
- Don't hallucinate projects, technologies, or capabilities not in the context
- If asked about availability, location, or contact: Dan is based in Haarlem, Netherlands (near Amsterdam), open to remote/hybrid roles, reachable at dantana@gmail.com or linkedin.com/in/dbenn8"""


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


SLUG_MAP = {
    "overnight-briefing": "/projects/overnight-briefing",
    "mbo-listing-sync": "/projects/mbo-listing-sync",
    "burrfect-pipeline": "/projects/burrfect-pipeline",
    "burrfect-water": "/projects/burrfect-water",
    "btc-backtesting": "/projects/btc-backtesting",
    "woordjes": "/projects/woordjes",
    "claude-slack": "/projects/claude-slack",
    "kumpel-ai": "/projects/kumpel-ai",
    "project-orchestrator": "/projects/project-orchestrator",
    "n8n": "/n8n",
    "index": "/",
}


def source_to_slug(source: str) -> str | None:
    stem = source.replace(".astro", "").replace(".md", "")
    return SLUG_MAP.get(stem)


def _resolve_slug(r: dict) -> str | None:
    slug = r.get("slug")
    if slug:
        return SLUG_MAP.get(slug, f"/projects/{slug}")
    return source_to_slug(r["source"])


def build_context(results: list[dict]) -> str:
    sections = []
    for r in results:
        slug = _resolve_slug(r)
        source_tag = f"[Source: {r['project']} — {slug}]" if slug else f"[Source: {r['project']}]"
        sections.append(f"{source_tag}\n{r['text']}")
    return "\n\n---\n\n".join(sections)


def build_source_links(results: list[dict]) -> str:
    seen = {}
    for r in results:
        slug = _resolve_slug(r)
        project = r["project"]
        if slug and project not in seen:
            seen[project] = slug
    if not seen:
        return ""
    return " · ".join(f"[{name}]({path})" for name, path in seen.items())


@router.post("/api/chat")
async def chat(request: ChatRequest):
    llm = LLMService()
    query_vector = await llm.embed(request.message)
    results = search(request.message, query_vector, top_k=5)
    context = build_context(results)
    sources = build_source_links(results)

    messages = [
        {
            "role": "user",
            "content": f"Context from Dan's portfolio:\n\n{context}\n\n---\n\nUser question: {request.message}",
        }
    ]

    async def event_generator():
        async for chunk in llm.chat_stream(messages, SYSTEM_PROMPT):
            yield {"data": chunk}
        if sources:
            yield {"data": "\n\n---\n**Sources:** " + sources}
        yield {"data": "[DONE]"}

    return EventSourceResponse(event_generator())
