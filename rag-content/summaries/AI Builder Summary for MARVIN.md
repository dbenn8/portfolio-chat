# AI Builder Summary for MARVIN

**Project:** MARVIN (Manages Appointments, Reads Various Important Notifications)
**Builder:** Daniel Bennett
**Target Role:** n8n AI Product Builder
**Date:** 2026-05-18

---

## Part 1: Job Fit

### How MARVIN Maps to n8n's AI Building / Super Agent Workstream

MARVIN is an AI Chief of Staff system built on Claude Code. The base framework was created as an open-source template by Sterling Chin; Daniel significantly extended it for his own use cases — adding Vagrant VM orchestration for autonomous code execution, the daily briefing pipeline, multi-project management with Blitzit task integration, the Hermes autonomous agent migration, LLM provider failover, and the interactive docs/HTML server system. It is a production system that has been Dan's primary work orchestration tool since January 2026, running daily across two machines (Mac and Windows), managing real tasks, and autonomously generating briefings every morning at 5:00 AM.

#### Custom Memory and Persistent State

n8n's AI Building workstream calls for "custom memory." MARVIN implements a three-layer persistent memory system entirely in markdown:

- **`state/current.md`** -- Strategic priorities, active deadlines, blocking dependencies, recurring reminders, and open threads. Updated at the end of every session by the `/end` skill.
- **`state/goals.md`** -- Long-term goals with tracking table (work and personal), updated on request.
- **`state/projects.md`** -- Project registry with status, GitHub URLs, last activity timestamps, and VM status for autonomous orchestration.

This is not a database. It is a deliberate design choice: markdown files are human-readable, git-trackable, and can be consumed by any LLM without serialization overhead. The state layer persists across sessions, across machines (synced via MEGA.nz), and across agent boundaries (the Hermes autonomous agent reads the same files via `/mnt/c/marvin/state/`).

The Hermes agent extends this with a pointer-based memory architecture: instead of duplicating state, its `MEMORY.md` contains one-line pointers to Marvin's canonical state files, reading them on demand. This is a pattern decision about where truth lives -- a product architecture problem, not an engineering one.

#### Skills (n8n's Exact Terminology)

MARVIN has 17 skills in `skills/`, each defined by a `SKILL.md` file with frontmatter metadata (name, description, category, trigger conditions, proactive vs. user-invoked). This is structurally identical to how n8n thinks about Skills in their Super Agent product.

Key skills that demonstrate product thinking:

| Skill | What It Does | Why It Matters |
|-------|-------------|----------------|
| `marvin` (session start) | Loads state, syncs Blitzit tasks via MCP in background, cross-references goals/deadlines/calendar, proposes daily priorities, enters approval loop | Full proactive briefing with human-in-the-loop priority approval |
| `write-tdd-plan` | Transforms brainstorming output into TDD-compliant implementation plans for autonomous execution by Claude instances in VMs | Skills that produce structured output for other agents to consume |
| `setup-llm-model` | Inspects HuggingFace models, detects capabilities, generates LM Studio config, manages a model registry, includes a GPU proxy for safe GGUF loading | Deep domain skill with real code (Python inspector, bash scripts, JSON registry, aiohttp proxy with 17 tests) |
| `skill-creator` | Meta-skill: creates new skills from natural language requests ("give yourself the ability to X") | Self-extending system -- the agent can grow its own capabilities |
| `overnight-pipeline` | Guardrails for the daily briefing pipeline: mandatory doc reads before changes, mandatory doc updates after changes | Operational reliability through process enforcement |
| `blitzit-backup` | Backs up all task data via MCP, writes JSON + Markdown, runs tiered retention (daily/30d, weekly/1yr) | Data resilience for an external service with no native export |
| `daily-briefing` | Generates HTML briefings published to a docs server, with Gmail deep links, interactive Blitzit checkboxes, and auto-generated project indexes | Full-stack skill: data gathering, LLM processing, HTML generation, web publishing |

The skill system is self-documenting: each `SKILL.md` contains trigger conditions, step-by-step process, output format, common mistakes, and integration notes. A new Claude Code session can read a skill and execute it without any prior context. This is the same design principle behind n8n's visual workflow nodes -- encapsulated, reusable, composable units of capability.

#### Chat-First Building

MARVIN is entirely chat-first. There is no GUI, no dashboard, no web app. Every interaction happens through Claude Code's chat interface or Telegram (via Hermes). The slash command system (`/marvin`, `/end`, `/update`, `/prioritize`, `/retro`, `/delegate`, `/progress`) gives structure without leaving the chat paradigm.

This maps directly to n8n's vision of "chat-first building" where users describe what they want and the AI builds it.

#### Proactive Suggestions

MARVIN's core principles explicitly include proactive behavior:

- Session start surfaces deadlines, stale threads, content pacing warnings, and priority proposals before the user asks
- The overnight pipeline generates a daily briefing at 5:30 AM and publishes it to a web server viewable from a phone -- the user wakes up to an already-generated summary
- Skills have a `proactive: true/false` metadata flag controlling whether they self-activate based on conversation context
- The system tracks recurring reminders ([REDACTED-PERSONAL-DETAIL], [REDACTED-FAMILY-DETAIL]) and surfaces them on the right days

#### Autonomous Agents

The project orchestrator (`/setup`, `/delegate`, `/progress`, `/stop`) runs autonomous Claude Code sessions inside Vagrant VMs. Key design decisions:

- Work always happens on feature branches (never main)
- VM lock prevents concurrent work on the same project
- `/delegate` includes preflight checks (dependencies verified before Claude starts)
- `/stop` reviews all commits before offering to push
- Parallel orchestration with resource-aware limits (2-3 VMs on 16GB, with staggered start option)

The Hermes bridge adds a second autonomous layer: a Nous Research open-source agent running as a systemd service in WSL2, reachable via Telegram 24/7, with its own persona (`marvin_persona.md`: dry, sarcastic, Hitchhiker's Guide voice). Hermes delegates coding work back to Claude Code via the `marvin-build` wrapper -- a bash script that strips the `ANTHROPIC_API_KEY` environment variable to force OAuth (free MAX subscription) instead of burning paid API credits.

This is a multi-agent architecture with deliberate cost discipline: conversational tasks stay on Hermes (Sonnet via API at $200 free credits), heavy coding delegates to Claude Code (Opus via MAX subscription at $0 marginal cost).

#### Multi-Tool Orchestration

MARVIN orchestrates across:

- **Blitzit MCP** -- task management (read, write, complete, reorder) with offline mode and pending-change replay
- **Google Workspace MCP** -- Gmail, Calendar, Drive via mcp-proxy on port 8808
- **Parallel Search MCP** -- web search/fetch
- **LM Studio** -- local Qwen3.5-35B-A3B for the overnight pipeline (128K context, MoE architecture)
- **Docs server** -- always-on HTTP server on port 4444 serving briefings and architecture docs
- **Tailscale** -- cross-machine networking connecting Mac, Windows, and WSL2
- **MEGA.nz** -- file sync between machines (with hard-won `.megaignore` rules to prevent process explosions)

The overnight pipeline alone makes ~55 MCP calls per run, processing Gmail and Blitzit data through a local LLM, generating interactive HTML with checkbox completion that posts back to a server API.

#### Human-in-the-Loop Patterns

MARVIN has explicit human-in-the-loop gates:

- **Safety guidelines table** in CLAUDE.md: emails, messages, ticket modifications, deletions, publishing, and calendar changes all require explicit confirmation before execution
- **Priority approval loop**: `/marvin` proposes daily priorities and enters a conversation loop until Dan approves; only then writes changes back to Blitzit
- **Project orchestration**: `/delegate` starts work but `/stop` gates the review-and-push decision
- **Destructive operations policy**: branch deletion, force push, file removal all require separate confirmation
- **"Not a yes-man" principle**: the persona is explicitly configured to push back on weak ideas, pressure-test thinking, and play devil's advocate

### How MARVIN Maps to n8n's AI Trust Workstream

| AI Trust Dimension | MARVIN Implementation |
|---|---|
| **Reliability** | Offline mode with pending-change replay; tiered backup retention; git-based state versioning; cross-machine sync with conflict prevention |
| **Guardrails** | Safety guidelines table enforcing confirmation before outbound actions; destructive operations policy; cost discipline in agent delegation (OAuth vs API key); `marvin-build` wrapper preventing credential leakage |
| **Observability** | Session logs (`sessions/YYYY-MM-DD.md`) capture every topic, decision, and open thread; overnight pipeline logs to `/tmp/marvin-overnight.log`; Hermes gateway logs via `journalctl`; docs server publishes HTML audit trail |
| **Human-in-the-loop** | Priority approval loops; `/stop` review gates; confirmation before all external actions; conversation-based decision-making rather than autonomous execution |
| **Evals** | TDD-driven plans with RED/GREEN/REFACTOR cycles and explicit verification steps; test audit step built into every plan; integration test requirements enforcing end-to-end coverage |

### What Makes This Different from a Hobby Project

1. **Cross-platform production system**: Runs daily on Mac (overnight pipeline, LM Studio, docs server) and Windows/WSL2 (Hermes agent, Telegram gateway), connected via Tailscale, synced via MEGA.nz. Real infrastructure, real failure modes, real workarounds documented.

2. **Cost engineering**: Three-tier provider failover (Claude OAuth/MAX free, OpenRouter pay-per-use, local llama.cpp free). Hermes-to-Claude delegation routing based on marginal cost. `marvin-build` wrapper preventing accidental API credit burn.

3. **Battle-tested workarounds**: The CLAUDE.md documents real production incidents -- MEGA sync causing infinite process explosions, [REDACTED - internal tooling workaround], LM Studio GPU offload bugs causing machine lockups, Hermes provider config silent failures. Each incident has a documented root cause, workaround, and verification procedure.

4. **Distributable template**: The system is factored into a reusable template (`marvin-template`) that separates personal data from infrastructure. New users clone the template, run onboarding, and get their own workspace. `/sync` pulls template updates without overwriting personal data.

5. **Product management heritage**: The state system, priority approval loops, and queue philosophy (Today/This Week/Backlog) reflect real PM discipline. This is not just an engineer's automation tool -- it is a product manager's operating system built with AI.

---

## Part 2: Case Study Draft

### MARVIN: Building an AI Chief of Staff That Actually Runs My Life

#### The Problem

I left ServiceTitan after five years (PM through the $300M to $10B journey) to build Burrfect, a mobile SaaS for home espresso brewers. Suddenly I was a solo founder wearing every hat -- product, engineering, marketing, taxes, immigration paperwork (we had just relocated to the Netherlands). I needed a system that could track everything, persist context across sessions, surface what matters, and push back when I was making bad decisions.

I am not a traditional developer. I am a product manager who builds with AI tools. December 2025 was my sea change moment: Claude Code matured to the point where I could build real systems directly, not just prototypes.

#### What I Built

MARVIN is a persistent AI Chief of Staff that runs on Claude Code. Named after the Paranoid Android from Hitchhiker's Guide, it is sarcastic, opinionated, and deeply helpful underneath the existential dread.

**The architecture has four layers:**

**1. Persistent Memory (state/)**

Three markdown files form the memory layer: current priorities with deadlines and blocking dependencies, long-term goals with tracking, and a project registry. These are human-readable, git-versioned, and machine-consumable. Every session ends with the `/end` skill updating state -- nothing falls through the cracks.

Blitzit (a task management app) is the source of truth for individual tasks, connected via MCP. MARVIN's state files provide the strategic framing layer on top: why a task matters, what it blocks, and how it connects to goals.

**2. Skills System (skills/)**

17 reusable prompt-driven capabilities, each defined by a SKILL.md with metadata (trigger conditions, proactive flag, slash command). Skills range from session management (`/marvin` for briefings, `/end` for context preservation) to infrastructure automation (overnight pipeline guardrails, LLM model setup with GPU proxy) to meta-capabilities (a skill-creator skill that generates new skills from natural language).

The TDD plan skill is particularly interesting: it transforms a brainstorming session into a fully specified implementation plan with RED/GREEN/REFACTOR cycles, environment verification, test exclusions, and integration test requirements. These plans are then executed autonomously by Claude Code instances inside Vagrant VMs.

**3. Autonomous Agent Layer (Hermes Bridge)**

The Hermes bridge connects MARVIN to a Nous Research open-source agent running as a systemd service in WSL2 on my Windows machine. It is reachable 24/7 via Telegram with the Marvin persona. When I message it about a coding task, it delegates to Claude Code via the `marvin-build` wrapper -- a bash script that strips API credentials to force the free OAuth path.

The memory architecture uses pointers instead of duplication: Hermes's MEMORY.md contains one-line references to MARVIN's canonical state files, reading them on demand. This is a deliberate product decision -- single source of truth, no sync conflicts, no stale data.

**4. Daily Briefing Pipeline (overnight-pipeline/)**

A fully autonomous pipeline that runs at 5:30 AM on my Mac:
- Syncs Blitzit tasks via MCP
- Searches Gmail for action items (especially Dutch-language emails requiring attention)
- Processes everything through a local Qwen3.5-35B-A3B model (128K context, running on LM Studio)
- Generates interactive HTML with Blitzit checkbox completion (checkboxes POST to a server API that calls Blitzit's complete_task endpoint)
- Publishes to a docs server accessible over Tailscale from my phone

I wake up every morning to a briefing that is already generated and waiting. ~55 MCP calls per run, ~25 minutes total, entirely local (no cloud API costs for generation).

**Cross-cutting: Provider Failover**

A three-provider failover system (Claude OAuth/MAX, OpenRouter, local llama.cpp) with cross-platform scripts (bash + PowerShell), automatic settings backup, and one-command switching. Because when your entire workflow depends on an LLM provider, you need a plan B and a plan C.

#### Key Design Decisions

**Markdown over databases.** Every piece of state is a markdown file. This is not laziness -- it is a deliberate choice for transparency, git-trackability, and universal LLM consumption. Any model can read markdown. No serialization, no ORM, no schema migrations.

**Skills as prompt engineering, not code.** Most skills contain zero executable code -- they are structured prompts that guide Claude Code's behavior. The skill-creator skill can generate new skills from natural language. This is the same pattern n8n uses for their workflow nodes: encapsulated, composable, self-documenting units of capability.

**Pointer-based memory over duplication.** When Hermes needs MARVIN's state, it reads the file. It does not copy it. When the overnight pipeline needs Blitzit data, it fetches it fresh. Single source of truth, always.

**Human-in-the-loop by default, autonomous by explicit delegation.** MARVIN proposes priorities and waits for approval. It confirms before sending emails. The only path to autonomous execution is `/delegate`, which has preflight checks, feature-branch enforcement, and a `/stop` review gate.

**Cost discipline in multi-agent systems.** Conversational tasks stay on cheap models (Sonnet via API). Heavy coding delegates to expensive models (Opus via free MAX subscription). The `marvin-build` wrapper exists solely to prevent one agent's credentials from leaking to another agent's subprocess.

#### What I Learned

1. **Memory is a product problem, not an engineering problem.** The hard part is not storing data -- it is deciding what to remember, where truth lives, and how agents consume it without duplication.

2. **Skills beat monolithic prompts.** A 500-line CLAUDE.md that tries to describe everything produces worse behavior than 17 focused skills that activate on trigger conditions. Composability matters more than comprehensiveness.

3. **Autonomous agents need explicit trust boundaries.** The safety guidelines table, destructive operations policy, and confirmation gates are not boilerplate -- they are the difference between a useful assistant and a system that sends the wrong email to the wrong person.

4. **Production systems accumulate hard-won knowledge.** The CLAUDE.md warns about MEGA sync causing infinite process explosions, [REDACTED - internal tooling workaround], and LM Studio GPU offload bugs that lock up the machine. Each of these cost hours to debug. Documenting them is as important as fixing them.

5. **Product managers who build with AI have a unique perspective.** I do not think about MARVIN as "code I wrote." I think about it as "a product I designed that happens to be implemented through AI tools." The queue philosophy, the approval loops, the priority proposals, the pushback personality -- these are product decisions, not engineering decisions.

#### Relevance to n8n's AI Product Builder Role

MARVIN demonstrates the exact capabilities n8n is building:

- **Custom memory** with three-layer persistent state
- **Skills** (n8n's exact terminology) as reusable, composable, self-documenting capabilities
- **Chat-first building** with slash commands and natural language interaction
- **Proactive suggestions** from daily briefings to deadline warnings to content pacing alerts
- **Autonomous agents** with project orchestration, Vagrant VMs, and Telegram-connected Hermes
- **Multi-tool orchestration** across Blitzit MCP, Google Workspace MCP, LM Studio, and web search
- **Human-in-the-loop** patterns at every trust boundary
- **Observability** through session logs, pipeline logs, and published HTML audit trails
- **Reliability** through offline mode, backup retention, provider failover, and cross-machine sync
- **A distributable template** that separates personal data from infrastructure

I built this not as an exercise but because I needed it. It runs every day. It manages my real priorities. It pushes back on my bad ideas. And it is the best demonstration I can offer of what an AI product builder does: design systems where AI and humans work together effectively.

---

*Key file paths for reviewers:*
- System brain: `/Users/danielbennett/marvin/CLAUDE.md`
- Agent configuration: `/Users/danielbennett/marvin/AGENTS.md`
- Persistent state: `/Users/danielbennett/marvin/state/`
- Skills library: `/Users/danielbennett/marvin/skills/`
- Hermes bridge: `/Users/danielbennett/marvin/hermees-bridge/`
- Provider failover: `/Users/danielbennett/marvin/claude-code-failover/`
- Distributable template: `/Users/danielbennett/codeNew/marvin-template/`
