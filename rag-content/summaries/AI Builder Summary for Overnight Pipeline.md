# AI Builder Summary: MARVIN Overnight Pipeline

## Part 1: Job Fit Analysis — n8n AI Product Builder

### Project Overview

The MARVIN Overnight Pipeline is a production-grade, fully automated daily operations system that runs at 5:30 AM every morning via macOS LaunchAgent. It orchestrates a local LLM (Qwen3.5-35B-A3B running on Apple Silicon via LM Studio), multiple MCP servers, a task management platform (Blitzit), and Gmail — to produce an interactive HTML daily briefing published to a Tailscale-accessible web server. The system handles multilingual email triage (Dutch/English), cross-references emails against a task backlog, auto-completes resolved tasks, and provides a human-in-the-loop interface for task completion directly from a mobile browser.

This is not a prompt-and-pray demo. It runs unattended every day, handles failures gracefully, and its output is the first thing Daniel checks each morning on his phone.

### Relevance to AI Building / Super Agent Workstream

**Hybrid Deterministic + LLM Architecture**
The pipeline is deliberately designed so that everything that *can* be deterministic *is* deterministic. Python handles all data loading, filtering, diffing, backup management, HTML conversion, and API orchestration. The LLM (Qwen) is called only for two specific tasks where judgment is needed: (1) reading and triaging multilingual emails, and (2) producing a structured JSON changeset for task sync. This separation is a core design principle — not an accident. It means the system is predictable, debuggable, and the LLM's blast radius is contained.

Key deterministic steps:
- `pre_filter_archived()` — Two-way Gmail/Blitzit reconciliation via thread ID matching (Python regex, no LLM)
- `_filter_completed_threads()` — Strips already-resolved emails from LLM context before Qwen ever sees them
- Stale recurring task cleanup — Deduplicates overdue daily task instances by comparing schedule timestamps
- `diff_task()` — Field-by-field before/after comparison of every task change
- `transform_dutch_tables()` — Converts LLM-generated markdown tables to styled, interactive HTML with checkbox controls
- `_build_gmail_to_taskid_map()` + `_fuzzy_match_task()` — Thread ID and keyword-based matching between briefing items and Blitzit tasks
- Backup snapshot management — Pre/post sync snapshots for audit trail

**Privacy-Conscious AI: Local LLM for Sensitive Data**
Email content (personal health insurance, childcare invoices, school communications, financial data) never leaves the machine. The pipeline uses a quantized local model (Qwen3.6-35B-A3B at 4-bit, 131K-191K context) running on LM Studio. This is a deliberate architectural choice — cloud LLM providers are used for the base briefing (via Claude Cowork scheduled job), but the email-reading layer that touches actual personal data runs entirely on-device.

The `run-overnight.sh` orchestrator even runs `caffeinate -disu` to prevent macOS from sleeping during GPU-intensive inference — because a Metal driver deadlock during MLX prefill will kernel-panic the machine. That level of operational awareness comes from running this in production daily, not from a tutorial.

**Custom Memory / Shared Context**
The pipeline maintains its own memory layer:
- Blitzit backup snapshots (`latest.json`) serve as the system's "memory" of task state
- Completed thread IDs are tracked across the Gmail/Blitzit boundary, preventing re-creation loops
- The enrichment prompt includes both Claude's earlier briefing *and* current Blitzit state, enabling cross-referencing (e.g., "this Dutch email confirms payment for an open Blitzit task")
- Session logs and state files (`current.md`, `goals.md`) provide continuity across runs

**Multi-Tool Orchestration via MCP**
The system is a native MCP client that orchestrates three separate MCP servers in a single run:
1. Google Workspace MCP (local mcp-proxy on port 8808) — Gmail search and read
2. Blitzit MCP (cloud endpoint with Bearer token auth and SSE response parsing) — Task CRUD
3. LM Studio local inference server — LLM completions with tool-use support

The `blitzit_api.py` module implements a full MCP session lifecycle: initialization, session ID tracking, notification handshake, and SSE response parsing. This is production MCP integration, not wrapper code.

**Skills Architecture**
The daily briefing is defined as a Claude Cowork "Skill" (`SKILL.md`) — a structured, versioned instruction set that defines the entire pipeline's behavior. This mirrors n8n's own approach to composable, reusable automation components.

**Agentic Loop with Tool Use**
`marvin_overnight.py` implements a genuine agentic loop (up to 30 turns) where the local LLM can make tool calls (Gmail search, email read), receive results, and decide what to do next. The loop includes:
- Duplicate call detection and caching (`calls_made` dict with dedup keys)
- Think-tag stripping for reasoning models
- Graceful termination on `finish_reason: stop` or content-without-tools
- Continuation prompts when the model stalls

### Relevance to AI Trust Workstream

**Guardrails**
- Pre-filter layer strips resolved emails *before* the LLM sees them — reducing hallucination surface
- Completed thread ID guard blocks re-creation of tasks for already-resolved emails (prevents the re-creation loop that plagued early versions)
- Strict categorization rules (4-point test) embedded in the system prompt force the LLM to justify every Action Needed vs Low Priority classification
- JSON changeset validation with regex extraction and parse-error handling
- Tool call deduplication prevents the LLM from making redundant API calls

**Observability**
- Every tool call logs: function name, arguments (truncated), response size, and wall-clock time
- Turn-by-turn logging with preview of LLM output
- Pre-filter logs both directions of sync with counts
- Changeset execution logs success/failure per task with field-by-field diffs
- Raw LLM responses saved to `/tmp/qwen-changeset-raw.txt` for debugging
- Complete pipeline log at `/tmp/marvin-overnight.log` with timestamps at each phase boundary

**Reliability / Error Handling**
- `run-overnight.sh` explicitly avoids `set -e` — handles errors individually to prevent silent failures
- LM Studio startup has 3 retries with progressive backoff
- Model loading attempts 191K context first, falls back to 128K
- MCP proxy restart logic if port 8808 is not responding
- Job B (Blitzit sync) failure does not block the briefing from being published
- 30-minute timeout on LLM inference calls (production-appropriate for large context windows)
- Post-sync backup refresh ensures the next run starts from accurate state

**Human-in-the-Loop**
The briefing HTML includes interactive checkboxes on every Action Needed email row. Each checkbox is wired to a `data-task-id` attribute mapped to the corresponding Blitzit task. The "Mark Checked as Complete" button sends a POST to `/api/complete-tasks`, which completes tasks in Blitzit and visually strikes through the row. This gives Daniel a one-tap interface from his phone to close the loop on tasks the pipeline surfaced — genuine human-in-the-loop, not just a read-only dashboard.

The search-hint copy-to-clipboard feature is another human-in-the-loop affordance: since Android Chrome intercepts Gmail deep links, each email row includes a copyable search query so Daniel can paste it directly into the Gmail app search bar.

**Evals (Implicit)**
The field-by-field diff engine in `blitzit_sync.py` functions as a continuous evaluation mechanism. Every task the LLM proposes to create, update, or complete is logged with before/after state and appended to the briefing as a visible changelog. Daniel reviews this changelog every morning — it is, in effect, a daily human eval of LLM task-management accuracy.

---

## Part 2: Case Study Draft

### MARVIN Overnight Pipeline — A Privacy-First, Multi-Agent Daily Operations System

#### The Problem

I relocated to the Netherlands with my family. Overnight, my personal email inbox became a flood of Dutch-language communications: childcare invoices, health insurance letters, school notifications, government correspondence. Mixed in with my English-language work emails and Burrfect business. Missing a payment deadline or school registration because I couldn't parse a Dutch email at 7 AM while managing family responsibilities was a real risk.

I needed a system that would: read all my email overnight while I slept, translate and triage the Dutch ones, cross-reference against my existing task list, and present me with an actionable briefing I could review on my phone before the family woke up.

#### The Architecture

The pipeline runs as three sequential jobs orchestrated by a bash script (`run-overnight.sh`) triggered at 5:30 AM via macOS LaunchAgent:

**Job 0 (Claude Cowork, 5:00 AM):** A Claude Code scheduled job generates the base briefing — priorities, calendar, strategic focus, English email highlights — and writes a Blitzit backup snapshot. This runs in the cloud via Anthropic's API.

**Job A (Local LLM, 5:30 AM):** `marvin_overnight.py` runs a local Qwen3.5-35B-A3B model (4-bit quantized, 131K-191K context window) on Apple Silicon via LM Studio. This is the privacy boundary — all email content stays on-device. The script:
1. Runs a deterministic pre-filter that syncs Gmail archive status with Blitzit task completion (no LLM needed)
2. Loads the Claude-generated base briefing + Blitzit task state as context
3. Enters an agentic tool-use loop where Qwen searches Gmail, reads each Dutch email individually, translates and categorizes them, cross-references against open tasks, and weaves the results into the existing briefing
4. Writes the enriched briefing as markdown, then converts to styled HTML via a deterministic Python pipeline

**Job B (Local LLM, after Job A):** `blitzit_sync.py` feeds the completed briefing back to Qwen, which produces a JSON changeset (create/update/complete actions). Python validates and executes each change via Blitzit's MCP API, logs field-by-field diffs, refreshes the backup, appends a changelog to the briefing, and re-converts to HTML.

**The Result:** An interactive HTML page published to a local documentation server, accessible from any device on my Tailscale network. Each Dutch email row has a checkbox linked to its Blitzit task — I can complete tasks directly from my phone.

#### Key Design Decisions

**Why a local LLM for email?** My email contains health insurance details, childcare invoices, school communications, and government correspondence. Sending this to a cloud API — even one I trust — was a boundary I didn't want to cross for a daily automated pipeline. The local model handles the judgment-requiring work (translation, categorization, cross-referencing) while everything else is deterministic Python.

**Why deterministic steps where possible?** LLMs are expensive (in time — each Qwen turn takes 30-120 seconds at this context size) and unreliable for structured operations. The pre-filter that syncs Gmail archive status with Blitzit completion is pure Python: regex matching of thread IDs, set operations, API calls. It handles 80% of the "is this email still relevant?" question before the LLM ever runs. The diff engine, backup management, HTML conversion, and fuzzy task matching are all deterministic. The LLM's job is strictly: read email content, judge its priority, and produce structured output.

**Why three-phase with two different AI providers?** Claude (cloud) is better at strategic synthesis, calendar awareness, and English-language business context. Qwen (local) handles the privacy-sensitive email reading. The enrichment architecture means Qwen *adds to* Claude's work rather than replacing it — each model does what it's best at.

**Why interactive HTML instead of a mobile app?** Fastest path to value. The docs server was already running on Tailscale. Adding checkboxes with a Blitzit API integration took one afternoon. The search-hint copy-to-clipboard is a pragmatic workaround for Android Chrome stealing Gmail deep links — the kind of detail you only discover from using your own tool daily.

#### What I Learned

**Guardrails are not optional for production agent systems.** The re-creation loop was my first hard lesson: Qwen would see a Dutch email, create a Blitzit task for it, then the next day see the same email and create another task. The fix was a completed-thread-ID guard — a deterministic pre-filter that builds a set of already-handled thread IDs and blocks the LLM from acting on them. This pattern (deterministic guardrail constraining LLM action space) turned out to be the single most important architectural decision.

**Observability pays for itself on day one.** Every tool call is logged with timing. Every task change is logged with before/after diffs. The raw LLM output is saved. When something goes wrong at 5:30 AM, I can read the log and know exactly which turn, which tool call, which email caused the issue.

**The 80/20 of agent reliability is context management.** Qwen's accuracy improved dramatically when I started pre-filtering completed tasks out of its context window. Less noise in, better signal out. The same principle applies to the enrichment architecture: giving Qwen a high-quality Claude briefing as a starting point means it only needs to add Dutch emails, not synthesize an entire day's priorities from scratch.

#### Relevance to n8n

This pipeline is essentially what an n8n power user would build if n8n had native local-LLM support and privacy-aware routing. The architecture maps directly:

- **run-overnight.sh** = n8n workflow with Schedule Trigger, sequential execution nodes, error handling branches
- **Pre-filter (Python)** = n8n Code node doing deterministic data transformation
- **Qwen agentic loop** = n8n AI Agent node with tool-use and memory
- **Blitzit MCP calls** = n8n MCP tool nodes (or HTTP Request nodes with session management)
- **Gmail MCP calls** = n8n Gmail trigger + read nodes
- **Diff engine + changelog** = n8n Code node for structured logging
- **HTML conversion + publish** = n8n HTTP Response or webhook node

The gap I had to bridge with custom Python is exactly the gap n8n's AI Product Builder role is closing: making it possible for non-developers to build production agent systems with guardrails, observability, and human-in-the-loop — without writing 43KB of Python.
