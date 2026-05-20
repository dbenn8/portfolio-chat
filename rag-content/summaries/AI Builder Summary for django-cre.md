# AI Builder Summary: django-cre

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Workstream Scores

**AI Building / Super Agent: 6/10**
This project doesn't directly involve building AI agents, LLM integrations, custom memory, or chat-first UX. However, the entire system was built using AI tools (Claude Code) and demonstrates the kind of complex multi-system orchestration that the Super Agent workstream builds. The field map system is architecturally similar to what an AI Skills system needs -- declarative JSON definitions that drive runtime behavior, extensible by end users. The n8n webhook integration shows comfort with event-driven orchestration. But there's no direct AI/LLM usage within the app itself.

**AI Trust: 4/10**
No eval frameworks, observability traces, guardrails, or human-in-the-loop AI safety patterns. The project has good observability practices (structlog, Sentry integration, credential audit logs, sync status tracking with field-level results) but these are applied to workflow automation, not to AI model behavior. The manual transfer system is a human-in-the-loop pattern, but for data transfer, not AI trust. The sync callback with per-field status verification is conceptually similar to eval harness thinking.

### Keywords Hit from Job Posting

| Keyword | Hit? | Evidence |
|---------|------|----------|
| Builder track record | YES | Full production system for a real consulting client, deployed on Appliku, 150+ model fields, multi-platform field mapping |
| AI-native builder | YES | Entire system built with Claude Code. Daniel describes himself as "an AI builder, not a real developer" |
| Workflow automation | YES | Core purpose: detect property changes, queue sync entries, dispatch to n8n webhooks for browser automation, track field-level results |
| Orchestration | YES | Multi-system orchestration: Django -> n8n webhook -> Puppeteer automation -> callback API -> credential queue drain |
| Open-source familiarity | YES | Built on Django (open source), integrating with n8n (open source). Uses the n8n webhook API as the sync execution layer |
| Coding background | PARTIAL | AI-assisted coding, not traditional. But the code quality is production-grade: proper service layer separation, Django CBVs, DRF APIs, encrypted credentials |
| Eval practice | NO | No formal eval or testing harness visible |
| Harness literacy | PARTIAL | The sync callback system (field-by-field status: OK/VERIFIED/VALUE_MISMATCH/SELECTOR_NOT_FOUND) is structurally similar to eval harnesses |
| Product instincts | YES | Smart prioritization: destination policy system (manual_transfer_only for CoStar due to ToS), user preference-driven field visibility, onboarding flow, progressive complexity |
| UX taste | YES | SpeedPy UI design system, htmx-driven rollup updates, copy-to-clipboard transfer workflow, section collapsibility, per-user sort preferences |
| Ambiguity comfort | YES | The entire field map rationalization system handles ambiguity: different platforms call the same concept different things, the system merges them under canonical keys |

### Strongest Talking Points (2-3 Bullets)

1. **"I built a multi-platform listing sync orchestration system that treats n8n as its execution engine."** The django-cre -> n8n -> Puppeteer -> callback pipeline is literally a workflow automation system that could be an n8n template. The architecture decision to use n8n webhooks as the automation layer (rather than building Puppeteer into Django) shows understanding of separation of concerns and the value of workflow orchestration platforms. This is the strongest n8n connection point -- Daniel is already an n8n customer who architected a system around it.

2. **"I designed a declarative field map system where JSON drives the entire platform integration -- UI rendering, manual transfer instructions, automation selectors, and computed rollups."** The field map JSON files are a single source of truth that drive: (a) which fields show platform badges in the property form, (b) what instructions appear in manual transfer, (c) what selectors Puppeteer uses for automation, (d) how rollups compute. This is the same "declarative skills" pattern the Super Agent workstream builds. Adding a new platform means adding one JSON file -- no code changes.

3. **"I built change detection and a sync queue that automatically fans out property edits to every connected platform."** When a user edits a property, the system diffs every trackable field, creates per-platform SyncQueueEntry records with the changed fields, and either triggers n8n automation or creates manual transfer checklists -- depending on the destination's policy. This demonstrates workflow automation thinking: event -> queue -> dispatch -> callback -> status.

### What to Highlight

- **The n8n integration is the centerpiece.** This system was literally designed around n8n as the automation execution layer. The webhook trigger, callback API, credential fetch API, and queue drain pattern are all designed to work with n8n workflows.
- **The field map architecture mirrors n8n's node system.** JSON definitions that drive runtime behavior, extensible without code changes, composable (rollups, sections, field mappings). This is the same pattern as n8n nodes.
- **AI-built, production-deployed.** This isn't a toy project. It handles real CRE listings for a brokerage client, with encrypted credentials, team-based access control, multi-platform sync, and a full onboarding flow.
- **The "custom destination" system is self-serve workflow building.** Teams can create their own platforms, define destination fields, map internal fields to destination fields, and export CSVs -- without touching code. This is the same "no-code workflow building" ethos as n8n.
- **Comfort with the messy middle.** CoStar's ToS prevents automation, so Daniel built a manual transfer workflow with copy-to-clipboard and field-by-field confirmation. This shows product judgment: ship what's possible now, automate later.

### What to Downplay

- **No direct AI/LLM integration in the app.** The app itself doesn't use Claude, GPT, or any AI model. The AI connection is that Daniel used AI tools to build it, not that the app does AI things. Don't oversell this as "AI product" -- sell it as "automation product built by an AI-native builder."
- **The eval/testing story is weak.** No visible test suite, no eval harness, no CI pipeline in the files reviewed. If asked about eval practices, pivot to the sync callback verification system as "structured evaluation of automation results."
- **The "coding background" is nontraditional.** The code is good, but Daniel should own the "AI builder" identity rather than claiming to be a developer. Frame it as: "I can read and modify any code, I just use AI tools to write it faster."

### Connection to n8n's Product

This project is unusually well-connected to n8n's product because:

1. **django-cre literally uses n8n as its automation backend.** The `N8N_CRE_SYNC_WEBHOOK_URL` env var, the webhook payload format, the callback API -- this is a real n8n integration.
2. **The field map system is conceptually identical to n8n's node definition system.** Declarative JSON that drives runtime behavior, defines input/output fields, and is extensible.
3. **The sync queue + credential queue is a workflow orchestration pattern.** Serial queuing for browser credentials (one automation session at a time) is the same kind of execution constraint that n8n handles with concurrency settings.
4. **The "destination" concept maps directly to n8n's "connection" concept.** Teams activate destinations, configure sync methods, and the system handles the rest.

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

I built a multi-platform listing sync engine for a commercial real estate brokerage that uses n8n as its automation backbone -- detecting property changes, queuing them, and dispatching them to CoStar, Crexi, and Moody's CRE through both automated and manual transfer workflows.

### The Problem

MBO Partners, a commercial real estate brokerage, manages property listings across multiple platforms (CoStar, Crexi, Moody's CRE / Catylist). Every time a property detail changes -- rent, square footage, availability -- someone has to manually update 3-4 platforms. Each platform has different field names, different UI layouts, different data formats, and different rules about which fields are required. A single property edit could mean 20 minutes of copy-paste across browser tabs, with frequent errors.

The brokers were spending hours per week on data entry they'd already done once. Worse, listings would drift out of sync across platforms, leading to confused prospects and missed deals.

### My Role

Solo AI builder and solution architect for this consulting engagement. I owned the entire system: requirements gathering with MBO, architecture design, implementation (using Claude Code), deployment, and ongoing iteration. There was no engineering team -- I was it.

### The Approach

I started by mapping the actual platform UIs. I spent time in CoStar's Listing Manager, Crexi's dashboard, and Moody's CRE property editor, documenting every field, every section, every dropdown option, every DOM selector. This became the field map system -- a set of canonical JSON files that serve as the single source of truth for how each platform organizes its data.

The key architectural insight was separation of concerns: Django handles the data model, change detection, and sync queue. n8n handles the actual automation execution (Puppeteer browser control). This meant I could build and iterate on the web app independently of the automation layer, and vice versa.

I also recognized early that not every platform allows automation. CoStar's Terms of Service prohibit browser automation, so I designed a dual-path system: automated sync for platforms that allow it, and a guided manual transfer workflow for platforms that don't. The manual transfer path shows the user exactly which field changed, what the new value is, where to find it on the destination platform, and lets them mark each field as transferred.

### What I Built

**Core data model:** A Property model with 150+ fields spanning identity, classification, building details, lease terms, contacts, parking, utilities, and more. Each field is tracked for changes via a diff mechanism in the model's `save()` method. Properties belong to Teams, and team members share access with role-based permissions.

**Declarative field map system:** Each platform (CoStar, Crexi, Moody's CRE) has a canonical JSON field map file (`mainapp/field_maps/costar.json`, etc.) that defines:
- Every field the platform expects, with its internal field mapping, display label, section, component type, and DOM selector
- Required fields per platform
- Rollup definitions (e.g., "Other Expenses" = CAM + Taxes + Insurance)
- Section ordering for the platform's UI
- Instructions for manual transfer

The field maps are loaded at runtime by a caching field map loader service. The property form renders platform badges next to each field, showing which platforms use that field and whether it's required. When platforms define the same rollup with different names (CoStar's "Other Expenses" vs. Moody's "Expenses"), a rationalization layer merges them into a single display with multiple platform badges.

**Change detection and sync queue:** When a property is saved, the model computes a field-level diff. Changed fields are fanned out into per-platform `SyncQueueEntry` records. Each entry tracks the changed fields, the target platform, the assigned credential, and the sync status (pending -> syncing -> success/partial/failed).

**Automated sync via n8n:** For automation-friendly platforms, the system POSTs a webhook payload to n8n containing the changed field values, platform listing ID, and credential fetch URL. n8n runs a Puppeteer workflow that logs into the platform, navigates to the listing, updates each field, and POSTs back a per-field callback with results (OK, VERIFIED, SELECTOR_NOT_FOUND, VALUE_MISMATCH, etc.). The callback API updates the sync entry, clears the property's sync lock, and drains the credential queue to process the next entry.

**Credential queue service:** Browser-based credentials can only run one automation session at a time. The credential queue service serializes sync entries per credential, queuing entries when another sync is already running and draining the queue when a callback arrives.

**Manual transfer workflow:** For platforms like CoStar (where automation is prohibited), the system generates a guided transfer checklist. Each changed field becomes a `SyncFieldResult` with the value to copy, the destination field label, component type, instructions, and section path. The manual transfer UI groups fields by platform section, provides copy-to-clipboard buttons, and tracks field-by-field confirmation with timestamps.

**Custom destinations:** Teams can create their own destination platforms (e.g., their company website, a WordPress CMS) without code changes. They define destination fields, map internal property fields to destination fields via a drag-and-drop mapping UI, and choose a sync method (manual, CSV export, API, or automation). The custom field map service dynamically generates field map JSON from the database mappings.

**Import/Export:** CSV import from Google Sheets creates properties, spaces, platform listings, and platform space mappings in one pass. CSV export generates platform-specific files based on the custom field mappings.

**API layer:** REST API with DRF + Swagger docs exposing credential fetch (for n8n to retrieve login credentials), sync callback (for n8n to report results), and field map retrieval (for external tools).

### The Result

MBO now manages all their listings from a single Django app. Property edits propagate to connected platforms either automatically (via n8n) or through a guided manual transfer workflow. The system tracks every sync with field-level audit trails. New platforms can be added by writing one JSON file (for canonical platforms) or through the self-serve destination builder (for custom platforms). The brokerage's listing management overhead dropped from hours to minutes per property update.

### Tech Stack

- **Backend:** Django 6.0.3, PostgreSQL 17, Celery + Redis, DRF with drf-spectacular
- **Frontend:** Tailwind CSS (SpeedPy UI design system), Alpine.js, htmx
- **Automation:** n8n webhooks, Puppeteer browser automation (separate repo)
- **Security:** Encrypted credentials (django-encrypted-fields with Fernet), team-based RBAC, service token auth for API, credential audit logging
- **Deployment:** Appliku (Docker, PostgreSQL, Redis, Celery worker + beat, media volumes)
- **Built with:** Claude Code (AI-assisted development)
