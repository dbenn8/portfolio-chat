## The Problem

MBO is a commercial real estate brokerage that lists properties on multiple platforms simultaneously — CoStar, LoopNet, Crexi, Catylist (Moody's CRE), and their own website. Each platform has its own UI, its own field names, its own quirks. Keeping listings in sync across five platforms was eating hours of manual data entry every week, with inevitable inconsistencies.

The broker wanted one place to manage all listings — a single Google Sheet — and have changes automatically flow to every platform. Some platforms have APIs. Most don't. Some actively block automation. The system needed to handle all of these realities.

## My Role

I designed the full system architecture and built every component: the n8n workflow suite, the Django web app for field management, the Puppeteer browser automation scripts, and the deployment infrastructure. This is my project end-to-end — I chose n8n because I'd been running my own instance and knew it could handle the orchestration complexity.

## The Approach

The system has three layers:

**Layer 1 — n8n Workflow Orchestration:** Eight workflows running on a self-hosted n8n instance. The main loop polls the Google Sheet for changes, routes each listing to the correct platform workflow, and manages a queue for rate-limited platforms. A webhook-based variant handles real-time updates. Content generation workflows use LLMs to produce listing descriptions and social media posts.

**Layer 2 — Browser Automation:** For platforms without APIs (most of them), Puppeteer scripts handle the actual data entry. These run inside n8n Code nodes using a thin-loader architecture: each node is ~50 lines that fetches the real script from a shared GitHub repository at runtime, caches it locally, and falls back to cache if the fetch fails. Fix a selector once in the shared repo, and all client instances pick it up automatically.

**Layer 3 — Django Field Management:** A Django web app manages the canonical field maps for each platform — which fields exist, what they're called on each platform, what type of input control they use, and how they map to the internal data model. The same JSON field map drives both the automated sync (Puppeteer reads it for selectors) and a manual transfer screen (for platforms like CoStar that prohibit automation).

## What I Built

- **8 n8n workflows** — listing sync (main loop, queue + webhook variant, per-platform), content creation, content repurposing, automated client reports, social media scheduling
  - **Thin-loader Puppeteer scripts** — runtime code-fetching from GitHub with caching, version pinning for canary deployments, 5-tier error taxonomy (CAPTCHA_BLOCKED, SESSION_EXPIRED, SELECTOR_NOT_FOUND, etc.)
  - **Django field management app** — declarative JSON field maps as single source of truth, manual transfer screen for platforms that block automation, self-serve custom destination system
  - **n8n deployment infrastructure** — `provision.py` spins up isolated n8n instances per client with PostgreSQL in ~2 minutes, `teardown.py` cleans up
  - **n8n Workflow SDK usage** — programmatic workflow authoring for the queue + webhook variant
  - **Cross-execution caching** — `$getWorkflowStaticData('global')` for script caching, `$workflow.settings` for per-instance config
## The Result

The broker manages listings in one Google Sheet. Changes flow automatically to all platforms within minutes. For platforms that block automation, the manual transfer screen provides a guided copy-paste workflow with field-by-field confirmation — shipping what's possible now rather than waiting for a perfect solution.

The thin-loader architecture means I can fix a broken selector for one platform and every client instance picks up the fix without redeployment. The provisioning script means onboarding a new client is a 2-minute automated process instead of 30–45 minutes of manual setup.

This is an ongoing paid engagement — the system is in production handling real listings for a real brokerage.

## Tech Stack

- **Orchestration:** n8n (self-hosted on Appliku), n8n Workflow SDK
  - **Browser Automation:** Puppeteer (thin-loader architecture via n8n Code nodes)
  - **Backend:** Django 6.0.3, PostgreSQL, Celery, Redis
  - **Frontend:** Tailwind CSS, Alpine.js
  - **Infrastructure:** Docker, Appliku, GitHub (script hosting)
  - **Integrations:** Google Sheets API, CoStar, Crexi, Catylist, LoopNet
  - **AI:** LLM content generation for listing descriptions and social posts