# AI Builder Summary for Woordjes

## Part 1: Job Fit

### Project Overview

**Woordjes** ("little words") is a Dutch vocabulary flashcard app I built for myself and a Dutch language teacher to use with students. I'm an American expat learning Dutch in Haarlem, NL, and existing flashcard apps didn't handle Dutch-specific complexity well -- articles (de/het), irregular verb conjugations, the unique Dutch time-telling system, and pronunciation rules that don't map to English. So I built what I needed.

It's a full-stack Django + HTMX + Tailwind app deployed on Appliku, with Claude API integration for three distinct AI capabilities: generating word lists from any topic, parsing vocabulary from uploaded PDFs, and enriching every card with grammar data and pronunciation guidance.

### How This Maps to AI Product Builder

**AI Building / Super Agent track:**

- **Built a multi-stage AI pipeline, not just a wrapper.** The app uses Claude at three different points in the content lifecycle: (1) AI-generated word lists via conversational refinement, (2) PDF-to-structured-data extraction, and (3) batch enrichment that adds word type classification, verb conjugations, noun plurals/diminutives, adjective comparatives, and pronunciation approximations with rule explanations. Each stage has its own model selection (configurable per-task in the admin -- e.g., Haiku for enrichment, Sonnet for generation).

- **Designed the LLM integration architecture.** The `LLMService` abstraction supports both Claude API and local LLM backends (OpenAI-compatible, used with local Qwen during development). Backend switching is a single admin toggle. The service layer handles JSON parsing, code fence stripping, thinking tag removal (for reasoning models), and malformed JSON repair from local models. This shows practical experience with LLM reliability engineering.

- **Built guardrails and abuse prevention.** The word list generation feature includes prompt-level guardrails (the LLM is instructed to reject non-vocabulary requests), server-side rejection detection (scanning responses for known rejection phrases), a `GuardrailRejection` model that logs every blocked attempt with user/timestamp/IP, rate limiting (configurable per-24-hour window via admin), and automatic lockout when the limit is exceeded. This is production-grade trust infrastructure for an AI feature.

- **Background processing queue for AI work.** Rather than making users wait for enrichment (which hits the Claude API for every card), I built an in-process background queue (`queue.py`) that processes PDF uploads and enrichment jobs sequentially. The queue uses a priority system (PDFs first, then enrichment), with progress tracking via model fields and HTMX polling for real-time status updates. No Celery dependency -- just a daemon thread with connection cleanup.

- **Prompt engineering for structured output.** The enrichment prompt (`services/__init__.py`) includes a comprehensive Dutch pronunciation reference guide (50+ rules covering consonants, vowels, diphthongs, stress patterns, and spelling rules) that the LLM uses to generate phonetic approximations for English speakers. The prompt requests structured JSON with type-specific detail objects (conjugation tables for verbs, plural/diminutive for nouns, comparative/superlative for adjectives). Token budget scales dynamically with batch size (~400 tokens/card).

**AI Trust track:**

- **Guardrail system with monitoring.** Every rejected request is logged with full context (user, request text, LLM response, timestamp, IP address). The admin can review patterns and adjust the rejection limit. Users who exceed the limit are locked out for 24 hours -- they see a clear message, not a silent failure.

- **Admin-configurable AI settings as a singleton model.** The `AIGenerationSettings` model controls LLM backend choice, per-task model selection, API key storage, rejection limits, and notification email -- all manageable through Django admin without code changes. This is the kind of operational control that matters when AI features are in production.

- **Human-in-the-loop for AI output.** PDF parsing results go through a review page where the teacher can edit, add, or remove word pairs before creating the word list. AI-generated word lists go through an interactive refinement flow (conversational chat with the LLM) before approval. Nothing goes directly from AI to student-facing content without review.

### Technical Depth

- **Full-stack ownership:** Django models, views, templates, HTMX interactivity, Tailwind styling, Docker packaging, Appliku deployment config, PostgreSQL in production, background queue, analytics instrumentation.

- **Teacher/student multi-role system:** Teacher creates students, assigns word lists, views practice analytics (sessions per student, time-on-task, per-list breakdown). Students see only their assigned content. Invite link system with token expiration for student onboarding.

- **Dutch time-telling system:** Built a complete programmatic model of Dutch clock-telling (the "anchor method" where times reference the nearest hour or half-hour). Generates SVG clock faces, 144 time cards across all 5-minute intervals. No LLM needed -- this is domain knowledge encoded in code (`time_utils.py`).

- **Product analytics:** PostHog integration with event tracking across practice sessions, uploads, student management, and AI generation. Teacher-facing analytics dashboard with 7-day/30-day/all-time views per student.

- **Test coverage:** Tests for AI generation settings, guardrail rejection logic, LLM service (generation, refinement, rejection detection), PDF upload flow, practice views, time utilities, and more.

### Product Instincts

The project demonstrates several product-thinking patterns relevant to the role:

1. **Solve your own problem first.** I wasn't building a hypothetical product -- I was learning Dutch and frustrated with existing tools. The features reflect real usage pain points.

2. **AI as capability multiplier, not gimmick.** The Claude integration does three specific jobs (generate, parse, enrich) that would be tedious or impossible manually. A teacher uploading a 30-word vocabulary PDF doesn't want to manually add pronunciation guides and conjugation tables for every word.

3. **Design for the slow path.** AI enrichment can take 30+ seconds for a batch. Rather than blocking the UI, I built background processing with progress polling. The architecture uses a simple queue (no external dependencies) because the realistic load is "one teacher uploading a few lists per week."

4. **Ship the simplest thing that works, but architect for growth.** Single-teacher design with the teacher FK already on the user model for future multi-tenancy. Local LLM fallback for development. Configurable model selection per task.

---

## Part 2: Case Study Draft

### Woordjes: AI-Enhanced Dutch Vocabulary Learning

**The problem:** I moved to the Netherlands and started learning Dutch with a private teacher. She'd share vocabulary lists as PDFs -- scanned worksheets, typed word lists, textbook pages. I'd practice them with generic flashcard apps that had no concept of Dutch grammar. They couldn't tell me that "huis" takes "het" (not "de"), that "schrijven" is an irregular verb, or that "ui" is pronounced nothing like how an English speaker would guess.

**What I built:** A flashcard app with three layers of AI integration:

1. **PDF Upload + AI Parsing.** Upload a vocabulary PDF from a Dutch lesson. PyMuPDF extracts the text, Claude parses it into structured word pairs (Dutch term, article, translation, notes). The teacher reviews and edits the parsed results before creating the word list. This turns a 20-minute data entry task into a 2-minute review.

2. **AI Word List Generation.** Type a topic ("cooking", "medical terms", "driving vocabulary") and select a difficulty level. Claude generates 15-35 contextually appropriate Dutch-English word pairs. An interactive chat interface lets you refine: "Add more verbs", "Make it harder", "Remove the compound words." When you approve, the list is created and queued for enrichment.

3. **Batch Enrichment Pipeline.** Every new word list goes through background enrichment via Claude. For each word, the LLM returns: word type (noun/verb/adjective/etc.), whether it's irregular, type-specific grammar details (verb conjugation tables, noun plurals and diminutives, adjective comparative and superlative forms), phonetic pronunciation approximation for English speakers (e.g., "SKHRAY-vuhn" for "schrijven"), and applicable pronunciation rules with explanations. This data appears in an expandable details panel on each flashcard during practice.

**Architecture decisions:**

- **Dual LLM backend.** The service layer abstracts over Claude API and any OpenAI-compatible server (I used local Qwen during development). Switching is a single admin toggle. This let me iterate on prompts without burning API credits, and it means the app works offline.

- **Background queue, not async.** AI enrichment runs in a daemon thread processing jobs sequentially from the database. No Celery, no Redis queue, no external dependencies. The queue checks for pending work every 2 seconds, processes one item at a time, and cleans up database connections. This is appropriate for the actual usage pattern (one teacher, a few uploads per week) and keeps deployment simple.

- **Guardrails as a first-class feature.** The AI generation feature includes prompt-level constraints (the LLM is instructed to only generate Dutch vocabulary), server-side rejection detection, per-user rate limiting, rejection logging with full audit trail, and admin-configurable limits. This isn't paranoia -- it's what shipping an AI feature to real users requires.

- **Configurable model selection per task.** The admin panel lets you choose different Claude models for word generation (Sonnet -- needs creativity), PDF parsing (Haiku -- structured extraction), and enrichment (Haiku -- deterministic grammar data). This keeps costs proportional to task complexity.

**What I'd highlight for n8n:**

- I built this end-to-end: data model, AI integration, background processing, UI, deployment, analytics. No team, no designer, no product spec from someone else.
- The AI integration is practical, not decorative. Each of the three AI features solves a specific workflow bottleneck.
- I thought about trust from day one: human review of AI output, guardrails, rate limiting, audit logging.
- I used Claude Code as my development tool throughout, which gave me deep experience with AI-assisted development workflows -- relevant to building AI products at n8n.

**Tech stack:** Django 5 / Python, HTMX, Tailwind CSS, Anthropic Claude API, PyMuPDF, PostHog analytics, PostgreSQL, Docker, Appliku (deployment).
