# AI Builder Summary: n8n-appliku

## Part 1: Job Fit Evaluation

### AI Building / Super Agent Workstream

**Relevance: HIGH**

This project demonstrates infrastructure-level mastery of n8n -- not just building workflows, but building the deployment and provisioning layer beneath them. Daniel created a repeatable, automated system for spinning up isolated n8n instances per client, something most n8n users never touch.

**Signals for AI Product Builder role:**

1. **Deep platform internals knowledge.** Daniel understood n8n's Docker image architecture well enough to extend it: the non-root `node` user constraint, the entrypoint that auto-prepends `n8n` to commands, the need for `tini` as PID 1, and how n8n expects Postgres connection vars (individual `DB_POSTGRESDB_*` vars rather than a single `DATABASE_URL`). He wrote a shell wrapper to bridge the gap between Appliku's `DATABASE_URL` convention and n8n's expected format -- a small but precise piece of glue code that shows he reads source, not just docs.

2. **Automation-first thinking.** `provision.py` is a fully automated 7-step provisioning pipeline: create GitHub repo, template the config files, push code, create Appliku app via API, set encryption key, trigger deploy. One command (`python3 provision.py acme`) and a client has a live n8n instance in ~2 minutes. `teardown.py` provides the reverse with safety confirmation. This is the kind of developer tooling that scales a consulting practice.

3. **API integration without frameworks.** Both scripts use raw `urllib.request` to call the Appliku REST API -- no SDK, no dependencies beyond the standard library. Daniel explicitly chose this after first attempting the Appliku Python SDK and finding it insufficient (commit: "Rewrite provisioning to use direct API calls, no SDK"). This shows pragmatic problem-solving and a preference for minimal dependencies.

4. **Iterative, production-hardened development.** The git history (28 commits) tells a story of real deployment debugging: fixing non-root file permissions (`COPY --chmod=755`), handling Appliku's `skip_release_command` quirk, adding a 3-second delay for GitHub propagation after repo creation, correcting API endpoint formats through trial and error. This is someone who ships to production and fixes what breaks.

5. **Template architecture for multi-tenancy.** The project is structured as a template: `provision.py` generates client-specific `appliku.yml` and `README.md` from the template, creating isolated repos and apps. Each client gets their own database, encryption key, domain, and deployment pipeline. This is the foundation for a scalable n8n consulting business.

**Proven in production:** The n8n-mbo instance (live at `n8nmbo.applikuapp.com`) was provisioned from this template and then extended significantly -- Chromium + Puppeteer for browser automation, Xvfb for headless rendering, CRE platform sync workflows, auto-login flows. The MBO instance has 50+ commits of active development on top of the base template, proving the provisioning system works as intended and the base is extensible.

### AI Trust Workstream

**Relevance: MODERATE**

While this project isn't directly about evals, guardrails, or observability, it touches adjacent trust/reliability concerns:

- **Encryption key management.** The provisioning script auto-generates a 256-bit encryption key (`secrets.token_hex(32)`) and sets it via API, with explicit documentation that changing it renders all saved credentials unreadable. This shows awareness of credential security in automation platforms.
- **Destructive operation safety.** `teardown.py` requires the user to type the client name to confirm deletion -- a simple but effective guardrail against accidental data loss.
- **Secret hygiene.** The encryption key is never printed to stdout (a deliberate change in the git history: "Don't print encryption key"). The `.gitignore` excludes environment files.
- **Isolated tenancy.** Each client gets a separate database, encryption key, and deployment -- no shared state that could leak between clients.

### Unique Angle for n8n Application

Most n8n job applicants will show *workflows they built*. Daniel can show that he built the *infrastructure to deploy n8n itself* -- programmatically, repeatably, for multiple clients. This demonstrates:

- Understanding of n8n at the Docker/deployment layer, not just the UI
- The ability to automate n8n operations (provisioning, teardown) via APIs
- Real multi-tenant production usage, not just demos
- The consulting business context where n8n is the product delivered to clients

---

## Part 2: Portfolio Case Study Draft

### n8n-appliku: Automated Client Provisioning for Self-Hosted n8n

**One-liner:** Built an infrastructure template and CLI tooling that provisions isolated, production-ready n8n instances for consulting clients in under 2 minutes.

### Problem

I run an AI consulting practice where I deploy n8n workflow automation for clients. Each client needs an isolated n8n instance with its own database, credentials, and domain. Setting this up manually -- creating repos, configuring hosting, provisioning databases, generating encryption keys, triggering deploys -- took 30-45 minutes per client and was error-prone.

### Solution

I created `n8n-appliku`: a deployment template and automated provisioning system that turns client onboarding into a single command.

**Architecture:**
- Custom Dockerfile extending `n8nio/n8n:latest` with a shell wrapper that bridges Appliku's `DATABASE_URL` to n8n's individual Postgres env vars
- `appliku.yml` template defining the full stack: PostgreSQL 17, persistent volumes, HTTPS, timezone, secure cookies
- `provision.py`: automated 7-step pipeline (GitHub repo creation, config templating, code push, Appliku app creation via REST API, encryption key generation, deploy trigger)
- `teardown.py`: safe client removal with confirmation prompt

**Key technical decisions:**
- **No SDK dependency.** After hitting limitations with the Appliku Python SDK, I rewrote provisioning to use direct REST API calls via `urllib.request`. Zero external dependencies.
- **Template, not fork.** Provisioning generates fresh repos from the template rather than forking, so each client repo is clean and independent. Changes to the template don't cascade unexpectedly.
- **Entrypoint wrapper pattern.** Rather than modifying n8n's startup, I wrapped its entrypoint to inject environment variable parsing. This keeps the n8n image untouched and the customization layer minimal.

### Outcome

- **Provisioning time:** 30-45 min manual --> ~2 min automated
- **First client deployed (MBO):** Successfully provisioned and extended with Chromium/Puppeteer browser automation, 42-field CRE platform sync, and auto-login flows -- all built on top of the base template
- **Production infrastructure:** Live at `applikuapp.com` with PostgreSQL 17, persistent storage, HTTPS, and auto-deploy on push

### What This Shows About How I Work

- **I go below the abstraction.** I didn't just use n8n's cloud offering -- I understood its Docker internals well enough to deploy and extend it on custom infrastructure.
- **I automate before I need to.** The provisioning script was built before the second client, not after the tenth. I recognized the pattern early.
- **I iterate in production.** The 28-commit history shows real debugging: non-root permissions, API endpoint formats, timing issues. I ship, observe, and fix.
- **I keep dependencies minimal.** Standard library only for the provisioning scripts. A 4-line Dockerfile. A 25-line shell wrapper. Complexity lives in the orchestration, not the components.

### Tech Stack

Python 3 (stdlib only), Docker, shell scripting, Appliku REST API, GitHub CLI (`gh`), PostgreSQL 17, n8n (self-hosted)
