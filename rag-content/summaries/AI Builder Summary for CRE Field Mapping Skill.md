# AI Builder Summary: CRE Field Mapping Skill

## Part 1: Job Fit

### What This Project Is

A **Claude Code Skill** -- a structured prompt/workflow definition that guides AI through a complex, multi-step technical task: onboarding a new commercial real estate (CRE) listing platform into an automated sync pipeline. The pipeline moves listing data from Google Sheets through Apps Script, n8n, and Puppeteer into target platforms like CoStar, Crexi, LoopNet, and YARDI.

The Skill is not a traditional codebase. It is a 233-line structured document (`SKILL.md`) plus a reference schema that together constrain and direct an AI agent through six phases of work -- from screenshot audit to end-to-end deployment -- producing correct, production-ready automation artifacts every time.

### Why This Maps to n8n's AI Building / Super Agent Workstream

n8n's AI Product Builder role (builder track) lists **Skills** as a first-class focus area within the AI Building workstream. This project is a Skill in the most literal sense:

| n8n AI Building Focus | How This Project Demonstrates It |
|---|---|
| **Skills** | This IS a Skill. A structured definition that makes AI reliable at a domain-specific task that would otherwise require deep platform knowledge, careful DOM inspection, and brittle manual work. |
| **AI-first product thinking** | The entire MBO Listing Sync system is designed AI-first. The field map JSON is the single source of truth consumed by both AI-generated Puppeteer scripts and human-facing manual transfer screens. The system assumes AI builds the automation; humans verify it. |
| **Chat-first building** | The Skill is invoked conversationally. A user says "add CoStar" or "map LoopNet fields" and the AI agent walks through all six phases interactively, asking for credentials, screenshots, and test listings as needed. |
| **Making AI reliable at complex tasks** | The core problem this Skill solves. Without it, AI hallucinates selectors, misidentifies field types, skips edge cases, and produces scripts that silently fail. The Skill's constraints make AI output production-grade. |

### Why This Maps to n8n's AI Trust Workstream

| AI Trust Focus | How This Project Demonstrates It |
|---|---|
| **Guardrails** | The Skill opens with a `CRITICAL SAFETY RULE: READ-ONLY ON ALL CRE PLATFORMS` block. AI is explicitly prohibited from clicking Save, filling form fields, or triggering syncs against live data. This is a hard guardrail -- not a suggestion, not a system prompt hint, but a structural constraint that the AI checks against before every browser interaction. |
| **Reliability** | The "Non-Negotiable Patterns" section (Phase 4) codifies 15 hard-won lessons from production failures: label-based lookup instead of brittle indices, per-field try-catch so one failure doesn't crash a batch, save-response waits instead of arbitrary delays, post-save verification to catch false positives. These patterns exist because the AI got them wrong without explicit constraints. |
| **Human-in-the-loop** | The Skill enforces human checkpoints at every phase boundary. Phase 1 requires the human to provide credentials and identify test listings. Phase 3 requires human verification of DOM inspection results. Phase 6 testing requires explicit human designation of test records. The AI never autonomously pushes to production. |
| **Preventing real-world harm** | The safety rule includes a "Why this matters" section explaining the real stakes: corrupted listings, broken deal negotiations, damaged broker reputations. This grounds the guardrail in concrete consequences, not abstract policy. |

### The Builder Profile This Demonstrates

This project shows someone who:

1. **Thinks in systems, not scripts.** The Skill orchestrates across 5 tools (Chrome browser, Puppeteer, Google Sheets, Apps Script, n8n, Docker) and produces artifacts consumed by both humans and machines. The field map JSON is a shared contract between AI automation and manual workflows.

2. **Designs for AI reliability, not AI capability.** The interesting problem isn't "can AI inspect a DOM?" -- it can. The interesting problem is "can AI do it correctly every time, across different platforms, without corrupting production data?" The Skill's structure is the answer.

3. **Learns from production failures and encodes those lessons.** Every "Non-Negotiable Pattern" has a backstory. "Never set `el.value` directly -- desyncs framework state from DOM" is a lesson that cost hours of debugging. The Skill turns tribal knowledge into repeatable process.

4. **Builds for the next platform, not just this one.** The Skill is platform-agnostic by design. It uses Crexi as a reference implementation but defines patterns that transfer to CoStar, LoopNet, YARDI, or any new provider. This is the same challenge n8n faces with its node/integration ecosystem.

---

## Part 2: Case Study Draft

### CRE Field Mapping Skill: Making AI Reliable at Platform Onboarding

**Context:** I run a commercial real estate listing sync service (MBO Listing Sync) that keeps property data synchronized between a Google Sheet and multiple CRE platforms. Each new platform requires: auditing every field in the platform's listing editor, building a JSON field map, writing Puppeteer automation scripts, and wiring everything through n8n workflows.

**Problem:** This onboarding process took 2-3 days of manual work per platform. Worse, when I tried using AI to help, it produced plausible-looking but broken output. It would guess at DOM selectors instead of inspecting them. It would identify a Quill rich text editor as a plain textarea. It would set `el.value` directly, desyncing Angular's state from the DOM. Each failure mode was different, hard to diagnose, and expensive to fix against live listings.

**Insight:** The AI wasn't lacking capability -- it was lacking structure. It could inspect DOMs, write Puppeteer scripts, and build JSON schemas. What it couldn't do was follow the correct sequence, apply platform-specific knowledge, and avoid the failure modes I'd already discovered. The problem was workflow, not intelligence.

**Solution:** I built a Claude Code Skill -- a structured definition that constrains and guides AI through the entire onboarding process in six phases:

1. **Screenshot Audit** -- Systematic capture of every field, noting exact labels, input types, option values, and required indicators
2. **Field Map Construction** -- JSON creation following a strict schema, with every field typed and mapped to both Sheet columns and DOM selectors
3. **DOM Inspection** -- Live verification of field types against the actual DOM, catching common misidentifications (rich text editors that look like textareas, hidden backing inputs, auto-formatting fields)
4. **Puppeteer Script Building** -- Code generation following 15 "Non-Negotiable Patterns" learned from production failures
5. **System Integration** -- Updates to Google Sheets, Apps Script, n8n workflows, and Docker deployment
6. **End-to-End Testing** -- Structured verification across field types, cross-page batches, error handling, and write-back confirmation

**The key design decisions:**

- **Safety guardrails at the top.** The Skill opens with an explicit READ-ONLY rule. AI must never click Save, fill form fields, or trigger syncs on live platforms. This isn't buried in fine print -- it's the first thing the AI reads, with concrete consequences explained.

- **Human-in-the-loop at phase boundaries.** The AI doesn't autonomously progress from audit to implementation to deployment. Humans provide credentials, verify DOM findings, designate test records, and approve deployments.

- **Failure patterns encoded as constraints.** Rather than hoping AI avoids mistakes, the Skill lists specific failure modes ("Looks like textarea, actually is Quill rich text editor") with detection methods. The "Non-Negotiable Patterns" section is a checklist of lessons from production, not theoretical best practices.

- **Single source of truth architecture.** The JSON field map serves both AI automation and human-facing manual transfer screens. This prevents the drift that happens when the same information lives in multiple places.

**Results:** Platform onboarding dropped from 2-3 days to 5-8 hours. More importantly, the output quality became consistent. The Skill produces the same caliber of field maps and Puppeteer scripts regardless of platform complexity, because the AI follows the same structured process every time. When I onboard the next platform, the Skill already knows about Angular state desync, rich text editor detection, and pill toggle deselection -- I don't have to rediscover those lessons.

**What this taught me about building AI products:** The highest-leverage work isn't making AI smarter -- it's making AI structured. A well-designed Skill turns an AI that "can probably do this task" into one that "reliably does this task correctly every time." That's the gap between demo and production, and it's the gap that n8n's Skills feature is designed to close.
