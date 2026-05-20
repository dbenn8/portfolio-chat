# Burrfect Water -- AI Builder Summary

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Relevance Scores

| Workstream | Score (1-10) | Rationale |
|---|---|---|
| **AI Building / Super Agent** | 6 | A deterministic math engine -- no LLMs, no ML models -- but it solves a genuinely hard constraint-satisfaction problem (linear dilution math across 10+ water parameters to find optimal tap-to-distilled ratios). The architecture is explicitly designed to be LLM-safe: compute everything deterministically first, then optionally feed results to an LLM for natural-language summary. This is the "AI trust" approach to building AI features -- keep the math auditable, use AI only for presentation. The map + data pipeline covers 40+ European cities with zone-level granularity. |
| **AI Trust** | 7 | The core design philosophy IS trust: "ALL math is done here in Python -- no LLM calls, no hallucination risk." The engine computes constraint intersections mathematically, generates deterministic recommendations with full audit trails (binding constraints, post-dilution values, effort levels), and provides grocery-store-accessible mineral recipes with safety warnings. The deploy pipeline has verification steps that validate city counts and data integrity. |

### Keywords Hit

- Proactive suggestions (city-specific water recommendations pushed to users)
- Guardrails (safety warnings on mineral additives, food-grade requirements, chloride caps)
- Reliability (deterministic math, no hallucination risk, verification pipeline)
- Human-in-the-loop (zone-level data gathered from government water quality reports, manually verified)

### Strongest Talking Points

1. **"I designed a hybrid architecture: deterministic math engine for the computation, LLM-optional for natural language. The math is always auditable."** This shows understanding that AI trust means keeping the critical path deterministic and only using AI where it adds value without introducing risk. This is the exact mindset needed for n8n's AI Trust workstream.

2. **"I built a data pipeline that covers 40+ European cities at zone-level granularity, with recommendations computed from SCA standards and constraint intersection math."** This is a real data product -- not a demo. Gathering water quality data from government reports across dozens of cities, normalizing it, computing recommendations, and deploying as an interactive map.

### What to Highlight

- The architecture decision to keep AI out of the critical path (deterministic engine) while making results AI-consumable
- The constraint-satisfaction approach: 10+ water parameters, each with SCA ideal ranges, linear dilution math, and binding constraint identification
- The multi-tier recommendation system: "use tap directly", "filter only", "dilute then use", "dilute then supplement", "build from scratch"
- The deploy pipeline that regenerates recommendations and rebuilds the interactive Leaflet map

### What to Downplay

- No actual LLM integration yet (the architecture supports it but it's not implemented)
- This is a side feature, not the core product

### Connection to n8n's Product

- **Trust-first AI architecture:** Computing deterministic results first, then optionally using AI for presentation, is the pattern n8n needs for reliable AI workflows
- **Data pipeline engineering:** Gathering, normalizing, and computing from heterogeneous data sources (analogous to n8n's data transformation capabilities)
- **Constraint satisfaction:** The dilution math is a constraint optimization problem -- the same class of problems that arise in AI agent planning and tool selection

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

"I built a deterministic water quality recommendation engine for 40+ European cities that tells espresso enthusiasts exactly how to optimize their tap water -- using constraint-satisfaction math, not LLMs."

### The Problem

Water is 98% of espresso by weight, and its mineral composition dramatically affects extraction and taste. The Specialty Coffee Association publishes ideal ranges for TDS, hardness, alkalinity, pH, and other parameters -- but tap water varies wildly by city and even by neighborhood. A user in Amsterdam gets different water than a user in Berlin. No existing tool could give city-specific, actionable water recommendations.

### My Role

Solo builder. Designed the recommendation engine algorithm, built the data pipeline for gathering city-level water quality data, created the interactive map, and integrated it into the Burrfect ecosystem.

### The Approach

The key insight was that dilution math is linear: `mixed_value = tap_value * f`, where `f` is the fraction of tap water. This means finding the optimal dilution ratio is a constraint intersection problem: find the range of `f` where ALL parameters simultaneously fall within SCA ideal ranges.

I deliberately chose NOT to use an LLM for the computation:
- Water chemistry is pure math -- LLMs add hallucination risk with no benefit
- Recommendations need to be reproducible and auditable
- Safety is critical (mineral additives need food-grade warnings)
- The engine outputs structured JSON that CAN be fed to an LLM for natural-language summaries if desired

### What I Built

**Recommendation Engine** (`water_recommendations_engine.py`):
- SCA ideal ranges for 10 parameters (TDS, pH, total hardness, alkalinity, chlorine, calcium, magnesium, sodium, chloride, sulfate)
- Linear constraint intersection: computes the feasible dilution range where all dilutable parameters are in-range simultaneously
- Identifies binding constraints (which parameter limits the ratio from above/below)
- 5-tier recommendation system: use tap directly, filter only, dilute then use, dilute then supplement, build from scratch
- Grocery-store mineral recipes with kitchen measurements (baking soda, food-grade Epsom salt, calcium chloride) with per-milligram-per-liter contribution factors
- Safety warnings (food-grade requirements, chloride caps, sodium limits)
- SCA scoring per parameter and overall

**Data Pipeline** (`burrfect_data.json`, `json_recommender.py`, `water_loader.py`):
- 40+ European cities with zone-level water quality data
- Sources: government water quality reports (PDFs), utility company websites
- JSON as single source of truth (replaced earlier SQLite approach for simplicity)
- Recommender reads JSON, computes all recommendations, writes back

**Interactive Map** (`build_map.py` -> `burrfect-water-map.html`):
- Leaflet.js map with city markers color-coded by SCA score
- Click a city to see full water quality profile, recommendation tier, dilution ratio, mineral supplement instructions
- Single self-contained HTML file (all CSS, JS, data inlined) for easy WordPress embedding
- WordPress plugin architecture designed (`DEPLOY-WORDPRESS.md`)

**Deploy Pipeline** (`deploy.sh`):
- 4-step verified pipeline: check data -> regenerate recommendations -> rebuild map -> verify output
- Validates city counts, HTML integrity, data completeness
- Designed for Claude Code Cowork sessions (handles session directory mounts)

### The Result

- 40+ European cities with zone-level water quality data and personalized recommendations
- Deterministic engine that produces reproducible, auditable results
- Interactive map deployable as WordPress plugin or standalone HTML
- Architecture designed for LLM integration (structured JSON output -> natural language summary) without trusting LLMs for the math

### Tech Stack

- **Engine:** Python (pure stdlib + dataclasses, no ML dependencies)
- **Data format:** JSON (burrfect_data.json as single source of truth)
- **Map:** Leaflet.js, inline CSS/JS, self-contained HTML
- **Data sources:** European government water quality reports (PDFs), utility APIs
- **Deploy:** Bash pipeline with verification steps
- **Target deployment:** WordPress shortcode plugin via WPX.net
