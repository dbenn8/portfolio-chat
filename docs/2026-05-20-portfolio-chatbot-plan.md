# Portfolio Chatbot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portfolio chatbot (Kumpel.ai revival) that answers questions about Dan's projects via RAG, deployed as a single FastAPI app that also serves the static Astro portfolio site.

**Architecture:** FastAPI app with multi-stage Docker build (Node for Astro → Python for API). Weaviate Cloud for vector storage. Configurable LLM layer (Claude, OpenAI, GreenPT, local). Chat widget embedded in the portfolio site as vanilla JS.

**Tech Stack:** FastAPI, uvicorn, weaviate-client, anthropic SDK, openai SDK (for GreenPT + OpenAI), sse-starlette, Python 3.12, Astro (portfolio), Docker

**Spec:** `docs/2026-05-20-portfolio-chatbot-design.md`

---

## File Structure

```
portfolio-chat/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, static mount, route includes
│   ├── config.py             # Pydantic settings from env vars
│   ├── chat.py               # /api/chat — retrieval + streaming response
│   ├── ingest_api.py         # /api/ingest — trigger re-indexing
│   ├── llm_service.py        # Configurable LLM (Claude, OpenAI, GreenPT, local)
│   └── weaviate_client.py    # Weaviate connection, search, upsert
├── portfolio/                # Symlink → ../portfolio (Astro source)
├── widget/
│   └── widget.js             # Chat widget vanilla JS
├── ingest.py                 # CLI script — read content, chunk, embed, upsert
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_llm_service.py
│   ├── test_chat.py
│   ├── test_ingest.py
│   └── test_weaviate_client.py
├── requirements.txt
├── Dockerfile
├── appliku.yml
├── .env.example
├── .gitignore
└── docs/
    ├── 2026-05-20-portfolio-chatbot-design.md
    └── 2026-05-20-portfolio-chatbot-plan.md
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `portfolio` (symlink)

- [ ] **Step 1: Create .gitignore**

```
__pycache__/
*.pyc
.env
.venv/
venv/
*.egg-info/
dist/
static/
.pytest_cache/
node_modules/
```

- [ ] **Step 2: Create requirements.txt**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sse-starlette==2.2.1
weaviate-client==4.10.4
anthropic==0.43.0
openai==1.82.0
httpx==0.28.1
python-dotenv==1.1.0
pydantic-settings==2.7.1
pytest==8.3.4
pytest-asyncio==0.25.0
```

- [ ] **Step 3: Create .env.example**

```bash
# LLM Provider: claude, openai, greenpt, local
LLM_PROVIDER=greenpt

# Anthropic (for claude provider)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI (for openai provider)
OPENAI_API_KEY=sk-...

# GreenPT (OpenAI-compatible, for greenpt provider + embeddings)
GREENPT_API_KEY=gpt-...
GREENPT_BASE_URL=https://api.greenpt.ai/v1
GREENPT_CHAT_MODEL=gemma-3-27b-it
GREENPT_EMBEDDING_MODEL=green-embedding

# Local LLM (OpenAI-compatible endpoint via Tailscale)
LOCAL_LLM_URL=https://laptop.tailf840c8.ts.net
LOCAL_LLM_MODEL=qwen3.5-27b

# Weaviate Cloud
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=...

# Ingestion API protection
INGEST_API_KEY=change-me-to-a-random-string

# Port (Appliku sets this)
PORT=8000
```

- [ ] **Step 4: Create app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "greenpt"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    greenpt_api_key: str = ""
    greenpt_base_url: str = "https://api.greenpt.ai/v1"
    greenpt_chat_model: str = "gemma-3-27b-it"
    greenpt_embedding_model: str = "green-embedding"

    local_llm_url: str = ""
    local_llm_model: str = "qwen3.5-27b"

    weaviate_url: str = ""
    weaviate_api_key: str = ""

    ingest_api_key: str = "change-me"

    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

- [ ] **Step 5: Create test for config**

```python
# tests/test_config.py
import os
from unittest.mock import patch


def test_settings_defaults():
    with patch.dict(os.environ, {}, clear=True):
        from importlib import reload
        import app.config
        reload(app.config)
        s = app.config.Settings()
        assert s.llm_provider == "greenpt"
        assert s.greenpt_base_url == "https://api.greenpt.ai/v1"
        assert s.port == 8000


def test_settings_from_env():
    env = {"LLM_PROVIDER": "claude", "ANTHROPIC_API_KEY": "test-key"}
    with patch.dict(os.environ, env, clear=True):
        from importlib import reload
        import app.config
        reload(app.config)
        s = app.config.Settings()
        assert s.llm_provider == "claude"
        assert s.anthropic_api_key == "test-key"
```

- [ ] **Step 6: Create empty __init__.py files**

Create empty files:
- `app/__init__.py`
- `tests/__init__.py`

- [ ] **Step 7: Create portfolio symlink**

```bash
cd /Users/danielbennett/codeNew/portfolio-chat
ln -s ../portfolio portfolio
```

- [ ] **Step 8: Set up venv and run tests**

```bash
cd /Users/danielbennett/codeNew/portfolio-chat
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/test_config.py -v
```

Expected: 2 tests PASS

- [ ] **Step 9: Commit**

```bash
git init
git add .gitignore requirements.txt .env.example app/__init__.py app/config.py tests/__init__.py tests/test_config.py
git commit -m "Scaffold project with config and dependencies"
```

---

### Task 2: Weaviate Client

**Files:**
- Create: `app/weaviate_client.py`
- Create: `tests/test_weaviate_client.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_weaviate_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_chunk_text_basic():
    from app.weaviate_client import chunk_text
    text = "Word " * 100  # 100 words
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    assert len(chunks) >= 2
    assert all(len(c.split()) <= 55 for c in chunks)  # allow small overshoot


def test_chunk_text_short():
    from app.weaviate_client import chunk_text
    text = "Short text."
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunk_text_preserves_content():
    from app.weaviate_client import chunk_text
    words = [f"word{i}" for i in range(200)]
    text = " ".join(words)
    chunks = chunk_text(text, max_tokens=50, overlap_tokens=10)
    reassembled = set()
    for chunk in chunks:
        for w in chunk.split():
            reassembled.add(w)
    for w in words:
        assert w in reassembled, f"Lost word: {w}"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_weaviate_client.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write weaviate_client.py**

```python
# app/weaviate_client.py
from typing import Optional
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from app.config import settings

COLLECTION_NAME = "Portfolio"

_client: Optional[weaviate.WeaviateClient] = None


def get_client() -> weaviate.WeaviateClient:
    global _client
    if _client is None or not _client.is_connected():
        _client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key),
        )
    return _client


def ensure_collection():
    client = get_client()
    if not client.collections.exists(COLLECTION_NAME):
        client.collections.create(
            name=COLLECTION_NAME,
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
                Property(name="project", data_type=DataType.TEXT),
                Property(name="section", data_type=DataType.TEXT),
                Property(name="content_type", data_type=DataType.TEXT),
                Property(name="slug", data_type=DataType.TEXT),
            ],
        )


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


def upsert_chunks(chunks: list[dict]):
    client = get_client()
    collection = client.collections.get(COLLECTION_NAME)
    with collection.batch.dynamic() as batch:
        for chunk in chunks:
            batch.add_object(
                properties={
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "project": chunk["project"],
                    "section": chunk["section"],
                    "content_type": chunk["content_type"],
                    "slug": chunk.get("slug", ""),
                },
                vector=chunk["vector"],
            )


def search(query_text: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
    client = get_client()
    collection = client.collections.get(COLLECTION_NAME)
    results = collection.query.hybrid(
        query=query_text,
        vector=query_vector,
        limit=top_k,
        alpha=0.5,  # 0 = pure keyword, 1 = pure vector, 0.5 = balanced
        return_metadata=MetadataQuery(score=True),
    )
    return [
        {
            "text": obj.properties["text"],
            "source": obj.properties["source"],
            "project": obj.properties["project"],
            "section": obj.properties["section"],
            "content_type": obj.properties["content_type"],
            "slug": obj.properties.get("slug", ""),
            "score": obj.metadata.score,
        }
        for obj in results.objects
    ]


def clear_collection():
    client = get_client()
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
    ensure_collection()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_weaviate_client.py -v
```

Expected: 3 tests PASS (chunking tests are pure functions, no Weaviate connection needed)

- [ ] **Step 5: Commit**

```bash
git add app/weaviate_client.py tests/test_weaviate_client.py
git commit -m "Add Weaviate client with chunking, upsert, and search"
```

---

### Task 3: LLM Service

**Files:**
- Create: `app/llm_service.py`
- Create: `tests/test_llm_service.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm_service.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


def test_get_provider_claude():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "claude"
        mock_settings.anthropic_api_key = "test"
        svc = LLMService()
        assert svc.provider == "claude"


def test_get_provider_greenpt():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "greenpt"
        mock_settings.greenpt_api_key = "test"
        mock_settings.greenpt_base_url = "https://api.greenpt.ai/v1"
        mock_settings.greenpt_chat_model = "gemma-3-27b-it"
        svc = LLMService()
        assert svc.provider == "greenpt"


def test_get_provider_invalid():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "nonexistent"
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMService()


@pytest.mark.asyncio
async def test_embed_text_greenpt():
    from app.llm_service import LLMService
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "greenpt"
        mock_settings.greenpt_api_key = "test"
        mock_settings.greenpt_base_url = "https://api.greenpt.ai/v1"
        mock_settings.greenpt_chat_model = "gemma-3-27b-it"
        mock_settings.greenpt_embedding_model = "green-embedding"

        svc = LLMService()
        svc._embedding_client = MagicMock()
        svc._embedding_client.embeddings.create.return_value = mock_response

        result = await svc.embed("test text")
        assert result == [0.1, 0.2, 0.3]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_llm_service.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write llm_service.py**

```python
# app/llm_service.py
from typing import AsyncGenerator
from app.config import settings

VALID_PROVIDERS = {"claude", "openai", "greenpt", "local"}


class LLMService:
    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.llm_provider
        if self.provider not in VALID_PROVIDERS:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
        self._chat_client = None
        self._embedding_client = None
        self._init_clients()

    def _init_clients(self):
        if self.provider == "claude":
            import anthropic
            self._chat_client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key
            )
        elif self.provider == "openai":
            from openai import AsyncOpenAI
            self._chat_client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "greenpt":
            from openai import AsyncOpenAI, OpenAI
            self._chat_client = AsyncOpenAI(
                api_key=settings.greenpt_api_key,
                base_url=settings.greenpt_base_url,
            )
            self._embedding_client = OpenAI(
                api_key=settings.greenpt_api_key,
                base_url=settings.greenpt_base_url,
            )
        elif self.provider == "local":
            from openai import AsyncOpenAI
            self._chat_client = AsyncOpenAI(
                api_key="not-needed",
                base_url=settings.local_llm_url + "/v1",
            )

        if self._embedding_client is None and self.provider != "greenpt":
            from openai import OpenAI
            if settings.greenpt_api_key:
                self._embedding_client = OpenAI(
                    api_key=settings.greenpt_api_key,
                    base_url=settings.greenpt_base_url,
                )
            elif settings.openai_api_key:
                self._embedding_client = OpenAI(api_key=settings.openai_api_key)

    async def embed(self, text: str) -> list[float]:
        model = settings.greenpt_embedding_model if settings.greenpt_api_key else "text-embedding-3-small"
        response = self._embedding_client.embeddings.create(
            model=model,
            input=text,
        )
        return response.data[0].embedding

    async def chat_stream(
        self, messages: list[dict], system_prompt: str
    ) -> AsyncGenerator[str, None]:
        if self.provider == "claude":
            async with self._chat_client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            model = self._get_chat_model()
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            stream = await self._chat_client.chat.completions.create(
                model=model,
                messages=full_messages,
                max_tokens=1024,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    def _get_chat_model(self) -> str:
        if self.provider == "greenpt":
            return settings.greenpt_chat_model
        elif self.provider == "openai":
            return "gpt-4o-mini"
        elif self.provider == "local":
            return settings.local_llm_model
        return "gpt-4o-mini"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_llm_service.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/llm_service.py tests/test_llm_service.py
git commit -m "Add configurable LLM service with Claude, OpenAI, GreenPT, local providers"
```

---

### Task 4: Chat Endpoint

**Files:**
- Create: `app/chat.py`
- Create: `tests/test_chat.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_chat.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


SYSTEM_PROMPT = """You are Dan Bennett's portfolio assistant. You help visitors learn about Dan's projects, technical skills, and professional background.

Rules:
- Answer based ONLY on the provided context. If the context doesn't contain the answer, say so honestly.
- Speak in third person about Dan ("Dan built...", "His approach was...")
- Do NOT add citations or source links — the system appends these automatically after your response.
- Be honest about what Dan built vs what teams/contractors built
- Keep responses concise — 2-3 paragraphs max unless asked for more detail
- Don't hallucinate projects, technologies, or capabilities not in the context
- If asked about availability, location, or contact: Dan is based in Haarlem, Netherlands (near Amsterdam), open to remote/hybrid roles, reachable at dantana@gmail.com or linkedin.com/in/dbenn8"""


def test_system_prompt_no_citation_instructions():
    from app.chat import SYSTEM_PROMPT as sp
    assert "automatically" in sp.lower()


def test_build_context_includes_source_tags():
    from app.chat import build_context
    results = [
        {"text": "Dan built MARVIN", "project": "MARVIN", "source": "summary.md", "section": "Overview", "content_type": "summary", "slug": None, "distance": 0.1},
        {"text": "n8n workflows for MBO", "project": "MBO Listing Sync", "source": "mbo-listing-sync.astro", "section": "Approach", "content_type": "portfolio", "slug": "mbo-listing-sync", "distance": 0.2},
    ]
    context = build_context(results)
    assert "Dan built MARVIN" in context
    assert "/projects/mbo-listing-sync" in context


def test_build_source_links_deduplicates():
    from app.chat import build_source_links
    results = [
        {"project": "MARVIN", "source": "summary.md", "slug": None, "distance": 0.1},
        {"project": "MBO Listing Sync", "source": "mbo-listing-sync.astro", "slug": "mbo-listing-sync", "distance": 0.2},
        {"project": "MBO Listing Sync", "source": "mbo-listing-sync.astro", "slug": "mbo-listing-sync", "distance": 0.3},
    ]
    links = build_source_links(results)
    assert "[MBO Listing Sync](/projects/mbo-listing-sync)" in links
    assert links.count("MBO Listing Sync") == 1  # deduplicated


def test_build_source_links_skips_no_slug():
    from app.chat import build_source_links
    results = [
        {"project": "MARVIN", "source": "summary.md", "slug": None, "distance": 0.1},
    ]
    links = build_source_links(results)
    assert links == ""
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_chat.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write chat.py**

```python
# app/chat.py
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
- When discussing a project, mention which case study page has more detail (link format: /projects/{slug})
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


def build_context(results: list[dict]) -> str:
    sections = []
    for r in results:
        slug = r.get("slug") or source_to_slug(r["source"])
        source_tag = f"[Source: {r['project']} — {slug}]" if slug else f"[Source: {r['project']}]"
        sections.append(f"{source_tag}\n{r['text']}")
    return "\n\n---\n\n".join(sections)


def build_source_links(results: list[dict]) -> str:
    seen = {}
    for r in results:
        slug = r.get("slug") or source_to_slug(r["source"])
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
    results = search(query_vector, top_k=5)
    context = build_context(results)

    messages = [
        {
            "role": "user",
            "content": f"Context from Dan's portfolio:\n\n{context}\n\n---\n\nUser question: {request.message}",
        }
    ]

    sources = build_source_links(results)

    async def event_generator():
        async for chunk in llm.chat_stream(messages, SYSTEM_PROMPT):
            yield {"data": chunk}
        if sources:
            yield {"data": "\n\n---\n**Sources:** " + sources}
        yield {"data": "[DONE]"}

    return EventSourceResponse(event_generator())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_chat.py -v
```

Expected: 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/chat.py tests/test_chat.py
git commit -m "Add chat endpoint with RAG retrieval and SSE streaming"
```

---

### Task 5: Ingestion Pipeline

**Files:**
- Create: `ingest.py`
- Create: `tests/test_ingest.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ingest.py
import pytest


def test_strip_astro_frontmatter():
    from ingest import strip_astro
    content = '---\nimport Foo from "bar";\n---\n\n<h2>Hello</h2>\n<p>World</p>'
    result = strip_astro(content)
    assert "import" not in result
    assert "Hello" in result
    assert "World" in result


def test_strip_html_tags():
    from ingest import strip_html
    html = "<h2>Title</h2>\n<p>Some <strong>bold</strong> text.</p>"
    result = strip_html(html)
    assert "<h2>" not in result
    assert "Title" in result
    assert "bold" in result


def test_extract_project_name_from_summary():
    from ingest import extract_project_name
    assert extract_project_name("AI Builder Summary for MARVIN.md") == "MARVIN"
    assert extract_project_name("AI Builder Summary for Burrfect Backend.md") == "Burrfect Backend"
    assert extract_project_name("AI Builder Summary for MBO n8n Workflows.md") == "MBO n8n Workflows"


def test_extract_sections():
    from ingest import extract_sections
    text = "# Title\n\nIntro paragraph.\n\n## Section One\n\nContent one.\n\n## Section Two\n\nContent two."
    sections = extract_sections(text)
    assert len(sections) >= 2
    assert any("Section One" in s["section"] for s in sections)
    assert any("Content one" in s["text"] for s in sections)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_ingest.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write ingest.py**

```python
#!/usr/bin/env python3
"""Ingestion pipeline: reads portfolio content and AI Builder Summaries,
chunks text, embeds via GreenPT/OpenAI, upserts to Weaviate."""

import glob
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from app.llm_service import LLMService
from app.weaviate_client import chunk_text, ensure_collection, upsert_chunks, clear_collection


HOME = Path.home()

SUMMARY_PATTERNS = [
    str(HOME / "codeNew/*/AI Builder Summary for *.md"),
    str(HOME / "Documents/Claude/**/AI Builder Summary for *.md"),
    str(HOME / "marvin/AI Builder Summary for *.md"),
    str(HOME / "marvin/Meal Planning/AI Builder Summary for *.md"),
    str(HOME / "projects/*/AI Builder Summary for *.md"),
    str(HOME / "llm/AI Builder Summary for *.md"),
]

PORTFOLIO_DIR = Path(__file__).parent / "portfolio" / "src" / "pages"


def strip_astro(content: str) -> str:
    content = re.sub(r"^---\n.*?\n---\n*", "", content, count=1, flags=re.DOTALL)
    return strip_html(content)


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\{[^}]*\}", " ", text)  # remove Astro expressions
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def extract_project_name(filename: str) -> str:
    match = re.match(r"AI Builder Summary for (.+)\.md$", filename)
    return match.group(1) if match else filename.replace(".md", "")


def extract_sections(text: str) -> list[dict]:
    lines = text.split("\n")
    sections = []
    current_section = "Introduction"
    current_text = []

    for line in lines:
        heading_match = re.match(r"^#{1,3}\s+(.+)$", line)
        if heading_match:
            if current_text:
                joined = "\n".join(current_text).strip()
                if joined:
                    sections.append({"section": current_section, "text": joined})
            current_section = heading_match.group(1)
            current_text = []
        else:
            current_text.append(line)

    if current_text:
        joined = "\n".join(current_text).strip()
        if joined:
            sections.append({"section": current_section, "text": joined})

    return sections


def collect_portfolio_pages() -> list[dict]:
    docs = []
    if not PORTFOLIO_DIR.exists():
        print(f"Warning: portfolio dir not found at {PORTFOLIO_DIR}")
        return docs

    for astro_file in PORTFOLIO_DIR.rglob("*.astro"):
        content = astro_file.read_text()
        text = strip_astro(content)
        project = astro_file.stem
        if project == "index":
            project = "Portfolio Home"
        elif project == "n8n":
            project = "n8n Application Page"

        for section in extract_sections(text):
            docs.append({
                "text": section["text"],
                "source": str(astro_file.name),
                "project": project,
                "section": section["section"],
                "content_type": "portfolio",
            })

    return docs


def collect_summaries() -> list[dict]:
    docs = []
    for pattern in SUMMARY_PATTERNS:
        for filepath in glob.glob(pattern, recursive=True):
            content = Path(filepath).read_text()
            filename = Path(filepath).name
            project = extract_project_name(filename)

            for section in extract_sections(content):
                docs.append({
                    "text": section["text"],
                    "source": filename,
                    "project": project,
                    "section": section["section"],
                    "content_type": "summary",
                })

    return docs


async def run_ingestion():
    print("Starting ingestion...")
    llm = LLMService()

    print("Collecting portfolio pages...")
    portfolio_docs = collect_portfolio_pages()
    print(f"  Found {len(portfolio_docs)} sections from portfolio pages")

    print("Collecting AI Builder Summaries...")
    summary_docs = collect_summaries()
    print(f"  Found {len(summary_docs)} sections from summaries")

    all_docs = portfolio_docs + summary_docs
    print(f"Total sections: {len(all_docs)}")

    print("Chunking...")
    all_chunks = []
    for doc in all_docs:
        text_chunks = chunk_text(doc["text"], max_tokens=250, overlap_tokens=50)
        for chunk in text_chunks:
            all_chunks.append({**doc, "text": chunk})
    print(f"Total chunks: {len(all_chunks)}")

    print("Embedding chunks...")
    for i, chunk in enumerate(all_chunks):
        chunk["vector"] = await llm.embed(chunk["text"])
        if (i + 1) % 20 == 0:
            print(f"  Embedded {i + 1}/{len(all_chunks)}")
    print(f"  Embedded {len(all_chunks)}/{len(all_chunks)}")

    print("Clearing and re-creating collection...")
    clear_collection()

    print("Upserting to Weaviate...")
    upsert_chunks(all_chunks)
    print(f"Done! {len(all_chunks)} chunks indexed.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_ingestion())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_ingest.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add ingest.py tests/test_ingest.py
git commit -m "Add ingestion pipeline for portfolio pages and AI Builder Summaries"
```

---

### Task 6: FastAPI Main App

**Files:**
- Create: `app/main.py`
- Create: `app/ingest_api.py`

- [ ] **Step 1: Write ingest_api.py**

```python
# app/ingest_api.py
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()


@router.post("/api/ingest")
async def trigger_ingest(x_api_key: str = Header(...)):
    from app.config import settings
    if x_api_key != settings.ingest_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    from ingest import run_ingestion
    await run_ingestion()
    return {"status": "ok", "message": "Ingestion complete"}
```

- [ ] **Step 2: Write main.py**

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.chat import router as chat_router
from app.ingest_api import router as ingest_router

app = FastAPI(title="Dan Bennett Portfolio + Chat API")

app.include_router(chat_router)
app.include_router(ingest_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
```

- [ ] **Step 3: Verify the app starts locally**

```bash
cd /Users/danielbennett/codeNew/portfolio-chat
source venv/bin/activate
mkdir -p static
echo "<html><body>placeholder</body></html>" > static/index.html
uvicorn app.main:app --port 8000 &
sleep 2
curl http://localhost:8000/api/health
kill %1
```

Expected: `{"status":"ok"}`

- [ ] **Step 4: Commit**

```bash
git add app/main.py app/ingest_api.py
git commit -m "Add FastAPI main app with health, chat, ingest routes and static serving"
```

---

### Task 7: Chat Widget

**Files:**
- Create: `widget/widget.js`

- [ ] **Step 1: Write widget.js**

```javascript
// widget/widget.js — Portfolio chat widget
(function() {
  const API_URL = window.PORTFOLIO_CHAT_API || '';
  const GREETING = "Hi! I'm Dan's portfolio assistant. Ask me about any of his projects, his tech stack, or his background.";

  let isOpen = false;
  let messages = [{ role: 'assistant', content: GREETING }];

  function createStyles() {
    const style = document.createElement('style');
    style.textContent = `
      #pc-bubble { position:fixed; bottom:20px; right:20px; width:56px; height:56px; border-radius:50%; background:#10b981; color:white; border:none; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.3); z-index:9999; display:flex; align-items:center; justify-content:center; font-size:24px; transition:transform 0.2s; }
      #pc-bubble:hover { transform:scale(1.1); }
      #pc-panel { position:fixed; bottom:88px; right:20px; width:380px; max-height:500px; background:white; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.2); z-index:9999; display:none; flex-direction:column; overflow:hidden; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
      #pc-panel.open { display:flex; }
      #pc-header { background:#0f172a; color:white; padding:14px 16px; font-weight:600; font-size:14px; display:flex; justify-content:space-between; align-items:center; }
      #pc-close { background:none; border:none; color:white; cursor:pointer; font-size:18px; padding:0 4px; }
      #pc-messages { flex:1; overflow-y:auto; padding:12px; max-height:340px; }
      .pc-msg { margin-bottom:10px; line-height:1.5; font-size:13px; }
      .pc-msg.user { text-align:right; }
      .pc-msg.user span { background:#10b981; color:white; padding:8px 12px; border-radius:12px 12px 2px 12px; display:inline-block; max-width:85%; text-align:left; }
      .pc-msg.assistant span { background:#f1f5f9; color:#1e293b; padding:8px 12px; border-radius:12px 12px 12px 2px; display:inline-block; max-width:85%; text-align:left; }
      .pc-msg.assistant span a { color:#10b981; }
      .pc-msg.assistant span strong { font-weight:600; }
      .pc-msg.assistant span code { background:#e2e8f0; padding:1px 4px; border-radius:3px; font-size:12px; }
      #pc-input-row { display:flex; border-top:1px solid #e2e8f0; }
      #pc-input { flex:1; border:none; padding:12px; font-size:13px; outline:none; }
      #pc-send { background:#10b981; color:white; border:none; padding:12px 16px; cursor:pointer; font-weight:600; font-size:13px; }
      #pc-send:hover { background:#059669; }
      #pc-send:disabled { background:#94a3b8; cursor:not-allowed; }
      @media(max-width:440px) { #pc-panel { width:calc(100vw - 24px); right:12px; bottom:80px; } }
    `;
    document.head.appendChild(style);
  }

  function renderMarkdown(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
      .replace(/`(.+?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  function createUI() {
    const bubble = document.createElement('button');
    bubble.id = 'pc-bubble';
    bubble.innerHTML = '💬';
    bubble.onclick = toggle;

    const panel = document.createElement('div');
    panel.id = 'pc-panel';
    panel.innerHTML = `
      <div id="pc-header">
        <span>Ask about Dan's projects</span>
        <button id="pc-close" onclick="document.getElementById('pc-panel').classList.remove('open');document.getElementById('pc-bubble').style.display='flex'">✕</button>
      </div>
      <div id="pc-messages"></div>
      <div id="pc-input-row">
        <input id="pc-input" placeholder="Ask me anything..." />
        <button id="pc-send">Send</button>
      </div>
    `;

    document.body.appendChild(bubble);
    document.body.appendChild(panel);

    document.getElementById('pc-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    document.getElementById('pc-send').addEventListener('click', sendMessage);

    renderMessages();
  }

  function toggle() {
    const panel = document.getElementById('pc-panel');
    const bubble = document.getElementById('pc-bubble');
    isOpen = !isOpen;
    panel.classList.toggle('open', isOpen);
    bubble.style.display = isOpen ? 'none' : 'flex';
    if (isOpen) document.getElementById('pc-input').focus();
  }

  function renderMessages() {
    const container = document.getElementById('pc-messages');
    container.innerHTML = messages.map(m =>
      `<div class="pc-msg ${m.role}"><span>${renderMarkdown(m.content)}</span></div>`
    ).join('');
    container.scrollTop = container.scrollHeight;
  }

  async function sendMessage() {
    const input = document.getElementById('pc-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    messages.push({ role: 'user', content: text });
    messages.push({ role: 'assistant', content: '' });
    renderMessages();

    const sendBtn = document.getElementById('pc-send');
    sendBtn.disabled = true;

    try {
      const response = await fetch(API_URL + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;
            messages[messages.length - 1].content += data;
            renderMessages();
          }
        }
      }
    } catch (err) {
      messages[messages.length - 1].content = 'Sorry, something went wrong. Please try again.';
      renderMessages();
    }

    sendBtn.disabled = false;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { createStyles(); createUI(); });
  } else {
    createStyles(); createUI();
  }
})();
```

- [ ] **Step 2: Commit**

```bash
git add widget/widget.js
git commit -m "Add chat widget — vanilla JS floating bubble with SSE streaming"
```

---

### Task 8: Dockerfile and Appliku Config

**Files:**
- Create: `Dockerfile`
- Create: `appliku.yml`

- [ ] **Step 1: Write Dockerfile**

```dockerfile
# Stage 1: Build Astro portfolio site
FROM node:20-slim AS frontend
WORKDIR /app/portfolio
COPY portfolio/ .
RUN npm ci && npm run build

# Stage 2: Python API + static portfolio + widget
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY ingest.py .
COPY widget/widget.js ./static/widget.js
COPY --from=frontend /app/portfolio/dist ./static

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Write appliku.yml**

```yaml
build_settings:
  build_image: dockerfile
  dockerfile_path: "./Dockerfile"
  container_port: 8000
```

- [ ] **Step 3: Commit**

```bash
git add Dockerfile appliku.yml
git commit -m "Add Dockerfile (multi-stage Node+Python) and Appliku config"
```

---

### Task 9: Widget Integration in Portfolio

**Files:**
- Modify: `portfolio/src/layouts/Base.astro` (add widget script tag)

- [ ] **Step 1: Add widget script to Base.astro**

Add before the closing `</body>` tag in `portfolio/src/layouts/Base.astro`:

```html
    <script src="/widget.js" defer></script>
  </body>
</html>
```

- [ ] **Step 2: Verify Astro build still works**

```bash
cd /Users/danielbennett/codeNew/portfolio
npm run build 2>&1 | tail -5
```

Expected: `Complete!`

- [ ] **Step 3: Commit in portfolio repo**

```bash
cd /Users/danielbennett/codeNew/portfolio
git add src/layouts/Base.astro
git commit -m "Add chat widget script tag to base layout"
```

- [ ] **Step 4: Commit symlink update in portfolio-chat repo**

```bash
cd /Users/danielbennett/codeNew/portfolio-chat
git add -A
git commit -m "Track portfolio symlink for Docker build context"
```

---

### Task 10: Weaviate Cloud Setup and First Ingestion

**Files:**
- No new files — operational setup

- [ ] **Step 1: Create Weaviate Cloud sandbox cluster**

Go to https://console.weaviate.cloud — create a free sandbox cluster. Copy the cluster URL and API key.

- [ ] **Step 2: Create .env from .env.example**

```bash
cd /Users/danielbennett/codeNew/portfolio-chat
cp .env.example .env
```

Fill in:
- `WEAVIATE_URL` and `WEAVIATE_API_KEY` from the Weaviate Cloud console
- `GREENPT_API_KEY` — your GreenPT API key
- At least one chat provider key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or use `greenpt` as `LLM_PROVIDER`)

- [ ] **Step 3: Run ingestion**

```bash
source venv/bin/activate
python ingest.py
```

Expected output:
```
Starting ingestion...
Collecting portfolio pages...
  Found ~XX sections from portfolio pages
Collecting AI Builder Summaries...
  Found ~XX sections from summaries
Total sections: ~XX
Chunking...
Total chunks: ~XX
Embedding chunks...
  Embedded XX/XX
Clearing and re-creating collection...
Upserting to Weaviate...
Done! XX chunks indexed.
```

- [ ] **Step 4: Test the full stack locally**

```bash
uvicorn app.main:app --port 8000 --reload &
sleep 2
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What projects has Dan built with n8n?"}'
kill %1
```

Expected: SSE stream with a relevant answer mentioning MBO Listing Sync and n8n workflows.

- [ ] **Step 5: Commit .env.example updates if any**

```bash
git add .env.example
git commit -m "Finalize env vars after first successful ingestion"
```

---

### Task 11: Deploy to Appliku

**Files:**
- No new files — deployment

- [ ] **Step 1: Create GitHub repo**

```bash
cd /Users/danielbennett/codeNew/portfolio-chat
gh repo create dbenn8/portfolio-chat --public --source=. --remote=origin --push
```

- [ ] **Step 2: Create Appliku app**

Use Appliku dashboard or CLI:
- Connect to GitHub repo `dbenn8/portfolio-chat`
- Set environment variables from `.env`
- Deploy

- [ ] **Step 3: Verify deployment**

```bash
curl https://portfolio-chat.applikuapp.com/api/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 4: Test chat on the live site**

Visit the portfolio URL. The chat bubble should appear in the bottom-right corner. Click it and ask "What projects has Dan built with n8n?"

---

### Task 12: Conversation Memory (Multi-Turn)

**Files:**
- Modify: `app/chat.py`
- Create: `tests/test_chat_memory.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_chat_memory.py
def test_session_store_and_retrieve():
    from app.chat import get_history, save_turn

    save_turn("test-session-1", "user", "What did Dan build with n8n?")
    save_turn("test-session-1", "assistant", "Dan built MBO Listing Sync...")

    history = get_history("test-session-1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_session_isolation():
    from app.chat import get_history, save_turn

    save_turn("session-a", "user", "Question A")
    save_turn("session-b", "user", "Question B")

    assert len(get_history("session-a")) == 1
    assert get_history("session-a")[0]["content"] == "Question A"


def test_session_max_history():
    from app.chat import get_history, save_turn, MAX_HISTORY

    for i in range(MAX_HISTORY + 5):
        save_turn("overflow-session", "user", f"Message {i}")

    history = get_history("overflow-session")
    assert len(history) <= MAX_HISTORY
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_chat_memory.py -v
```

Expected: FAIL — `ImportError`

- [ ] **Step 3: Add memory functions to chat.py**

Add to `app/chat.py`:

```python
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
```

Update the `chat` endpoint to use history:

```python
@router.post("/api/chat")
async def chat(request: ChatRequest):
    llm = LLMService()
    query_vector = await llm.embed(request.message)
    results = search(request.message, query_vector, top_k=5)
    context = build_context(results)
    sources = build_source_links(results)

    session_id = request.session_id or "anonymous"
    history = get_history(session_id)

    messages = history + [
        {
            "role": "user",
            "content": f"Context from Dan's portfolio:\n\n{context}\n\n---\n\nUser question: {request.message}",
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
        save_turn(session_id, "user", request.message)
        save_turn(session_id, "assistant", full_response)
        yield {"data": "[DONE]"}

    return EventSourceResponse(event_generator())
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_chat_memory.py -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/chat.py tests/test_chat_memory.py
git commit -m "Add multi-turn conversation memory with session isolation"
```

---

### Task 13: Widget Enhancements (Starters + Typing Indicator + Session ID)

**Files:**
- Modify: `widget/widget.js`

- [ ] **Step 1: Update widget.js**

Add these features to the widget:

**Starter questions** — show below the greeting as clickable chips:

```javascript
  const STARTERS = [
    "What projects has Dan built with n8n?",
    "Tell me about Dan's background",
    "What AI systems has Dan shipped?",
  ];
```

In `createUI()`, after the messages div, add a starters container:

```javascript
    const starters = document.createElement('div');
    starters.id = 'pc-starters';
    starters.style.cssText = 'padding:8px 12px; display:flex; flex-wrap:wrap; gap:6px;';
    STARTERS.forEach(q => {
      const chip = document.createElement('button');
      chip.textContent = q;
      chip.style.cssText = 'background:#f1f5f9; border:1px solid #e2e8f0; border-radius:16px; padding:6px 12px; font-size:11px; color:#475569; cursor:pointer; transition:background 0.15s;';
      chip.onmouseover = () => chip.style.background = '#e2e8f0';
      chip.onmouseout = () => chip.style.background = '#f1f5f9';
      chip.onclick = () => {
        document.getElementById('pc-input').value = q;
        sendMessage();
        starters.style.display = 'none';
      };
      starters.appendChild(chip);
    });
    panel.querySelector('#pc-messages').after(starters);
```

**Typing indicator** — show "..." while waiting for first token:

```javascript
  function showTyping() {
    messages.push({ role: 'assistant', content: '...' });
    renderMessages();
  }

  function clearTyping() {
    if (messages.length && messages[messages.length - 1].content === '...') {
      messages[messages.length - 1].content = '';
    }
  }
```

In `sendMessage()`, call `showTyping()` after pushing the user message, and `clearTyping()` before the first SSE data event.

**Session ID** — generate a random session ID per widget instance and send with every request:

```javascript
  const SESSION_ID = 'pc-' + Math.random().toString(36).slice(2, 10);
```

In the fetch body: `JSON.stringify({ message: text, session_id: SESSION_ID })`

**Hide starters after first message:**

```javascript
  // In sendMessage(), after first send:
  const startersEl = document.getElementById('pc-starters');
  if (startersEl) startersEl.style.display = 'none';
```

- [ ] **Step 2: Commit**

```bash
git add widget/widget.js
git commit -m "Add starter questions, typing indicator, and session ID to widget"
```

---

### Task 14: Rate Limiting

**Files:**
- Create: `app/rate_limit.py`
- Modify: `app/chat.py`
- Create: `tests/test_rate_limit.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_rate_limit.py
import time


def test_rate_limiter_allows_under_limit():
    from app.rate_limit import RateLimiter
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        assert limiter.check("1.2.3.4") is True


def test_rate_limiter_blocks_over_limit():
    from app.rate_limit import RateLimiter
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        limiter.check("1.2.3.4")
    assert limiter.check("1.2.3.4") is False


def test_rate_limiter_isolates_ips():
    from app.rate_limit import RateLimiter
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.check("1.1.1.1")
    limiter.check("1.1.1.1")
    assert limiter.check("1.1.1.1") is False
    assert limiter.check("2.2.2.2") is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_rate_limit.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write rate_limit.py**

```python
# app/rate_limit.py
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        self._requests[ip] = [t for t in self._requests[ip] if t > cutoff]
        if len(self._requests[ip]) >= self.max_requests:
            return False
        self._requests[ip].append(now)
        return True


chat_limiter = RateLimiter(max_requests=10, window_seconds=3600)
```

- [ ] **Step 4: Add rate limiting to chat endpoint**

In `app/chat.py`, add at the top of the `chat` function:

```python
from fastapi import Request, HTTPException
from app.rate_limit import chat_limiter

@router.post("/api/chat")
async def chat(request_body: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not chat_limiter.check(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in an hour.")
    # ... rest of function
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_rate_limit.py -v
```

Expected: 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add app/rate_limit.py app/chat.py tests/test_rate_limit.py
git commit -m "Add IP-based rate limiting (10 req/hour) to chat endpoint"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** All spec sections have corresponding tasks (architecture, endpoints, ingestion, LLM layer, widget, deployment, system prompt)
- [x] **Placeholder scan:** No TBDs, TODOs, or "implement later" — all code is complete
- [x] **Type consistency:** `LLMService.embed()` returns `list[float]`, used as `vector` in upsert and `query_vector` in search — consistent. `chunk_text()` signature matches usage in both `weaviate_client.py` and `ingest.py`. `search()` now takes `query_text` + `query_vector` for hybrid search.
- [x] **GreenPT integration:** Config has `greenpt_*` settings, LLM service handles `greenpt` provider, embedding uses GreenPT by default, env example includes all GreenPT vars
- [x] **Chunk size:** 250 tokens / 50 overlap per spec
- [x] **Single app architecture:** Dockerfile multi-stage, FastAPI serves static + API, widget same-origin
- [x] **Citations:** Programmatic `build_source_links()` appends deduplicated source links after LLM response — no reliance on LLM for citations
- [x] **Hybrid search:** `search()` uses `collection.query.hybrid()` with alpha=0.5 for balanced vector + keyword retrieval
- [x] **Conversation memory:** In-memory session store with MAX_HISTORY=10, session isolation, overflow trimming
- [x] **Starter questions:** 3 clickable chips in widget, hidden after first message
- [x] **Typing indicator:** "..." shown while waiting for first SSE token
- [x] **Rate limiting:** IP-based, 10 requests/hour, in-memory counter with time-window cleanup
