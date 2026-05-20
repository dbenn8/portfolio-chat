## The Problem

I'm an American living in the Netherlands, learning Dutch. Existing flashcard apps are generic — they don't understand Dutch grammar (de/het articles, diminutives, plural forms), they can't help with pronunciation, and they definitely can't take a PDF word list from my language class and turn it into enriched study cards.

I needed a tool that could take raw vocabulary — from typed lists, PDF uploads, or conversational requests — and automatically enrich each word with grammar details, pronunciation guides, example sentences, and conjugation tables. And I needed it to work with both cloud AI (for quality) and local LLMs (for cost and privacy).

## My Role

Solo project. Designed, built, and deployed in 4 days. I use it regularly for my Dutch studies.

## The Approach

Three distinct AI integration points, each solving a different problem:

**1. AI Word List Generation:** A conversational interface where I describe what I want to study ("give me 20 kitchen vocabulary words" or "words I'd need at the doctor's office") and the LLM generates a structured word list. Supports iterative refinement.

**2. PDF-to-Structured-Data Parsing:** Upload a PDF from language class and Claude extracts the vocabulary, maps it to the card schema, and creates study cards. Handles messy formatting, tables, and mixed Dutch/English content.

**3. Batch Enrichment:** Every card gets automatically enriched with grammar details (article, plural, diminutive), pronunciation guide, conjugation tables (for verbs), and contextual example sentences. Runs as a background queue.

## What I Built

- **Dual LLM backend** — abstracts over Claude API and OpenAI-compatible local LLMs. Per-task model selection (Sonnet for generation, Haiku for parsing) via Django admin.
  - **Guardrail rejection system** — configurable rate limiting (24-hour window), prompt-level guardrails, rejection detection, IP logging, automatic lockout.
  - **Background processing queue** — daemon thread with priority ordering (PDFs first, enrichment second), progress tracking, HTMX polling for real-time status. No external dependencies.
  - **Dutch-specific features** — time-telling with SVG clock generation, 50+ pronunciation rules, teacher/student roles with invite tokens.
  - **Full test suite** — AI generation settings, guardrail logic, LLM service, PDF upload, practice views, time utilities.
## The Result

A production app deployed on Appliku that I use for my actual Dutch studies. 30 seconds from "I need vocabulary for my doctor's appointment" to enriched flashcards with grammar, pronunciation, and examples — something that would take an hour manually.

The guardrail system handles edge cases (rate limiting, prompt injection, malformed PDFs) without false positives. The dual LLM backend lets me switch between Claude (quality) and local models (free, private) per task.

## Tech Stack

- **Backend:** Django 5.x, SQLite
  - **Frontend:** HTMX, Tailwind CSS
  - **AI:** Claude API (Sonnet/Haiku), OpenAI-compatible local LLMs
  - **Processing:** Background daemon queue, PDF parsing
  - **Analytics:** PostHog
  - **Deployment:** Appliku, Docker