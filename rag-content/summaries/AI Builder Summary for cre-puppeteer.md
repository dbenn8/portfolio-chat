# AI Builder Summary for cre-puppeteer

## Part 1: Job Fit Evaluation

### Workstream Scores

| Workstream | Relevance | Score |
|---|---|---|
| **AI Building / Super Agent** (browser & computer use) | **Direct hit** -- production browser automation orchestrated by n8n workflows, anti-detection patterns, multi-platform selector management, runtime code loading | **9/10** |
| **AI Trust** (evals, observability, guardrails, reliability) | Strong -- structured error taxonomy, fallback caching, version-pinned rollouts, screenshot-on-error, multi-tenant monitoring | **7/10** |

### Why This Project Maps to n8n's "Computer and Browser Use" Priority

n8n's AI Product Builder role explicitly calls out "computer and browser use" as a core workstream. This project is exactly that: headless Chromium controlling three different CRE platforms (CoStar, Crexi, Catylist) via Puppeteer, orchestrated entirely through n8n workflow nodes.

The architecture solves the hardest real-world problems in browser automation at scale:

- **Selector fragility** -- Every platform constantly changes their UI. The selector catalog pattern (`SELECTORS` object at the top of each script) means when CoStar moves a button, you update one line in one file, and every client instance self-heals on the next cycle. This is the same problem n8n's browser/computer-use agents will face: web UIs are moving targets.
- **Anti-detection** -- The `humanDelay()` helper with preset timing profiles (400-1200ms between fields, 2-5s after navigation) mimics human interaction cadence. Bot detection, CAPTCHA handling, and Cloudflare challenge selectors are first-class concerns, not afterthoughts. This is table-stakes knowledge for building production browser agents.
- **Multi-platform abstraction** -- Three different CRE platforms with different form structures, login flows, multi-space models (CoStar: building+spaces, Catylist: property+listing, Crexi: spaces as cards), and ID capture patterns. Each gets a consistent `SELECTORS` / `FIELD_MAP` / `syncTo*()` structure. This is the kind of abstraction layer n8n's agent system needs for computer use across arbitrary websites.

### Keywords for Resume/Cover Letter

`browser automation` | `Puppeteer` | `headless Chromium` | `computer use` | `n8n workflow orchestration` | `runtime code loading` | `multi-tenant SaaS` | `anti-detection` | `selector management` | `bot detection handling` | `CAPTCHA detection` | `human-like interaction timing` | `thin-loader architecture` | `version-pinned deployments` | `graceful degradation` | `multi-platform abstraction` | `field mapping` | `structured error taxonomy`

### Talking Points

1. **"I built the thing n8n is building."** n8n's AI Building workstream includes browser and computer use. I already have a production system where n8n workflows orchestrate Puppeteer to control three enterprise CRE platforms. I know the failure modes, the anti-detection requirements, and the selector maintenance burden firsthand.

2. **"Thin-loader = hot-reloadable agent skills."** The architecture where n8n Code nodes fetch scripts at runtime from a versioned repo is conceptually identical to how n8n's AI agent loads Skills. Fix a broken selector in the shared repo, and every client instance picks up the fix without redeployment. This is the same problem as updating an AI agent's tool definitions without restarting the agent.

3. **"I designed for the reliability gap."** Browser automation breaks constantly. My system has a structured error taxonomy (LOADER_FAILED, SCRIPT_ERROR, SELECTOR_NOT_FOUND, SESSION_EXPIRED, CAPTCHA_BLOCKED, TIMEOUT), cached fallbacks when GitHub is unreachable, version-pinned rollouts so a bad push doesn't cascade to all clients, and screenshot-on-error for debugging. These are exactly the guardrails and observability patterns the AI Trust workstream cares about.

4. **"Multi-tenant from day one."** Each CRE brokerage (client) runs their own n8n instance, but all instances fetch the same shared automation scripts. I can roll out a fix to one client, verify it works, then update the rest -- canary deployments for browser automation. This is the operational maturity n8n needs for enterprise AI features.

5. **"I know what breaks per-client vs. globally."** The README's failure matrix (platform selector change = global fix, session expiration = per-client fix, CMS change = per-client fix) shows I think about failure domains the way a platform builder needs to. This translates directly to thinking about which AI agent failures are systemic vs. user-specific.

---

## Part 2: Portfolio Case Study Draft

### Hook

> When a commercial real estate brokerage lists a property, they have to manually enter the same data into 3-4 different platforms -- CoStar, Crexi, Catylist, their own website. Each platform has different forms, different field names, different login flows. For a firm with 50 active listings, that's hundreds of hours of copy-paste per year. I built a system that does it automatically, using n8n to orchestrate headless browser automation across all platforms simultaneously.

### Problem

CRE brokerages maintain listings on multiple platforms (CoStar/LoopNet, Crexi, Catylist/Moody's) plus their own website. Each platform has a different web UI, different form fields, different publishing workflows. Keeping listings in sync means a human manually logging into each platform, finding the listing, and updating fields one by one. It's slow, error-prone, and the first thing that gets skipped when brokers get busy -- which means stale listings, missed leads, and lost revenue.

The platforms don't offer APIs. The only interface is their web UI.

### Role

Solo architect and builder. I designed the system architecture, wrote all the Puppeteer automation scripts, built the n8n workflow orchestration, and created the multi-tenant deployment model. Built entirely with AI-assisted development (Claude Code).

### Approach

Instead of building a monolithic automation tool, I designed a three-layer architecture:

1. **Data layer**: Google Sheets as the single source of truth (brokers already live in spreadsheets). One sheet per client, standardized column schema.
2. **Orchestration layer**: n8n workflows that trigger on sheet changes, route data to the right platform scripts, handle retries, and report results back to the sheet.
3. **Automation layer**: Shared Puppeteer scripts fetched at runtime by n8n nodes. The "thin-loader" pattern means each n8n Code node is just a ~50-line fetch-and-execute stub. The real automation logic lives in a versioned Git repo.

Key architectural decisions:
- **Runtime code loading** over bundled scripts -- so fixing a broken selector doesn't require redeploying every client's n8n instance
- **Version-pinned fetches** with cached fallback -- so a bad push doesn't cascade, and network failures don't halt syncs
- **Structured error taxonomy** -- so the workflow can route failures correctly (CAPTCHA_BLOCKED needs human intervention; SELECTOR_NOT_FOUND means the platform changed their UI; SESSION_EXPIRED means re-login)
- **Human-like timing profiles** -- randomized delays between interactions to avoid bot detection, with named presets (between_fields, after_navigation, before_submit) for consistency across all platform scripts

### What I Built

**Shared automation scripts** for 3 CRE platforms:
- **CoStar/LoopNet**: Building-level + multi-space forms, rich text editors, photo upload, MFA-aware login
- **Crexi**: Multi-space card layout, headline-based listings, sublease handling
- **Catylist/Moody's**: Two-layer property + listing model (create property first, then attach listings), one listing per space

**Thin-loader framework** for n8n:
- 50-line Code node stubs that fetch, cache, and execute remote scripts
- `globalThis.__crePuppeteerEntry` convention for script-to-loader handoff
- `AsyncFunction` constructor for safe dynamic code execution
- AbortController-based fetch timeouts with graceful cache fallback

**Anti-detection and reliability patterns**:
- `humanDelay()` with 6 named timing presets (400ms-6s ranges)
- CAPTCHA/Cloudflare detection selectors built into every script
- Screenshot-on-error hooks for post-mortem debugging
- 5-tier error classification: LOADER_FAILED, SCRIPT_ERROR, SELECTOR_NOT_FOUND, SESSION_EXPIRED, CAPTCHA_BLOCKED

**Multi-tenant operations model**:
- Per-client n8n instances with shared script repo
- Canary deployment via per-client version pinning
- Failure domain separation (global vs. per-client fixes documented)
- GitHub PAT-based private repo access with token rotation plan

### Result

A production-ready browser automation system that turns n8n into a multi-platform CRE listing sync engine. One brokerage's data enters a Google Sheet and flows to 3 platforms automatically. Selector fixes deploy to all clients in minutes, not days. The system is designed for the reality that web UIs break constantly -- every failure mode has a name, a routing path, and a remediation playbook.

### Tech Stack

| Layer | Technology |
|---|---|
| Browser automation | Puppeteer (headless Chromium) |
| Workflow orchestration | n8n (self-hosted on Appliku) |
| Data source | Google Sheets API |
| Script hosting | GitHub (private repo, raw content API) |
| Caching | n8n static data (workflow-level persistence) |
| Deployment | Appliku (per-client n8n instances) |
| Development | Claude Code (AI-assisted development) |

### n8n Connection

This project demonstrates direct, production experience with:
- **n8n workflow architecture** -- Code nodes, workflow settings, static data, credential management
- **Browser automation at scale** -- the exact capability n8n is building into their AI agent platform
- **The reliability challenges** of computer use -- selector fragility, bot detection, session management, error classification
- **Multi-tenant platform operations** -- the same operational model n8n uses for their cloud offering
- **Runtime skill loading** -- architecturally analogous to how n8n's AI agent loads and executes Skills
