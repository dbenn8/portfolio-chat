# Portfolio Chatbot Design (Kumpel.ai Revival)

**Date:** 2026-05-20
**Status:** Approved
**Target:** n8n AI Product Builder application — meta-flex: the portfolio is powered by a chatbot Dan built

---

## Overview

Revive Kumpel.ai as a portfolio chatbot that answers questions about Dan's projects, tech stack, and background. Embedded as a floating widget on the portfolio site. New repo, modern stack, Weaviate vector DB for RAG.

## Architecture

Single application — FastAPI serves both the static portfolio site AND the chat API.

### Unified App (`codeNew/portfolio-chat/`)

FastAPI app deployed on Appliku with a multi-stage Docker build:
- **Stage 1 (Node):** Builds the Astro portfolio site to static HTML
- **Stage 2 (Python):** FastAPI serves the static files at `/` and the chat API at `/api/*`

**Endpoints:**
- `GET /*` — serves static portfolio site (Astro build output)
- `POST /api/chat` — accepts `{ message, session_id? }`, streams response via SSE
- `POST /api/ingest` — re-index portfolio content (API key protected)
- `GET /api/health` — healthcheck

**Dependencies:**
- `fastapi` + `uvicorn` — API framework + static file serving
- `weaviate-client` — Weaviate Cloud Python client
- `anthropic` — Claude API (default LLM)
- `openai` — OpenAI API (fallback LLM) + embeddings
- `greenpt` - Openai compatible privacy and environmental impact focused provider: https://api.greenpt.ai/v1/models
- `httpx` — for local LLM OpenAI-compatible calls
- `sse-starlette` — Server-Sent Events for streaming

### Chat Widget

Vanilla JS file (~200 lines) served as a static asset from the same app (no cross-origin needed).

Features:
- Floating bubble icon (bottom-right corner)
- Expandable chat panel with message history
- Streams responses character-by-character via SSE
- Minimal inline markdown renderer (bold, links, lists, code)
- Configurable greeting message
- Responsive — works on mobile
- No CORS complexity — same origin

## Data Flow

```
Portfolio .astro files + AI Builder Summary .md files
  ↓ (ingest.py: extract text, chunk, embed)
Weaviate Cloud (collection: "Portfolio")
  ↓ (on chat: similarity search, top_k=5)
System prompt + retrieved context + user message
  ↓ (LLM: Claude Sonnet / OpenAI / local)
Streaming SSE response
  ↓
Chat widget renders in browser
```

## Ingestion Pipeline (`ingest.py`)

A CLI script that:

1. **Reads portfolio content:**
   - All `.astro` files from `../portfolio/src/pages/` and `../portfolio/src/pages/projects/`
   - Strips Astro frontmatter and HTML tags, extracts clean text
   - Preserves section structure (headings become metadata)

2. **Reads AI Builder Summaries:**
   - Glob pattern: `~/codeNew/*/AI Builder Summary for *.md` + `~/Documents/Claude/**/AI Builder Summary for *.md` + `~/marvin/AI Builder Summary for *.md` + `~/marvin/Meal Planning/AI Builder Summary for *.md` + `~/projects/*/AI Builder Summary for *.md` + `~/llm/AI Builder Summary for *.md`
   - These contain deeper technical analysis than the portfolio pages

3. **Chunks text:**
   - ~250 token segments with 50 token overlap
   - Each chunk tagged with metadata: `source` (filename), `project` (project name), `section` (heading), `type` ("portfolio" or "summary")

4. **Embeds and upserts:**
   - Greenpt `green-embedding` for embeddings
    https://docs.greenpt.ai/api/models
   - Upsert to Weaviate Cloud collection "Portfolio"
   - Idempotent — safe to re-run after content changes

**Run manually:** `python ingest.py`
**Run via API:** `POST /api/ingest` with `X-API-Key` header

## Configurable LLM Layer (`llm_service.py`)

Abstraction over multiple providers (same pattern as Woordjes `LLMService`):

```python
class LLMService:
    def __init__(self, provider: str = None):
        # provider from env var LLM_PROVIDER or parameter
        # "claude" (default), "openai", "local"

    async def chat_stream(self, messages, system_prompt) -> AsyncGenerator[str, None]:
        # Yields text chunks for SSE streaming
```

**Providers:**
- `claude` — Anthropic API, model `claude-sonnet-4-6` (default)
- `openai` — OpenAI API, model `gpt-4o-mini`
- `greenpt`- https://docs.greenpt.ai/api/models model `gemma-3-27b-it` also api is openAI compatible at https://api.greenpt.ai/v1/models

- `local` — OpenAI-compatible endpoint at Tailscale URL, configurable model

Selection via `LLM_PROVIDER` env var. All support streaming.

## System Prompt

```
You are Dan Bennett's portfolio assistant. You help visitors learn about Dan's
projects, technical skills, and professional background.

Rules:
- Answer based ONLY on the provided context. If the context doesn't contain
  the answer, say so honestly.
- Speak in third person about Dan ("Dan built...", "His approach was...")
- When discussing a project, mention which case study page has more detail
  (link format: /projects/{slug})
- Be honest about what Dan built vs what teams/contractors built
- Keep responses concise — 2-3 paragraphs max unless asked for more detail
- Don't hallucinate projects, technologies, or capabilities not in the context
- If asked about availability, location, or contact: Dan is based in Haarlem,
  Netherlands (near Amsterdam), open to remote/hybrid roles, reachable at
  dantana@gmail.com or linkedin.com/in/dbenn8
```

## Deployment

### Single Appliku App (multi-stage Docker build)

**`Dockerfile`:**
```dockerfile
# Stage 1: Build Astro portfolio site
FROM node:20-slim AS frontend
WORKDIR /app/portfolio
COPY portfolio/ .
RUN npm ci && npm run build

# Stage 2: Python API + static portfolio
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY ingest.py .
COPY --from=frontend /app/portfolio/dist ./static
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`appliku.yml`:**
```yaml
build_settings:
  build_image: dockerfile
  dockerfile_path: "./Dockerfile"
  container_port: 8000
```

**Environment variables:**
- `WEAVIATE_URL` — Weaviate Cloud cluster URL
- `WEAVIATE_API_KEY` — Weaviate Cloud API key
- `ANTHROPIC_API_KEY` — Claude API key
- `OPENAI_API_KEY` — OpenAI API key (for embeddings + fallback LLM)
- `LLM_PROVIDER` — "claude" (default), "openai", or "local"
- `LOCAL_LLM_URL` — Tailscale URL for local LLM (optional)
- `INGEST_API_KEY` — API key for the /api/ingest endpoint

### Weaviate Cloud

Free tier (sandbox cluster). Collection schema:

```json
{
  "class": "Portfolio",
  "properties": [
    { "name": "text", "dataType": ["text"] },
    { "name": "source", "dataType": ["text"] },
    { "name": "project", "dataType": ["text"] },
    { "name": "section", "dataType": ["text"] },
    { "name": "content_type", "dataType": ["text"] }
  ]
}
```

### Widget Integration

The widget JS is bundled into the Astro build as a static asset. Add to `Base.astro` layout:

```html
<script src="/widget.js" defer></script>
```

Same origin — no CORS, no external dependency.

## Project Structure

```
portfolio-chat/
├── app/
│   ├── main.py              # FastAPI app, static file mount, API routes
│   ├── chat.py              # /api/chat endpoint, RAG retrieval, streaming
│   ├── llm_service.py       # Configurable LLM abstraction
│   ├── weaviate_client.py   # Weaviate connection and search
│   └── config.py            # Environment variable management
├── portfolio/               # Astro portfolio source (git submodule or copy)
│   ├── src/
│   ├── package.json
│   └── astro.config.mjs
├── ingest.py                # CLI ingestion script
├── static/                  # Built at Docker build time (Astro output + widget)
├── requirements.txt
├── Dockerfile               # Multi-stage: Node (Astro build) → Python (FastAPI)
├── appliku.yml
├── .env.example
└── docs/
    └── 2026-05-20-portfolio-chatbot-design.md  # This file
```

## Success Criteria

1. Visitor can ask "What projects has Dan built with n8n?" and get an accurate, sourced answer
2. Responses stream in real-time (first token < 2 seconds)
3. Widget loads without affecting portfolio site performance (async, deferred)
4. Ingestion covers all 16 AI Builder Summaries + 11 portfolio pages
5. Deployed and accessible within 1 day of implementation start
6. The chatbot itself becomes a portfolio project — meta-flex for n8n application

## Out of Scope (for v1)

- Conversation persistence across page reloads (session memory only)
- User analytics / chat logging
- Admin UI for managing knowledge base
- Multi-language support
- Rate limiting (add if abuse detected)
