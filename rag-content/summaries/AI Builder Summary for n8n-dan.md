# AI Builder Summary for n8n-dan

## Part 1: Job Fit

### What This Project Is

n8n-dan is Daniel's personal n8n instance running at n8ndan.applikuapp.com, deployed on Appliku with PostgreSQL. What makes it unusual: the Docker image embeds Tailscale, giving a cloud-hosted n8n container outbound access to services on Daniel's private tailnet — specifically LM Studio running local LLMs on his MacBook Pro M2 Max.

This is not a demo. It is live infrastructure that Daniel built and operates as part of MARVIN, his AI-powered personal operating system.

### Relevance to AI Building / Super Agent Workstream

**Deep platform engagement.** Daniel does not just use n8n — he extends it at the infrastructure level. The Dockerfile uses a multi-stage Alpine build to install Tailscale binaries into the n8n container, runs tailscaled in userspace networking mode (no NET_ADMIN required, works as non-root), and exposes a SOCKS5/HTTP proxy on localhost:1055 that n8n HTTP Request nodes route through. This is production networking knowledge applied to make n8n do something it cannot do out of the box: call private LLM endpoints.

**Workflow complexity.** The three exported workflows (Phase 1a, 1.1, 1.2) show iterative development of multi-step data pipelines that fetch context from a private docs server, filter and transform it deterministically in Code nodes, call a local LLM (Qwen 3.5 35B) via the OpenAI-compatible API, and extract structured results. Each phase adds capability:

- **Phase 1a** — Baseline: fetch 6 context files from a Tailscale-accessible docs server, normalize responses, build a prompt, call LM Studio, extract a priority summary.
- **Phase 1.1** — Adds Blitzit task filtering: deterministic Code node that implements done-board filtering, completed-thread-ID extraction for cross-referencing with Gmail, stale recurring task detection, and compact output with stats. This is porting logic from a standalone Python script into n8n's execution model.
- **Phase 1.2** — Adds Gmail integration: two Gmail search queries (broad inbox + Dutch-sender-specific), deduplication, cross-filtering against Blitzit completed thread IDs, and fan-in with the task context before the LLM call. This version uses native Gmail OAuth nodes, replacing an earlier MCP-proxy approach (visible in the git history).

**Architecture thinking.** The workflow design shows deliberate choices: continueOnFail on HTTP nodes to handle network failures gracefully, per-item normalization that handles multiple response formats across n8n versions, fan-in Code nodes that collapse per-file items into a single context bag, and 30-minute timeouts on LLM calls (realistic for large local models). The proxy configuration (`http://127.0.0.1:1055`) is set per-node, not globally — Daniel understands that only tailnet-bound requests need the proxy.

**Part of a larger AI system.** n8n-dan is one component in MARVIN (Manages Appointments, Reads Various Important Notifications), which includes:
- An overnight pipeline (Python + LM Studio + MCP) that generates daily briefings at 5:30 AM
- A docs server on port 4444 serving HTML briefings via Tailscale
- Blitzit task management with two-way sync
- Gmail pre-filtering with Dutch email handling (Daniel lives in the Netherlands)
- Interactive checkbox completion from the HTML briefing back to Blitzit's API

The n8n workflows are the cloud-hosted component of this system — they can run even when Daniel's laptop is asleep (as long as Tailscale is connected), unlike the LaunchAgent-based overnight pipeline.

### Relevance to AI Trust Workstream

**Local LLM integration demonstrates privacy-aware architecture.** By routing LLM calls through Tailscale to a local model (Qwen on LM Studio), Daniel keeps personal data (Gmail content, task lists, daily priorities) off third-party AI APIs. The n8n instance itself runs in the cloud, but inference happens on hardware he controls. This is a practical implementation of the "use AI but control your data" principle that the Trust workstream cares about.

**Progressive trust in automation.** The git history shows Daniel building capability incrementally — not shipping a fully autonomous agent on day one. Phase 1a just reads and summarizes. Phase 1.1 adds deterministic filtering rules (no LLM involved — pure logic). Phase 1.2 adds Gmail but with conservative search bounds (15 days, 50-message limits). The overnight pipeline adds auto-completion of stale tasks but only after human-readable changelog generation. This incremental approach to automation scope is exactly the kind of judgment needed for AI Trust work.

### Key Technical Details

| Aspect | Detail |
|--------|--------|
| Deployment | Appliku (Dockerfile-based), PostgreSQL 17 |
| Domain | n8ndan.applikuapp.com |
| Tailscale | Userspace networking, SOCKS5/HTTP proxy on :1055, auth key via env var |
| LLM endpoint | LM Studio at laptop.tailf840c8.ts.net:1234, OpenAI-compatible API |
| Model | Qwen 3.5 35B-A3B (MoE, 3B active per token) |
| Workflows | 3 exported (data fetch, Blitzit filter, Gmail prefilter) |
| Git branches | master + feat/tailscale-sidecar (11 commits of iterative development) |
| Timezone | Europe/Amsterdam |

---

## Part 2: Case Study Draft

### Title: Bridging Cloud Workflows and Local LLMs with n8n + Tailscale

### The Problem

Daniel runs a personal AI operating system (MARVIN) that needs to:
1. Pull context from multiple sources (task manager, Gmail, local markdown files)
2. Filter and prioritize that context deterministically
3. Summarize the result using an LLM
4. Do all of this without sending personal data to third-party AI APIs

The overnight pipeline handles this with a Python script running on his MacBook, but it only works when the laptop is awake. He needed a cloud-hosted component that could run the same logic on-demand, with access to the same local LLM.

### The Approach

**Infrastructure layer:** Extended the stock n8n Docker image with a Tailscale sidecar. Multi-stage build installs tailscale binaries from Alpine, copies them into the n8n image, and a wrapper entrypoint script starts tailscaled in userspace mode before delegating to n8n's original entrypoint. The Tailscale auth key is injected via environment variable — no key in the image, clean separation of concerns. The proxy runs on localhost:1055, and only the HTTP Request nodes that target tailnet services use it.

**Workflow layer:** Built three progressively more capable workflows:

1. **Phase 1a (Pull Cowork Data):** Fetches 6 context files (goals, current priorities, last session log, base briefing, task data, manifest) from a Tailscale-accessible docs server. Each file is fetched as a separate n8n item, normalized to handle different response formats, then collapsed into a single context bag. A Code node builds an LLM prompt and sends it to LM Studio via the Tailscale proxy. The response is parsed into a one-sentence priority summary.

2. **Phase 1.1 (Filter Blitzit):** Adds a deterministic pre-filter for Blitzit task data before it reaches the LLM. The Code node implements: filtering done-board tasks older than 7 days, extracting Gmail thread IDs from completed task descriptions (for cross-referencing), detecting stale recurring task instances (same title, multiple open copies, all but newest before today). Output includes the filtered task set plus metadata (completedThreadIds, staleToComplete candidates, stats).

3. **Phase 1.2 (Gmail Prefilter):** Adds two Gmail OAuth searches — broad inbox (last 15 days) and Dutch-sender-specific (15 senders: schools, healthcare, delivery services, etc.). Results are deduplicated, cross-filtered against Blitzit's completed thread IDs (so emails that already have a completed task are suppressed), and merged into the context bag before the LLM call. The git history shows this replaced an earlier MCP-proxy approach with native Gmail nodes — a deliberate simplification.

**Deployment:** Pushed to Appliku via git. The appliku.yml declares the PostgreSQL database, volume mount for n8n data persistence, and all required environment variables including the Tailscale auth key. The instance runs at n8ndan.applikuapp.com with HTTPS, secure cookies, and a single-hop proxy configuration.

### What It Demonstrates

**For AI Building / Super Agent:**
- Extending n8n's reach beyond its network boundary using Tailscale — a pattern applicable to any enterprise scenario where workflows need to call internal services
- Iterative workflow development (11 commits, 3 workflow versions) showing how to evolve from simple data fetch to multi-source pre-filtered LLM pipelines
- Hybrid deterministic + LLM architecture: business rules (task filtering, deduplication, thread ID matching) run in Code nodes; only the final summarization uses the LLM. This keeps behavior predictable and debuggable.
- Practical use of n8n as personal infrastructure, not just a tool for building customer-facing automations

**For AI Trust:**
- Data sovereignty: personal email and task data processed by a local LLM, never leaving the user's hardware for inference
- Incremental trust: each workflow phase adds scope gradually, with deterministic guardrails (filtering rules, message limits, explicit thread-matching logic) before any LLM involvement
- Graceful degradation: continueOnFail flags, error normalization, and fallback handling ensure the workflow produces useful output even when individual sources fail

### Connection to the Broader System

n8n-dan is one piece of a system that includes:
- **MARVIN overnight pipeline** — Python + LM Studio + MCP, runs at 5:30 AM via LaunchAgent, generates HTML briefings with interactive Blitzit checkboxes
- **Docs server** (port 4444) — serves briefings via Tailscale to Daniel's phone
- **Blitzit sync** — two-way task management integration with Google Calendar and Notion
- **Claude Code (MARVIN)** — AI chief of staff that reads from and writes to the same state files

The n8n workflows can be seen as the "always-on cloud brain" complement to the laptop-dependent overnight pipeline. Same data sources, same LLM endpoint, but reachable from anywhere n8n can run.
