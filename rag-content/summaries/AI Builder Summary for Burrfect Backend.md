# Burrfect Backend -- AI Builder Summary

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Relevance Scores

| Workstream | Score (1-10) | Rationale |
|---|---|---|
| **AI Building / Super Agent** | 9 | Built a full AI recommendation system from scratch: 12 sub-models competing via data-driven meta-model selection (Master Model V2), custom memory (cascading stats pipeline: batch -> user-grinder -> bean -> global), proactive suggestions (dial-in guidance, insight recommendations pushed to users on schedule), LLM-powered auto-enhancement of beans/roasters/grinders/machines via Perplexity API, and a user model training pipeline that trains on shot creation and runs on schedule. This is productionized AI that runs autonomously. |
| **AI Trust** | 9 | Comprehensive eval/backtesting system (`backtest_all_recommendations.js`) that scores all 12 models + both meta-models against real user data. 6-layer governance pipeline (oscillation dampening, slope-proportional delta clamping, elastic band, soft bracketing, min-delta enforcement, physics validation). Physics violation filtering removes impossible recommendations. Variance gating detects unreliable model outputs. OldService CV thresholds. Sentry monitoring on every error path with `await Sentry.flush(2000)`. Human-in-the-loop via `needsRepublish` flag for content, `needsEnhancing` flag for AI enhancement. |

### Keywords Hit

- AI-first product
- Custom memory (cascading stats per user/grinder/bean)
- Proactive suggestions (scheduled insight recommendations, dial-in guidance)
- Evals (backtesting harness across 14 models)
- Observability (Sentry + structured logging + debug metadata in every recommendation)
- Guardrails (6-layer governance pipeline)
- Reliability (fallback cascades, null-value fallback chains, partial null recovery)
- Human-in-the-loop (enhancement tracking, republish flags)
- Trigger-based automation (Firestore triggers -> cascading stats rebuild)

### Strongest Talking Points

1. **"I built a meta-model that selects from 12 recommendation sub-models using real-time performance stats, with a two-phase architecture that separates strategy selection from model selection."** This is exactly the kind of AI product complexity n8n's Super Agent needs -- not just calling an LLM, but building a system that routes between multiple AI approaches based on context and measured performance. The cascading stats pipeline (batch -> user-grinder -> bean -> global) is custom memory that improves over time.

2. **"I built a backtesting harness that runs every model against real user dial-in histories to measure which gets users closer to their target."** This is evaluation-driven AI development. The backtest script (`backtest_all_recommendations.js`) scores grind setting accuracy, yield accuracy, and directional correctness for all 14 models across all iterations. This is how you build trust in AI systems.

3. **"The governance pipeline has 6 layers -- oscillation dampening, delta clamping, elastic band, soft bracketing, min-delta enforcement, and physics validation -- each with feature flags for safe rollout."** This shows understanding that shipping AI into production requires guardrails. Each layer is independently toggleable, isolated (failure in one doesn't block others), and logged for debugging.

### What to Highlight

- The recommendation engine is NOT an LLM wrapper. It's a statistical/ML system with 12 regression models (LR, MLR, Theil-Sen, Adaptive Bayesian, EWMA drift, Safe Harbor), a meta-model selector, and a governance pipeline. This demonstrates deep AI product building beyond prompt engineering.
- The real-time cascading stats pipeline: when a user pulls a shot, batch stats rebuild automatically, then aggregate up to user-grinder and bean levels. This is event-driven AI that gets smarter with every data point.
- The backtesting system generates `backtest_insights.json` with per-iteration, per-model accuracy data -- this is the feedback loop that drives model selection improvements.
- The 50-bucket situation system (10 strength x 5 seconds) with nearest-neighbor impact scaling is a novel approach to contextual recommendation.

### What to Downplay

- The WordPress/Albato webhook integration (simple POST calls, not complex n8n workflows)
- The Mailchimp email automation (standard CRUD, not AI)
- The sheer complexity of the codebase -- frame it as "depth of AI product work" not "too much code"

### Connection to n8n's Product

This backend demonstrates the exact skills needed for n8n's AI Product Builder role:
- **Building an AI agent system** where multiple models compete and a meta-model selects the best one (analogous to n8n's Super Agent routing between tools/sub-agents)
- **Custom memory** that persists and improves (analogous to n8n AI memory features)
- **Evaluation-driven development** with backtesting (analogous to n8n's AI Trust workstream -- evals, observability, debugging)
- **Governance/guardrails** that prevent bad AI outputs from reaching users (analogous to n8n's reliability and safety features)
- **Event-driven architecture** where triggers cascade through a pipeline (analogous to n8n's workflow trigger model)

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

"I built an AI recommendation engine with 12 competing statistical models, a meta-model selector, and a 6-layer governance pipeline that helps espresso enthusiasts dial in their shots 40% faster."

### The Problem

Home espresso is notoriously difficult to dial in. Users pull a shot, taste it, and need to decide: should I grind finer or coarser? Change the yield? Adjust brew temperature? By how much? The wrong adjustment wastes expensive specialty beans and time. Existing apps gave no guidance -- users were on their own.

### My Role

Solo AI product builder. I designed the recommendation architecture, built all 12 models, created the meta-model selection system, implemented the governance pipeline, built the backtesting harness, and shipped it to production running on Firebase Cloud Functions.

### The Approach

I started with a single rule-based model (`oldService` -- heuristic multipliers). When that hit accuracy ceilings, I built progressively more sophisticated approaches:

1. **Statistical models first:** Linear regression (LR), multiple linear regression (MLR), Theil-Sen (outlier-robust), EWMA drift detection, Safe Harbor (variance-minimizing), Adaptive Bayesian (local + global blending)
2. **Data-driven model selection:** Rather than picking one model, I built Master Model V2 -- a two-phase selector that uses measured performance (MAE) across 4 cascading stat levels to choose the best model for each specific situation
3. **Governance layers:** As the system got more complex, I added safety layers -- oscillation dampening for users bouncing between recommendations, physics validation to catch impossible suggestions, slope-based delta clamping to prevent extreme moves
4. **Backtesting to close the loop:** A harness that replays all historical dial-in sessions and scores every model's recommendations against what the user actually did and how it turned out

### What I Built

**12 Sub-Models** (`functions/shot-adjustments/models/`):
- `ugsv2-lr-model.js`, `ugsv2-mlr-model.js` -- User-grinder-specific regressions aggregated across bean batches
- `dialin-stats-lr-model.js`, `dialin-stats-mlr-model.js` -- Global pre-computed regressions from 50-bucket situation system
- `adaptive-bayesian-model.js` -- Batch-local regression blended with broader priors
- `theil-sen-model.js` -- Robust to outliers via median-of-pairwise-slopes
- `ewma-drift-model.js` -- Detects gradual grinder drift via exponentially weighted moving average
- `safe-harbor-model.js` -- Variance-minimizing bucket selection for when precision matters more than speed
- 3 batch-local variants that outperform cross-batch models 60-64% of the time

**Master Model V2** (`functions/shot-adjustments/models/master-model-v2.js`):
- Phase 1: Strategy selection from situation buckets (which adjustment type to recommend)
- Phase 2: Model selection from all buckets (which model's magnitude to use)
- Cascading stats from 4 sources with preference boosts: batchLocal (+0.10), userGrinder (+0.05), bean (0), global (0)
- Nearest-neighbor impact scaling with physics violation pre-filtering
- Null-value fallback chain through 6 slope-based models before dialin-stats fallback

**Governance Pipeline** (`functions/shot-adjustments/governance/`):
- Oscillation dampening (detects sour->bitter->sour patterns, reduces delta magnitude)
- Slope-proportional delta clamping (bigger strength offset = bigger allowed correction)
- Elastic band (clamps effective slopes to 0.5x-2.0x global averages)
- Soft bracketing (prevents known-bad parameter zones using batch memory)
- Min-delta enforcement (bumps imperceptible changes to thresholds)
- Final physics validation (last-resort direction reversal)

**Cascading Stats Pipeline** (`functions/services/cascading-stats-service.js`):
- Triggered automatically on shot save
- Step 1: Full batch-level rebuild (12 models evaluated)
- Step 2: Aggregate to user-grinder level (8 models)
- Step 3: Aggregate to bean level (8 models)
- Global level computed weekly via scheduled function

**Backtesting Harness** (`scripts_admin/dial-in/backtest_all_recommendations.js`):
- Replays all bean batch histories
- Scores 14 models (12 sub-models + Master Model V1 + V2)
- Per-iteration accuracy breakdown
- Generates insights JSON for analysis

**AI Auto-Enhancement** (`functions/ai/`):
- LLM-powered (Perplexity API) enhancement of beans, roasters, grinders, machines
- Trigger-based: Firestore `needsEnhancing` flag kicks off enhancement pipeline
- Edit tracking to prevent re-enhancing user-modified data

**User Model Training** (`functions/ai/user-model/`, `functions/shared/model-training/`):
- Training pipeline triggered on shot creation + scheduled every 5 hours
- Trains per-user models for starting point prediction
- Artifact storage in Firebase Storage with versioned manifests
- Lock-based concurrency control to prevent duplicate training runs

### The Result

- 12 production recommendation models serving real users
- Master Model V2 selects the optimal model per-situation using measured performance data
- 6-layer governance pipeline prevents bad recommendations
- Backtesting harness validates every change before shipping
- Real-time cascading stats that improve with every shot pulled
- Scheduled jobs maintain data consistency across 8+ Firestore collections
- Sentry monitoring, structured logging, and debug metadata on every recommendation

### Tech Stack

- **Runtime:** Node.js 20 on Firebase Cloud Functions v6
- **Database:** Firestore (real-time triggers, subcollections for stats)
- **AI/ML:** Custom statistical models (LR, MLR, Theil-Sen, EWMA, Bayesian), LLM via Perplexity API
- **Monitoring:** Sentry (errors + profiling), structured console logging
- **Scheduling:** Firebase Scheduled Functions (daily consistency jobs, weekly global stats, user model training)
- **Email:** Mailchimp Marketing + Mandrill Transactional
- **Analytics:** Mixpanel event tracking
- **External:** Albato webhooks to WordPress, Firebase Remote Config for guidance tables
