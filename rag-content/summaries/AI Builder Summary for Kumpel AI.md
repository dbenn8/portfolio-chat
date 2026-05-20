# AI Builder Summary for Kumpel AI

## Part 1: Job Fit (n8n AI Product Builder)

### Project Overview

Kumpel AI is an early-stage AI-powered personal knowledge assistant that connects to a user's Notion workspace, ingests their content, builds a vector knowledge base, and lets them chat with their own data through a conversational interface. It was built as a two-repo product: a Django backend handling data ingestion, knowledge base construction, and AI-powered Q&A; and a React/Next.js chat frontend that streams real-time responses to the user.

This was built in late 2023, when RAG (Retrieval-Augmented Generation) patterns were still emerging and LlamaIndex was at v0.8. Building a multi-user RAG system at that stage required working directly with the underlying primitives rather than relying on turnkey frameworks that didn't yet exist.

### AI Building / Super Agent Workstream

**What I built:**

- **Full RAG pipeline from scratch**: Notion API integration -> JSON extraction -> Markdown conversion -> vector embedding -> GPT-4 chat with retrieval. Not a wrapper around a hosted service -- the entire data pipeline was hand-built.

- **Multi-user knowledge base architecture**: Each user gets isolated storage (JSON, Markdown, vector indices) with per-user Notion API keys stored via Django's auth system. The vector store is constructed per-user and persisted to disk using LlamaIndex's `GPTVectorStoreIndex`.

- **Streaming chat with conversational memory**: The Django backend uses LlamaIndex's `ChatMemoryBuffer` and streams GPT-4 responses token-by-token via `StreamingHttpResponse`. The React frontend reads the response stream using a custom `TextDecoderStream` implementation for real-time rendering.

- **Notion content processing engine**: A comprehensive block-by-block processor that handles 25+ Notion block types (paragraphs, headings, lists, code blocks, callouts, tables, synced blocks, child pages, databases, embeds, etc.) and converts them faithfully to Markdown. Recursive child block fetching with rate limiting, pagination, and retry logic for the Notion API.

- **Automated code documentation generator**: A utility that uses Python's AST module to extract function signatures, parameters, return types, dependencies, and comments from the codebase, generating a condensed documentation file designed to fit within GPT-4's context window for self-referential development assistance.

**Technical stack:**
- Backend: Django 3.2, Django REST Framework, LlamaIndex 0.8.x, LangChain 0.0.312, OpenAI GPT-4, Python 3.10
- Frontend: Next.js 13 (API proxy version) + Create React App (direct streaming version), React 18, react-markdown, axios
- Infrastructure: Docker, Gunicorn, Nginx (reverse proxy with streaming support), PostgreSQL (production), Replit (initial prototype)
- Vector stores: LlamaIndex document store (primary), Weaviate (scaffolded for future use)

**Relevance to n8n AI Product Builder:**
- Demonstrates understanding of the complete AI application lifecycle: data ingestion, transformation, embedding, retrieval, and generation
- Shows experience building multi-step pipelines that connect external APIs to AI models -- exactly the pattern n8n's AI nodes enable
- Streaming response handling across a full stack (Django -> Nginx -> React) shows depth in making AI feel responsive to end users
- The Notion integration involved working through paginated API responses, recursive data structures, rate limiting, and error recovery -- the same class of problems users face when building n8n workflows with external service nodes

### AI Trust Workstream

**What I built that's relevant:**

- **Per-user data isolation**: Every user's Notion data, vector indices, and chat logs are stored in sandboxed directories. The `read_user_file` and `write_user_file` utilities enforce that users can only access their own data, with an admin override for debugging.

- **API key management**: Notion API keys are stored per-user via a `UserSource` -> `Source` -> `Provider` model hierarchy with Django's ORM, not hardcoded or shared.

- **Authentication and session security**: Django's built-in auth with custom login views, CSRF token rotation, cross-domain cookie management for the decoupled chat frontend, and session-based identity propagation.

- **Defensive API integration**: The Notion API wrapper implements retry logic with exponential backoff on 429 rate limits, request timeouts, structured error logging to per-user error files, and graceful degradation when the API is unavailable.

- **Input validation and error boundaries**: User IDs are validated against Django's User model before file operations. The JSON-to-Markdown pipeline handles malformed blocks gracefully with per-block error handling rather than failing the entire page.

**Relevance to n8n AI Trust:**
- Multi-tenant data isolation is a core trust concern for any AI platform -- users need confidence their data isn't leaking to other users
- The defensive API integration patterns (retries, timeouts, error logging) are exactly what's needed for reliable workflow execution in n8n
- Structured error logging per user per operation creates the kind of observability that builds trust in AI systems

---

## Part 2: Case Study Draft

### Kumpel AI: Building an Early RAG-Powered Personal Knowledge Assistant

**The problem**: Knowledge workers store vast amounts of information in Notion -- meeting notes, project plans, todo lists, reference material -- but retrieving specific information means remembering where you put it and manually searching. In late 2023, ChatGPT had shown what conversational AI could do, but there was no way to point it at your own private data.

**What I built**: A full-stack application that lets users connect their Notion workspace and chat with their own data using GPT-4. The system handles the entire pipeline: authenticating with Notion, recursively fetching all pages and child blocks, converting 25+ block types to clean Markdown, generating vector embeddings, and serving a streaming chat interface with conversational memory.

**How it works (architecture):**

1. **Data Ingestion**: User provides their Notion API key. The system calls the Notion Search API with pagination to discover all accessible pages, then recursively fetches each page's block tree (child blocks, nested children, child pages, child databases). Rate limiting with configurable delays and retry logic handles Notion's API constraints. A `should_process` function tracks when each page was last fetched, allowing incremental updates without re-fetching everything.

2. **Content Processing**: A block processor maps each of Notion's 25+ block types to Markdown. Rich text with annotations (bold, italic, code, links, mentions) is preserved. Nested structures (bulleted lists inside toggle blocks inside callouts) are handled recursively with proper indentation. Child pages generate separate Markdown files with cross-references.

3. **Knowledge Base Construction**: The Markdown files are fed to LlamaIndex's `SimpleDirectoryReader`, chunked, embedded via OpenAI's embedding model, and stored in a `GPTVectorStoreIndex`. Each user's index is persisted to their own directory on disk. The system was architected to support Weaviate as an alternative vector store for production scaling.

4. **Chat Interface**: Users ask questions through a React chat UI. The Django backend loads the user's vector index, creates a chat engine with `similarity_top_k=3` retrieval and conversational memory (1500 token buffer), and streams the GPT-4 response token-by-token. The frontend renders responses progressively using a custom `TextDecoderStream` with Markdown formatting via `react-markdown`.

**Key design decisions:**

- **Per-user everything**: Rather than a shared vector database with access controls, each user gets their own vector index. Simpler to reason about data isolation, and the index sizes for individual Notion workspaces are small enough that this scales to the target user base.

- **JSON intermediate format**: Rather than converting Notion blocks directly to Markdown, the system first saves the complete page structure as JSON. This lets users re-run the Markdown conversion without re-fetching from Notion, and preserves the original data for debugging and future processing improvements.

- **Streaming responses**: Implemented end-to-end streaming from LlamaIndex's chat engine through Django's `StreamingHttpResponse`, with Nginx configured to disable buffering (`X-Accel-Buffering: no`). This makes the AI feel responsive even when GPT-4 takes several seconds to generate a full answer.

- **Incremental sync**: The `last_processed_time` tracking and `hrs_threshold` parameter let users control how aggressively the system re-fetches from Notion. A force refresh re-fetches everything; otherwise, recently-processed pages are skipped.

**What I'd do differently today:**

- Use a managed vector database (Pinecone, Weaviate Cloud) instead of per-user file-based indices for better scaling and concurrent access
- Add chunking strategy tuning -- the default LlamaIndex chunking worked but wasn't optimized for Notion's document structure
- Implement proper background job processing (Celery) for the Notion sync, which can take minutes for large workspaces
- Add source citations in chat responses so users can click through to the original Notion page

**What this demonstrates:**
- End-to-end AI product building: from API integration through data transformation to user-facing AI chat
- Working with LLM frameworks (LlamaIndex, LangChain) at a low level, not just calling hosted APIs
- Multi-user SaaS architecture with data isolation and auth
- Full-stack development across Python/Django and React/Next.js
- Comfort with the messy reality of building AI products: rate limits, streaming, error handling, incremental processing
