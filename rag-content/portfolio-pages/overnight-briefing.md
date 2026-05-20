## The Problem

I relocated to the Netherlands with my family. Overnight, my email inbox became a flood of Dutch-language communications: childcare invoices, health insurance letters, school notifications, government correspondence — all mixed in with English-language work emails and Burrfect business.

Missing a payment deadline or school registration because I couldn't parse a Dutch email at 7 AM while managing family responsibilities was a real risk. I needed a system that would read all my email overnight, translate and triage the Dutch ones, cross-reference against my existing task list, and present me with an actionable briefing I could review on my phone before the family woke up.

## My Role

I designed and built the entire pipeline end-to-end: the bash orchestrator, the Python agentic loop, the Blitzit sync engine, the HTML conversion pipeline, and the interactive briefing interface. This is a solo project — ~2,200 lines of production code running daily since March 2026.

## The Architecture

Three sequential jobs orchestrated by a bash script triggered at 5:00 AM via macOS LaunchAgent:

**Job 0 — Claude Cowork (5:00 AM):** A Claude Code scheduled job generates the base briefing — priorities, calendar, strategic focus, English email highlights — and writes a Blitzit backup snapshot. This runs in the cloud via Anthropic's API.

**Job A — Local LLM (5:30 AM):** `marvin_overnight.py` runs a local Qwen3.5-35B-A3B model (4-bit quantized, 131K–191K context) on Apple Silicon via LM Studio. This is the privacy boundary — all email content stays on-device. The script:

- Runs a deterministic pre-filter that syncs Gmail archive status with Blitzit task completion (no LLM needed)
  - Loads the Claude-generated base briefing + Blitzit task state as context
  - Enters an agentic tool-use loop (up to 30 turns) where Qwen searches Gmail, reads each Dutch email, translates and categorizes them, cross-references against open tasks, and weaves results into the briefing
  - Writes the enriched briefing as markdown, then converts to styled HTML via a deterministic Python pipeline
**Job B — Blitzit Sync (after Job A):** `blitzit_sync.py` feeds the completed briefing to Qwen, which produces a JSON changeset (create/update/complete actions). Python validates and executes each change via Blitzit's MCP API, logs field-by-field diffs, refreshes the backup, appends a changelog to the briefing, and re-converts to HTML.

**The result:** An interactive HTML page published to a local documentation server, accessible from any device on my Tailscale network. Each task row has a checkbox linked to its Blitzit task — I can complete tasks directly from my phone.

## Key Design Decisions

### Why a local LLM for email?
My email contains health insurance details, childcare invoices, school communications, and government correspondence. Sending this to a cloud API — even one I trust — was a boundary I didn't want to cross for a daily automated pipeline. The local model handles the judgment-requiring work (translation, categorization, cross-referencing) while everything else is deterministic Python.

### Why deterministic steps where possible?
LLMs are expensive in time — each Qwen turn takes 30–120 seconds at this context size — and unreliable for structured operations. The pre-filter that syncs Gmail archive status with Blitzit completion is pure Python: regex matching of thread IDs, set operations, API calls. It handles 80% of the "is this email still relevant?" question before the LLM ever runs. The diff engine, backup management, HTML conversion, and fuzzy task matching are all deterministic. The LLM's job is strictly: read email content, judge its priority, and produce structured output.

### Why two different AI providers?
Claude (cloud) is better at strategic synthesis, calendar awareness, and English-language business context. Qwen (local) handles the privacy-sensitive email reading. The enrichment architecture means Qwen *adds to* Claude's work rather than replacing it — each model does what it's best at.

### Why interactive HTML instead of a mobile app?
Fastest path to value. The docs server was already running on Tailscale. Adding checkboxes with a Blitzit API integration took one afternoon. The search-hint copy-to-clipboard is a pragmatic workaround for Android Chrome stealing Gmail deep links — the kind of detail you only discover from using your own tool daily.

## What I Learned

**Guardrails are not optional for production agent systems.** The re-creation loop was my first hard lesson: Qwen would see a Dutch email, create a Blitzit task for it, then the next day see the same email and create another task. The fix was a completed-thread-ID guard — a deterministic pre-filter that builds a set of already-handled thread IDs and blocks the LLM from acting on them. This pattern (deterministic guardrail constraining LLM action space) turned out to be the single most important architectural decision.

**Observability pays for itself on day one.** Every tool call is logged with timing. Every task change is logged with before/after diffs. The raw LLM output is saved. When something goes wrong at 5:30 AM, I can read the log and know exactly which turn, which tool call, which email caused the issue.

**The 80/20 of agent reliability is context management.** Qwen's accuracy improved dramatically when I started pre-filtering completed tasks out of its context window. Less noise in, better signal out.

## Tech Stack

- **Orchestration:** Bash (run-overnight.sh), macOS LaunchAgent, Claude Cowork scheduled jobs
  - **AI — Cloud:** Claude (strategic briefing via Anthropic API)
  - **AI — Local:** Qwen3.5-35B-A3B via LM Studio on Apple Silicon (M2 Max, 64GB)
  - **Integrations:** Gmail MCP, Blitzit MCP, LM Studio API
  - **Pipeline:** Python (marvin_overnight.py, blitzit_sync.py, convert_briefing.py)
  - **Delivery:** HTML docs server, Tailscale for mobile access
  - **Data:** JSON backups with tiered retention (daily/30d, weekly/1yr)