> I built a "chat with your Notion" product months before Notion shipped their own -- proof that identifying the right problem matters more than having the right resources.

## The Problem

Knowledge workers dump everything into Notion -- meeting notes, specs, research, decisions -- and then can't find any of it. Search only works when you remember the exact words you used. What people actually need is to *ask questions* about their own knowledge base and get answers grounded in their own data.

## My Role

Solo builder: product concept, architecture, full-stack development, and LLM integration.

## The Approach

I recognized that Notion's flat search was fundamentally broken for how people actually retrieve information. The answer was RAG (retrieval-augmented generation) -- let users ask natural language questions against their own workspace and get cited, contextual answers. I built a Django prototype with proper user management and OAuth-based Notion integration, treating security and data privacy as first-class concerns from day one. Users could selectively grant access to specific Notion pages rather than handing over their entire workspace -- a deliberate design choice around trust and control.

## What I Built

- **Notion OAuth integration** -- users connect their workspace and selectively choose which pages to index
- **Notion data pipeline** -- pulls and parses Notion's nested block structure into clean, chunk-able text suitable for embedding
- **Vector database with semantic search** -- embedded content for meaning-based retrieval, not just keyword matching
- **Conversational chat interface** -- users ask questions in natural language and get answers grounded in their own Notion data
- **Full user management and auth** -- registration, login, session handling, and secure API key storage
- **Per-user data isolation** -- each user's vector store is scoped to their account only

## The Result

Kumpel.ai worked. Users could connect their Notion, choose their pages, and have a genuine conversation with their own knowledge base. It was scrappy -- a prototype, not a polished product -- but it validated the core insight: people want to *talk to* their documents, not *search through* them.

Months later, Notion shipped Notion AI with built-in Q&A over workspace content. That's not a failure story -- it's a validation story. I identified the same gap that a $10B company eventually prioritized, and I had a working solution before they did.

## Tech Stack

- **Backend:** Python, Django
- **LLM integration:** OpenAI API (embeddings + chat completion)
- **Vector database:** Semantic search and retrieval
- **Data source:** Notion API (OAuth 2.0)
- **Auth:** Django user management with secure credential storage