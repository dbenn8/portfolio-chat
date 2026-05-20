from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from app.llm_service import LLMService
from app.weaviate_client import search
from app.rate_limit import chat_limiter

router = APIRouter()

_sessions: dict[str, list[dict]] = {}
MAX_HISTORY = 10


def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def save_turn(session_id: str, role: str, content: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})
    if len(_sessions[session_id]) > MAX_HISTORY:
        _sessions[session_id] = _sessions[session_id][-MAX_HISTORY:]


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
async def chat(request_body: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not chat_limiter.check(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in an hour.")

    llm = LLMService()
    query_vector = await llm.embed(request_body.message)
    results = search(request_body.message, query_vector, top_k=5)
    context = build_context(results)
    sources = build_source_links(results)

    session_id = request_body.session_id or "anonymous"
    history = get_history(session_id)

    messages = history + [
        {
            "role": "user",
            "content": f"Context from Dan's portfolio:\n\n{context}\n\n---\n\nUser question: {request_body.message}",
        }
    ]

    async def event_generator():
        full_response = ""
        async for chunk in llm.chat_stream(messages, SYSTEM_PROMPT):
            full_response += chunk
            yield {"data": chunk}
        if sources:
            source_line = "\n\n---\n**Sources:** " + sources
            full_response += source_line
            yield {"data": source_line}
        save_turn(session_id, "user", request_body.message)
        save_turn(session_id, "assistant", full_response)
        yield {"data": "[DONE]"}

    return EventSourceResponse(event_generator())
