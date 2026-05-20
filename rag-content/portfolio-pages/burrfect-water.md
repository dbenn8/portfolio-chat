## The Problem

Water is 90%+ of espresso by weight, and its mineral composition dramatically affects taste. The Specialty Coffee Association (SCA) publishes ideal ranges for 10 parameters (pH, hardness, alkalinity, TDS, calcium, magnesium, sodium, chloride, sulfate, bicarbonate), but most home brewers have no idea what's in their tap water or what to do about it.

Burrfect needed a tool that could tell users: "Here's your city's water quality. Here's how it scores against SCA standards. Here's exactly what to do — use it as-is, dilute with RO water at this ratio, add these minerals, or a hybrid approach." It had to work for 44+ European cities and be genuinely useful, not just informational.

## My Role

I designed the recommendation algorithm, gathered water quality data for all 44 cities (from municipal reports, water authority APIs, and direct research), built the constraint satisfaction engine, and shipped the interactive map. Solo project, 5 days from concept to deployment.

## The Approach

The key architectural decision was **deliberately avoiding LLMs for the critical computation path**. Water chemistry has precise, deterministic relationships — there's one correct answer for "what ratio of RO water brings your TDS from 380 to 150." An LLM would hallucinate plausible but wrong ratios. Instead, I built a constraint satisfaction engine in pure Python that solves across all 10 parameters simultaneously.

The system evaluates four possible strategies for each city: use tap water as-is, dilute with RO water, add minerals to RO water, or a hybrid (partial dilution + mineral addition). It picks the strategy that brings the most parameters into SCA range with the least intervention.

Data gathering was the harder problem. Municipal water reports are published in wildly different formats — some as PDFs, some as interactive maps, some as ArcGIS endpoints, some only available by emailing the water authority. I built a data pipeline that normalizes all sources into a consistent JSON format, then runs the recommendation engine across the full dataset.

## What I Built

- **Constraint satisfaction engine** — solves across 10 SCA parameters simultaneously, evaluates 4 strategies, picks the optimal one with minimal intervention
  - **Data pipeline** — normalizes water quality data from PDFs, APIs, GIS servers, and manual research into a consistent JSON schema
  - **Interactive map** — single-file HTML with city markers, color-coded by water quality, expandable panels showing all parameters and the specific recommendation
  - **Zone-level coverage** — some cities have multiple water zones with different sources; the system handles per-zone recommendations
  - **Scheduled monitoring** — a Claude Code scheduled task checks for updated data from city GIS servers (currently monitoring Dublin's Irish Water endpoint)
## The Result

44 European cities with complete water quality profiles and actionable recommendations. The tool tells you exactly what to do — not "your water might be too hard" but "dilute your tap water 60:40 with RO water, which brings TDS from 320 to 128 (target: 75–175) and hardness from 180 to 72 (target: 50–175)."

The trust-first architecture — deterministic math for the critical path, LLM-consumable output format — is a design pattern I keep coming back to. AI is great for research, data gathering, and presentation. But when there's a mathematically correct answer, you compute it; you don't ask a model to guess.

## Tech Stack

- **Engine:** Python (constraint satisfaction, SCA scoring, strategy evaluation)
  - **Data:** JSON database, ArcGIS API integration, PDF extraction pipeline
  - **Frontend:** Single-file interactive HTML map with embedded data
  - **Deployment:** Static hosting via Burrfect docs infrastructure
  - **Monitoring:** Claude Code scheduled task for GIS endpoint checks
  - **Research:** Claude for initial city data gathering, manual verification