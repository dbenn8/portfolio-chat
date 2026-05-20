# AI Builder Summary: Meal Planning + Shared Docs Server

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Workstream Scores

| Workstream | Score | Rationale |
|------------|-------|-----------|
| **AI Building / Super Agent** | 8/10 | Strong demonstration of a conversational AI pipeline that turns a short planning chat into fully-deployed, production-quality deliverables. The workflow -- recommend recipes, approve/reject until 3 are locked, auto-generate shopping lists organized by store layout, auto-generate cook-mode walkthroughs with timers, auto-publish to a family docs server -- is exactly the "AI agent that delivers value to end users" pattern n8n is building toward. Slightly below top marks because the published outputs are static HTML (no dynamic AI loop at serving time). |
| **AI Trust** | 5/10 | Some guardrail thinking visible (localStorage state isolation, server-side validation, CORS headers, no arbitrary code execution in the HTTP server), but this project isn't primarily about trust, reliability, or safety constraints on AI behavior. |

### Keywords Hit

- **Proactive suggestions** -- The AI recommends recipes based on past family successes. The overnight briefing pipeline (which feeds the same docs server) surfaces alerts, deadlines, and Dutch email triage without being asked.
- **AI-to-human delivery** -- The entire docs server is purpose-built for delivering AI-generated artifacts to a real person on their phone -- at the grocery store, at the stove, on the morning commute.
- **Chat-first building** -- The workflow starts with a short conversation: the AI suggests meals, Dan approves or rejects until 3 good ones are selected. Then the AI generates everything downstream -- shopping lists, recipe walkthroughs, timers -- and publishes it all automatically. The CLAUDE-INSTRUCTIONS.md file is a meta-artifact: instructions for AI to produce future meal plans.
- **Builder identity** -- Real family use case, not a demo. Shopping lists localized to a specific Albert Heijn in Haarlem with Dutch product names. This is someone who handles the cooking and grocery runs some weeks and built a system to reduce the mental load.
- **Workflow automation** -- From a 3-minute conversation to a fully-published, mobile-ready app: recipe selection, shopping list generation organized by store layout, cook-mode walkthrough generation, and deployment to the docs server all happen without manual intervention after the initial approval loop.
- **Full-stack single-player** -- Python HTTP server, HTML/CSS/JS frontends, cross-platform path resolution, LaunchAgent scheduling, MEGA sync -- all built by one person with AI.

### Strongest Talking Points (pick 2-3)

1. **"A short conversation produces a complete, deployed app."** The meal planning workflow is a compelling demo of what AI-powered product building should feel like. I have a 3-minute conversation where the AI recommends recipes based on what my family has liked before. I approve or reject until we land on 3 good meals. Then the AI automatically generates a shopping list organized exactly how my grocery store is laid out, a cook-mode walkthrough with step tracking and built-in timers, and publishes everything to my family's HTML server -- all without me touching a file or running a deploy command. This is the pattern n8n's super-agent workstream is chasing: conversational input, automatic multi-step output.

2. **"The output quality is what makes it land."** The shopping list HTML files are 1000-line single-file applications with dark mode, progress tracking, timers with audio alerts, wake lock for cooking, per-recipe step tracking, and localStorage persistence. These aren't throwaway prototypes. I use the shopping list on my phone at Albert Heijn, checking off items as I walk the aisles. When I get home and cook, I switch to Cook Mode and follow the steps -- the timers ping when something needs attention, the screen stays on while I've got flour on my hands. The Spa Night list even has a "Spa Flow" tab that assigns tasks to assigned to different family members, with embedded timers. This demonstrates taste and attention to the end user.

3. **"The instruction file is the most interesting artifact."** CLAUDE-INSTRUCTIONS.md is a 21-line document that teaches AI how to produce future meal plans and publish them correctly. It encodes the publishing workflow (create HTML, save to correct directory, regenerate index, start server, verify). This is a micro-example of the "AI building AI tools" pattern that n8n's super-agent workstream is exploring.

### What to Highlight

- **The conversational-to-automatic pipeline.** This is the core story. The human effort is a short conversation (recommend, approve/reject, lock in 3 meals). Everything after that -- shopping list generation, store-layout organization, recipe walkthrough creation, timer embedding, server deployment -- is automatic. The ratio of human input to delivered output is extremely favorable.
- **The human angle.** This is someone who handles meal planning and grocery runs for his family and built a system to cut out the mental overhead. The fish sticks recipe is called "Your rescue night." The Spa Night list was a family project for his partner. This is relatable in a way that most AI portfolios aren't.
- **The infrastructure reuse.** The docs server serves meal plans, daily briefings, project documentation, and Blitzit task data. One HTTP server, one index generator, multiple AI-generated content types. This shows systems thinking.
- **The cross-platform story.** The docs system syncs via MEGA between Mac and Windows, resolves paths cross-platform, and serves over Tailscale. The meal plans are mobile-optimized with viewport locking and touch targets.
- **The overnight pipeline integration.** The docs server is the output layer for an automated daily briefing system that runs a local LLM (Qwen3.5-35B) at 5:30 AM, triages Dutch emails, syncs with Blitzit task management, and publishes HTML -- all without human intervention. The meal planning project plugs into the same infrastructure.

### What to Downplay

- **The docs server is not novel technology.** It's a Python SimpleHTTPRequestHandler with some API endpoints. Don't oversell the server itself -- sell the pattern of "AI generates, infrastructure delivers, humans consume."
- **No AI-in-the-loop at serving time.** The meal plans are generated once and served statically. There's no dynamic recommendation, no feedback loop, no personalization engine. The AI involvement is upstream (generation) not runtime.
- **The Blitzit integration complexity.** The convert_briefing.py file has elaborate Gmail thread ID matching, fuzzy title matching, and HTML entity unescaping for Dutch email triage. This is impressive engineering but tangential to the meal planning story -- only mention if asked about the broader system.

### Connection to n8n's Product

n8n's AI Product Builder role is about making AI agents that are useful to real people, not just technically impressive. The meal planning + docs server project demonstrates exactly this pattern:

- **Conversational input, automatic output.** The meal planning workflow mirrors what n8n wants its AI agents to do: take a brief human interaction (recipe selection) and turn it into a complete, deployed deliverable (shopping list + cook mode + published site) without manual steps.
- **Agent output, human consumption.** n8n workflows produce outputs. The question is how those outputs reach users. This project solves that for a family context.
- **Proactive delivery.** The overnight briefing pipeline runs without being asked and surfaces what matters. This is the "proactive suggestions" behavior n8n wants in its AI building workstream.
- **Builder as user.** Dan is both the builder and the primary user. He knows exactly where the friction is because he lives it. This maps to n8n's "builder track" philosophy.

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

I built a conversational AI pipeline where I approve 3 meal recommendations and the system automatically generates shopping lists organized by my grocery store's layout, step-by-step cooking walkthroughs with built-in timers, and publishes everything to a family docs server I use on my phone every week.

### The Problem

Some weeks I own meals and groceries for my family -- family in the Netherlands. Meal planning is a deceptively heavy cognitive task: figuring out what to cook based on what's worked before, building a shopping list, navigating a Dutch supermarket efficiently, and then actually cooking everything with family life happening in the background. I also needed a general-purpose way to get AI-generated outputs -- not just meal plans, but daily briefings, email triage, and task summaries -- onto my phone without requiring a terminal.

### My Role

Solo builder. I designed the system, built the infrastructure, generated the content, and I'm the primary user. My family members are end users of specific outputs (the Spa Night list was a family project). I used Claude Code as my building partner throughout -- every HTML file, every Python script, every CSS animation was produced through AI-assisted development.

### The Approach

The key insight was that meal planning has a natural conversation-to-output structure. I know my family's preferences. The AI knows recipes. The interesting part isn't a fancy UI -- it's the pipeline from a short planning conversation to a fully-deployed, mobile-ready app.

The workflow:
1. **Conversational planning.** I start a Claude session. The AI recommends recipes based on past family successes -- what the family actually liked, what was easy enough for a weeknight, what worked well as leftovers.
2. **Approve/reject loop.** I approve or reject suggestions until we land on 3 meals that feel right for the week.
3. **Automatic generation.** The AI generates a complete shopping list organized by how my specific grocery store (Albert Heijn) is laid out -- produce first, then meat, dairy, pasta aisle, freezer section, spices. Each item is tagged to its recipe.
4. **Automatic deployment.** The generated HTML file is saved to the docs server directory, the index is regenerated, and the server starts. I open `http://laptop:4444` on my phone and I'm ready to shop.

Rather than building a dedicated meal planning app, I built a lightweight documentation server that could serve any AI-generated HTML -- then pointed my meal planning workflow at it. One infrastructure, many content types.

The key design decisions:
- **Single-file HTML apps.** Each meal plan is a self-contained HTML file with no dependencies. It works offline, on any device, with no build step. This means AI can generate a complete, working application in one shot.
- **Mobile-first UX with real cooking features.** Dark mode, progress tracking with checkable items, countdown timers with audio alerts and vibration, screen wake lock (so your phone doesn't sleep while you're cooking), and per-recipe step tracking with localStorage persistence.
- **Store-layout-aware shopping lists.** Items are organized by grocery store section, not by recipe. You walk the store once, checking items off in order, instead of zigzagging between aisles.
- **Reusable publishing pipeline.** The same `generate_project_index.py` that indexes technical documentation also indexes meal plans. The same HTTP server that serves daily briefings also serves shopping lists. One infrastructure, many content types.
- **AI-reproducible workflow.** CLAUDE-INSTRUCTIONS.md encodes the full publishing process so any future Claude session can produce a new meal plan and deploy it without me re-explaining the system.

### What I Built

**Meal Planning App (x2 so far):**
- Weekly shopping list with checkable progress tracking, organized by supermarket aisle (Groente & Fruit, Vlees & Vis, Diepvries, etc.), with Dutch product names and English translations
- Color-coded recipe tags so you know which items go with which meal
- Cook Mode with step-by-step instructions, ingredient lists, and countdown timers
- Audio alerts (Web Audio API oscillator tones) and vibration when timers complete
- Screen wake lock toggle -- keeps your phone awake while you're cooking with dirty hands
- Per-recipe step tracking that persists across browser sessions via localStorage
- "Spa Night" variant with Shopping, Prep, and Spa Flow tabs -- assigns tasks to different family members, with embedded timers for foot soaks, face masks, and massages. Built as a family surprise.

**Shared Docs Server:**
- Python HTTP server (port 4444) with `/api/regenerate` endpoint for one-click content refresh
- Auto-discovery index generator that scans HTML files, reads `<title>` tags, categorizes by directory and keywords, and sorts by timestamp
- Cross-platform path resolution (Mac to Windows via MEGA sync)
- Tailscale-accessible for remote viewing on any device
- Serves multiple content types: meal plans, daily briefings (from overnight LLM pipeline), project documentation, Blitzit task data
- Blitzit task completion API -- briefings have interactive checkboxes that mark tasks complete in the task management system

**Publishing Skill:**
- SKILL.md documentation that teaches Claude Code sessions how to use the docs system
- CLAUDE-INSTRUCTIONS.md for meal-plan-specific publishing workflow
- Regeneration scripts per project with centralized metadata.json configuration

### The Result

Before grocery runs, I open `http://laptop:4444` on my phone. The shopping list is organized by store section, so I walk Albert Heijn once from produce through freezer, checking items off as I go. When I get home and it's time to cook, I switch to Cook Mode and follow the steps. The timers ping when something needs attention. The screen stays on while I'm wrist-deep in meat sauce.

The entire process from "what should we eat this week" to "shopping list on my phone" takes about 3 minutes of conversation. The AI handles the rest -- recipe details, ingredient quantities, store-section organization, HTML generation, server deployment.

I open the same URL every morning and see my daily briefing -- alerts about overdue Dutch bills, school deadlines, and email summaries -- generated overnight by a local LLM without me lifting a finger.

The system has been in daily use since April 2026. It serves 6+ content types across 2 machines, accessible on any device via Tailscale.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| AI generation | Claude Code (Opus), local Qwen3.5-35B via LM Studio |
| Frontend | Vanilla HTML/CSS/JS, single-file apps, localStorage, Web Audio API, Wake Lock API |
| Server | Python 3, http.server, custom API endpoints |
| Publishing | Auto-discovery index generators, markdown-to-HTML converter, Mermaid diagram support |
| Sync | MEGA cloud sync (cross-platform), Tailscale (remote access) |
| Task management | Blitzit MCP integration, Gmail thread ID matching |
| Scheduling | macOS LaunchAgent (5:30 AM overnight pipeline) |
| Orchestration | MARVIN (Claude Code-based AI chief of staff) |
