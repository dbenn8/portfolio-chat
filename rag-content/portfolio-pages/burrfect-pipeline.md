## The Problem

Burrfect's recommendation engine needs rich data about coffee roasters and beans — tasting notes, origins, roast profiles, roaster websites, country of operation — but manually researching and entering that data doesn't scale. We had hundreds of roasters and thousands of beans in the database with minimal metadata. The recommendation engine was starving for context.

The challenge: no single AI provider could do what I needed. I needed web search (to find roaster websites, verify data, discover bean details) AND structured JSON extraction (to reliably populate our database schema). In late 2023, Perplexity could search but couldn't return structured output. OpenAI could return structured JSON but couldn't search the web. Neither was sufficient alone.

## My Role

I designed and built the AI enhancement pipeline end-to-end — from the original Google Apps Script prototype through the production Cloud Functions implementation. I also built the eval/testing harness for regression testing model upgrades. My cofounder and our contractor built the mobile app and most of the backend; the AI enhancement system is specifically my contribution.

## The Approach

### Phase 1: Prototype on Google Apps Script

I started where I could iterate fastest: Google Apps Script with Google Sheets as the UI. The pipeline chains two API calls for each enhancement:

- **Perplexity AI** — searches the web for the roaster/bean, returns unstructured research results
  - **OpenAI** — takes the Perplexity research and extracts structured JSON matching our Firestore schema
This two-provider pattern worked remarkably well. Perplexity found the data; OpenAI structured it. I validated output against our schema before touching the database. The goal wasn't production code — it was proving the data quality was good enough to trust.

### Phase 2: Migration to Cloud Functions

Once the logic was validated, the pipeline moved to Firebase Cloud Functions (with my PRD as specification). This introduced real engineering challenges:

- **Cold start management:** Cloud Functions spin down between invocations. Each enhancement needs two sequential API calls, and the function needs to stay warm for both.
  - **Roaster-before-beans dependency chain:** Search quality for beans depends heavily on having correct roaster data (country, proper name, website). The pipeline must fully enhance a roaster before starting on any of its beans. This is tracked via a `_enhancement_tracking_` collection in Firestore.
  - **Rate limiting and retry:** Both Perplexity and OpenAI have rate limits. The pipeline manages backoff and retry across potentially dozens of sequential enhancements.
### Phase 3: The Eval Harness

When a new model version drops (GPT-4 → GPT-4 Turbo → GPT-4o, or Perplexity model upgrades), I need to know: does this help or hurt our results? I built a regression testing harness that:

- Runs the new model against a body of 20+ known-good records
  - Compares output to the verified ground truth using fuzzy matching
  - Classifies differences by severity (critical = wrong country/name, minor = slightly different description phrasing)
  - Reports a pass/fail with specific examples of regressions
This means I can upgrade models with confidence — I measure before I trust.

## What I Built

- **Two-provider AI pipeline** — Perplexity for search + OpenAI for structured extraction, before either had native support for the other's strength
  - **Google Apps Script prototype** — zero-infrastructure iteration environment with Sheets as UI
  - **Production Cloud Functions** — cold start management, dependency chain orchestration, rate limiting
  - **Enhancement tracking system** — Firestore collection managing roaster→bean sequencing
  - **Eval/regression testing harness** — 20+ record test body, fuzzy matching, severity classification
  - **Growth loop** — enhanced data flows to WordPress via Albato webhooks, creating SEO-discoverable content that drives app installs
## The Result

Hundreds of roasters and thousands of beans enriched with structured, verified data. The recommendation engine went from "we have a bean name and nothing else" to having origin, process, tasting notes, roast profile, roaster country, and website — all sourced from the web and validated against our schema.

The eval harness has caught multiple regressions during model upgrades that would have degraded data quality if shipped blindly. The "measure before you trust" principle turned out to be the most important thing I built.

## What I Built vs. What the Team Built

Honesty matters: I didn't build most of Burrfect. My cofounder built the Flutter mobile app. Our contractor built the Firebase backend, the recommendation engine (12 models), and the shot tracking system. I PM'd the recommendation engine extensively but didn't write its code.

What I *did* build: the AI enhancement pipeline (both GAS and Cloud Functions versions), the eval harness, the analytics dashboard (Streamlit + BigQuery), the water quality map, and the Albato/WordPress growth loop. These are my direct contributions — systems I designed, prototyped, and shipped.

## Tech Stack

- **AI:** Perplexity AI (web search), OpenAI (structured extraction), Claude (eval analysis)
  - **Prototype:** Google Apps Script, Google Sheets
  - **Production:** Firebase Cloud Functions (Node.js), Firestore
  - **Eval:** Custom testing harness (Node.js), fuzzy matching, severity classification
  - **Integration:** Albato (webhooks), WordPress REST API
  - **Monitoring:** Sentry, Mixpanel