# Burrfect Analytics -- AI Builder Summary

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Relevance Scores

| Workstream | Score (1-10) | Rationale |
|---|---|---|
| **AI Building / Super Agent** | 5 | Not an AI product itself, but the observability/measurement layer that validates AI product decisions. The dashboard measures the downstream impact of the backend's AI recommendation engine on user retention, activation, and conversion. The A/B testing page (`12_Test_Experiments.py`) with statistical significance testing is directly relevant to evaluating AI feature rollouts. |
| **AI Trust** | 8 | This IS the trust layer. PMF validation dashboard with 13 analysis pages that measure whether the AI-powered product actually works: cohort retention heatmaps, activation research (shot count breakpoints), onboarding funnel drop-off, natural frequency analysis, resurrection rates, power user curves, conversion funnels, and A/B experiment results with guardrail metrics. All backed by 20+ BigQuery views computing the metrics from raw GA4 and Firestore data. |

### Keywords Hit

- Observability (full analytics dashboard monitoring product health)
- Evals (A/B testing with statistical significance, guardrail metrics)
- Debugging (research pages for activation discovery, retention benchmarks)
- Human-in-the-loop (dashboard enables data-driven product decisions)
- Traces (user journey tracking from first touch through tier progression)
- Reliability measurement (retention cohorts, resurrection rates, churn detection)

### Strongest Talking Points

1. **"I built a 13-page PMF validation dashboard backed by 20+ BigQuery views to measure whether my AI features actually improve user outcomes."** This shows the mindset n8n needs: not just building AI, but measuring whether it works. The dashboard covers cohort retention, activation research, conversion, lifecycle tracking, and A/B experiments -- all the metrics needed to validate AI product decisions.

2. **"The A/B testing page auto-populates experiment results with funnel comparison, guardrail metrics, and statistical significance using scipy stats."** This is exactly how you ship AI features responsibly -- with proper experiment infrastructure that measures both the target metric and guardrail metrics to catch regressions.

3. **"I built activation discovery research that identified the shot-count breakpoints where users retain -- this drove the recommendation engine's design."** The analytics directly informed the AI system design. Research pages (`5_Activation_Research.py`) identify natural usage frequency, notification impact, and time-to-first-shot patterns.

### What to Highlight

- The full BigQuery analytics pipeline: raw GA4 events and Firestore exports -> 20+ SQL views (foundation, retention, tiers, conversion, attribution, experiments) -> Streamlit dashboard with Plotly visualizations
- PMF methodology breadth: bracket retention, usage density, L-ness ratios, power user curves, natural frequency CDF, resurrection rates, gap distributions, batch retention funnels
- Research-driven product development: the `research/` folder contains published findings (activation discovery, retention benchmarks, VC investor benchmarks, notification timing analysis)
- Deployed on Appliku with Tailscale remote access and password auth

### What to Downplay

- This is analytics, not AI -- frame it as "the measurement layer that validates AI decisions"
- The Streamlit framework choice (commodity tech) -- focus on the analytical methodology

### Connection to n8n's Product

This demonstrates the AI Trust mindset n8n needs:
- **Evals and observability** -- measuring whether AI features improve outcomes, not just shipping and hoping
- **A/B experiment infrastructure** -- the same framework needed to evaluate n8n AI feature rollouts
- **PMF validation** -- understanding whether an AI product delivers value (retention, activation, conversion)
- **Data pipeline engineering** -- BigQuery views that compute complex metrics from raw event data (analogous to n8n's data transformation workflows)

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

"I built a 13-page PMF validation dashboard that measures whether my AI recommendation engine actually improves user outcomes -- from cohort retention to activation breakpoints to A/B experiment significance."

### The Problem

I had an AI recommendation engine serving real users, but no way to measure whether it was working. App store ratings and support emails are lagging indicators. I needed real-time answers: Are users who get recommendations retaining better? What's the activation threshold? Is the new model version improving conversion? Without this, every AI change was a guess.

### My Role

Solo builder. Designed the analytics methodology, built the BigQuery view pipeline, created the Streamlit dashboard, and deployed it as a production internal tool.

### The Approach

Started with the question "how do I know if Burrfect is working?" and worked backward:

1. **Foundation layer:** Built identity bridge views that link Firebase Auth UIDs to GA4 events to Firestore user data. This is the unglamorous plumbing that makes everything else possible.
2. **Retention as the north star:** Weekly cohort retention heatmaps with weighted averages, benchmarked against niche utility apps and GA4 industry data. If retention is flat or improving, the AI is adding value.
3. **Activation research:** Identified the shot-count breakpoints where retention jumps (via `get_retention_by_shot_count`, `get_natural_breakpoints`). This directly informed the recommendation engine's "nudge at the right time" design.
4. **PMF deep dive:** Multiple methodologies (bracket retention, usage density, L-ness ratios, power user curves, natural frequency CDF, resurrection rates) to triangulate whether the product has product-market fit.
5. **Experiment infrastructure:** A/B testing page that auto-populates results with funnel comparison, guardrail metrics, and scipy statistical significance testing. Used for every AI model rollout.

### What I Built

**BigQuery Analytics Pipeline** (`bigquery/`):
- `burrfect_funnel_analytics` dataset with 20+ materialized views
- Foundation views: `v_user_first_touch`, `v_user_identity_bridge`, `v_user_activity_daily`
- Retention views: `v_retention_cohort_weekly`, `v_retention_ratios`, `v_retention_ga4_comparison`
- Tier views: `v_user_tier_current`, `v_user_tier_history`, `v_tier_distribution`, `v_tier_progression_rates`
- Conversion views: `v_conversion_by_tier`, `v_conversion_by_cohort`, `v_ltv_by_cohort`, `v_revenue_events`
- Experiment views: `v_experiment_enrollment`, `v_experiment_funnel`, `v_experiment_guardrails`
- Revenue dataset for subscription analytics

**Streamlit Dashboard** (`dashboard/`):
- 13 analysis pages covering the full PMF methodology stack
- `1_Cohort_Retention.py` -- Weekly cohort heatmaps with benchmark bands
- `2_Engagement_Trends.py` -- DAU/WAU/MAU trends
- `5_Activation_Research.py` -- Shot-count breakpoints, notification impact, time-to-first-shot
- `7_Conversion.py` -- Tier conversion rates, LTV by cohort, subscription status
- `9_Onboarding_Funnel.py` -- Step-by-step drop-off analysis with user path visualization
- `10_PMF_Deep_Dive.py` -- Multi-methodology analysis (bracket retention, usage density, natural frequency, resurrection rates, gap distributions)
- `11_User_Lifecycle.py` -- Firestore-sourced journey tracking through milestones
- `12_Test_Experiments.py` -- A/B test results with statistical significance (chi-squared, proportion z-tests)

**Research Output** (`dashboard/research/`):
- Activation discovery findings
- Retention benchmarks (niche utility, GA4 industry)
- VC investor benchmarks for comparison
- Notification permission timing analysis

**Reusable Components** (`dashboard/components/`):
- Cohort heatmap with color-coded retention rates
- Benchmark bands (amber/green/elite) for KPI cards
- Marketing event annotations on time-series charts
- Date range selector with sensible defaults

### The Result

- Live dashboard at a custom URL (Appliku deployment + Tailscale access)
- 13 analysis pages covering retention, activation, conversion, lifecycle, and experiments
- 20+ BigQuery views computing metrics from 2 data sources (GA4 events + Firestore exports)
- Research findings that directly drove AI recommendation engine design
- A/B experiment infrastructure used for every model version rollout
- Password-protected with bcrypt authentication

### Tech Stack

- **Dashboard:** Streamlit (Python), Plotly for interactive charts, Pandas for data manipulation
- **Data warehouse:** Google BigQuery with 20+ SQL views across 6 analytical domains
- **Statistics:** scipy.stats for A/B test significance testing
- **Data sources:** GA4 analytics events, Firestore document exports
- **Deployment:** Appliku (Docker), Tailscale for remote access
- **Auth:** bcrypt password hashing
