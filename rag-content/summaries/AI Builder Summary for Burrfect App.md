# AI Builder Summary for Burrfect App

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Workstream Relevance Scores

**AI Building / Super Agent: 7/10**
- The app's backend recommendation engine is an AI-first product feature: a Cloud Function generates personalized espresso dial-in recommendations (grind setting, yield, brew temperature, dose) based on shot history and equipment context. This is not a simple rules engine -- it calls `devRecommendations` / `recommendations` Firebase Cloud Functions that analyze shot balance (extraction strength, pull quality, offsets) to produce multi-parameter suggestions with debug info and "why this" explanations.
- AI-powered "Enhancement" pipeline: when users add beans, roasters, grinders, or machines, a Firestore-triggered Cloud Function auto-enriches the catalog entry using AI. The `EnhancementNotifier` tracks enhancement status (`pending` -> done) via real-time Firestore listeners.
- Insights ranking algorithm uses a weighted scoring formula: `(0.6 x relevance) + (0.25 x popularity) + (0.15 x recency)` to deliver a personalized feed. This is a lightweight but real recommendation system.
- Auto-timer feature uses MFCC (Mel-Frequency Cepstral Coefficients) audio signal processing to detect espresso machine pump sounds, calibrate against background noise using Median Absolute Deviation, and automatically time shot extraction. This is real-time ML/DSP running on-device.
- Starting Point system calls a cloud function that uses a pro/free model tiering to predict optimal starting parameters for new bean bags, adapting grind settings across different grinder configurations using relative grind settings (RGS).

**AI Trust: 5/10**
- The app has real observability: Sentry for error tracking (with 100% traces and profiles sample rate), Mixpanel for product analytics, Firebase Analytics for event tracking, and Firebase Crashlytics for crash reporting.
- Experiment assignments are logged as super properties on every event, enabling proper A/B test attribution.
- Recommendation quality has a human-in-the-loop feedback mechanism: the "Something seems off? Report it" button on the Dial In Coach screen sends full debug context (recommendation state, guidance state, shot context, debug info from the algorithm) to a feedback review pipeline.
- Debug info from the recommendation engine is surfaced in-app via `DebugInfoSheet` -- the team can inspect exactly why a recommendation was made.
- However, there is no formal eval harness, no automated regression testing of recommendation quality, and no systematic guardrails beyond the feedback loop.

### Keywords Hit

| Keyword | Evidence |
|---------|----------|
| **Builder track record** | Solo-built a cross-platform mobile app (Flutter, iOS+Android) at version 2.0.1 with 158 builds. Full-stack: client + Firebase Cloud Functions backend + AI recommendation engine + audio DSP. |
| **AI-native product** | Recommendation engine, AI catalog enhancement, MFCC-based auto-timer, ranked insights feed, starting point prediction. AI is not bolted on -- it is the core value proposition. |
| **Eval practice** | A/B testing framework with `ExperimentRegistry`, `ExperimentDefinition`, variant funnels, primary metrics, and Mixpanel super property attribution. Three live experiments: onboarding survey, home stats grid, post-signup beans flow. |
| **Product instincts** | PRD-driven development (PRD-Insights.md), clear success metrics (25% DAU engagement, 5% shot-to-insight conversion), freemium/pro tiering with token-based metering. |
| **UX taste** | Card-stack shuffle animation in Dial In Coach, extraction meter visualization, skeleton loading states, haptic feedback on interactions, dark/light theme with custom Commissioner/Inter typography. |
| **Ambiguity comfort** | Building in a niche domain (home espresso) with no playbook. Invented the RGS (Relative Grind Setting) abstraction to make recommendations portable across 100+ different grinder models. |
| **Workflow automation** | Firebase Cloud Functions triggered by Firestore writes, enhancement pipeline that auto-enriches catalog data, push notification system for insights delivery. |
| **Coding background** | Deep: Flutter/Dart frontend, Node.js Cloud Functions, Firestore data modeling, real-time audio processing with MFCC/FFT, RevenueCat subscription management, Algolia search. |

### Strongest Talking Points for Interview

1. **"I built an AI recommendation engine that understands physical equipment constraints."** The Relative Grind Setting system translates recommendations across different grinder models by normalizing to a 0-1 scale. When a user switches grinders, the system adapts grind settings using the new grinder's calibrated range. This is the kind of real-world constraint that makes AI products hard -- you cannot just output a number; it has to map to the specific clicks and marks on someone's physical grinder.

2. **"I run real A/B tests on a live product with defined funnels and primary metrics."** The `ExperimentRegistry` defines experiments with per-variant screen funnels, event tracking, and primary metrics (e.g., `account_created`, `shot_pulled`, `bean_added`). Every analytics event carries experiment assignments as super properties. This is not theoretical -- it is the same eval-driven iteration loop that n8n needs for AI features.

3. **"I built an audio ML feature that detects espresso extraction in real-time."** The auto-timer uses MFCC audio fingerprinting with background noise calibration (Median Absolute Deviation), configurable thresholds via Firebase Remote Config, and a state machine (idle -> calibration -> listening -> analyzing -> in_progress -> completed). Every parameter is remotely tunable. This shows comfort building AI features where the signal is noisy and the feedback loop is physical.

### What to Highlight

- **AI as core product, not a feature.** Every major user flow (starting a new bean bag, dialing in, getting recommendations, browsing insights) touches an AI/ML system. This is rare for a solo builder.
- **Remote Config everything.** Feature flags, experiment variants, auto-timer thresholds, paywall copy -- all remotely configurable. Shows understanding that AI products need continuous tuning without app releases.
- **Full-stack ownership.** One person built the Flutter app, the Firebase backend, the recommendation engine, the audio DSP, the A/B testing framework, the analytics pipeline, and the insights ranking algorithm. At n8n this translates to: can own a feature end-to-end.
- **Pro/free token metering.** Both Starting Points and Dial In Coach use a token system where free users get limited AI recommendations. This shows understanding of how to monetize AI features while keeping the free tier useful.

### What to Downplay or Skip

- **Espresso domain specifics.** The interviewer does not care about MFCC coefficients or extraction theory. Frame everything as "domain-specific AI" and focus on the product patterns.
- **Flutter/Dart technology choice.** n8n is a TypeScript/Vue.js stack. Emphasize the problem-solving and product thinking, not the specific framework.
- **The fact that the recommendation engine runs in Cloud Functions, not in a sophisticated ML pipeline.** The product impact matters more than the infrastructure sophistication.
- **Audio processing details.** Mention it as "on-device ML for real-time detection" but do not go deep into DSP unless asked.

### Connection to n8n's Product

- **Recommendations = Agent actions.** The Dial In Coach is essentially a domain-specific agent: it takes context (shot balance, equipment, history), calls a backend "skill" (Cloud Function), presents options to the user, lets them accept/reject/tweak, and applies the result. This is the same pattern n8n's AI agents use: context -> tool call -> user review -> action.
- **Insights feed = curated AI content delivery.** The ranked insights feed with relevance scoring, topic filtering, daily drip, and pro content gating is analogous to how n8n might deliver AI-generated workflow suggestions or community templates.
- **A/B testing framework = eval infrastructure.** The experiment system with variant funnels and primary metrics is a lightweight version of what n8n needs to evaluate AI feature quality.
- **Enhancement pipeline = workflow automation.** The Firestore-triggered AI enhancement of catalog entries is literally a workflow automation pattern: document created -> trigger function -> call AI -> write result back. This could be an n8n workflow.
- **Token-based AI metering = usage-based pricing.** The free/pro token system for AI features maps directly to n8n's cloud pricing model.

---

## Part 2: Portfolio Case Study Draft

### One-line Hook

An AI-powered espresso companion that uses audio signal processing, personalized recommendation algorithms, and A/B-tested onboarding to help home baristas dial in their shots -- built solo from zero to a live product on iOS and Android.

### The Problem

Home espresso is a hobby with a brutally steep learning curve. A typical home barista spends $2,000-5,000 on a machine and grinder, pulls their first shot, and gets something that tastes nothing like what they had at the cafe. The variables are overwhelming: grind setting (which differs across 100+ grinder models), dose, yield, brew temperature, pre-infusion, shot time, and bean freshness. Most people cannot even articulate what went wrong -- they just know it does not taste right.

Existing tools in this space are either shot loggers (spreadsheets with a pretty UI) or generic recipe databases. Neither solves the core problem: when your shot tastes sour and fast, what specifically should you change on YOUR grinder, with YOUR beans, given YOUR last three shots? The answer depends on equipment context, extraction physics, and personal taste -- and it changes every time you open a new bag of beans.

The deeper retention problem is that users who cannot improve stop pulling shots. They drift away from the hobby and the app. The difference between a churned user and a retained one is whether Burrfect can get them from "this tastes bad" to "I know what to adjust" in the first few sessions.

### My Role

Solo product builder: I designed, built, and shipped the entire product -- mobile app (Flutter/Dart, iOS + Android), Firebase Cloud Functions backend (Node.js), recommendation engine, audio processing pipeline, A/B testing framework, analytics instrumentation, and RevenueCat subscription integration. I also wrote the PRDs, defined success metrics, ran experiments, and iterated based on data.

### The Approach

**Starting with the recommendation engine, not the UI.** The first thing I built was the "Dial In Coach" -- a Cloud Function that takes a shot's parameters and balance assessment and returns specific recommendations. The key insight was that recommendations need to be multi-parameter ("grind 2 clicks finer AND reduce yield to 34g") because espresso variables are interdependent. I built a card-stack UI where users can cycle through options, accept one, or tweak the values before committing. This meant the AI suggestions are starting points, not dictates -- preserving user agency while reducing the decision space.

**Inventing the Relative Grind Setting (RGS) abstraction.** The hardest engineering problem was making recommendations portable across grinder models. A "grind finer" recommendation means different things on a Niche Zero vs. a Comandante vs. a DF64. I built a normalization layer that maps any grinder's setting to a 0-1 scale based on the user's calibrated fine/coarse range. When the recommendation engine outputs an RGS, the client translates it to the user's specific grinder's scale. This also enabled the Starting Point feature: when a user opens a new bag of beans, the system finds similar shots from the community and adapts the grind settings to the user's equipment.

**Building audio-based shot detection.** To remove the friction of manually timing shots, I built an auto-timer that listens for the espresso machine's pump sound. It uses MFCC (Mel-Frequency Cepstral Coefficients) audio analysis with a state machine: background noise calibration (3 seconds of Median Absolute Deviation analysis) -> pattern detection -> shot in progress -> pump-off detection. Every threshold (consistency ratio, absolute minimum, MAD scale factor, buffer durations) is remotely configurable via Firebase Remote Config, because the optimal values differ across machine types and home environments.

**Running experiments from day one.** I built an A/B testing framework into the app's initialization flow. Experiments are defined in a typed registry with per-variant screen funnels and primary metrics. Mixpanel carries experiment assignments as super properties on every event, so any metric can be sliced by variant. The three active experiments test onboarding survey placement, home screen stats grid visibility, and post-signup bean-adding flows -- each with clear primary metrics (account creation rate, shot pull rate, bean addition rate).

### What I Built

- **Dial In Coach** -- AI-powered recommendation screen with card-stack UI, extraction meter visualization, multi-parameter suggestions (grind + yield + temperature), user edit capabilities, and a "Something seems off?" feedback loop with full debug context
- **Starting Point Engine** -- Cloud Function that predicts optimal starting parameters for new bean bags, with pro/free model tiering, local caching, and cross-grinder adaptation via RGS
- **Auto-Timer** -- On-device audio processing using MFCC analysis to detect espresso extraction start/stop, with background noise calibration and remotely tunable thresholds
- **Insights Feed** -- Ranked content discovery feed with personalized scoring (relevance + popularity + recency), system insight daily drip, community-contributed insights from shot notes, topic filtering, pro content gating with weekly preview, and push notifications
- **AI Enhancement Pipeline** -- Firestore-triggered Cloud Functions that auto-enrich beans, roasters, machines, and grinders when users add them
- **A/B Testing Framework** -- Typed experiment registry, Firebase Remote Config integration, per-variant funnel definitions, Mixpanel super property attribution, and widget/function/value split test helpers
- **Subscription System** -- RevenueCat integration with token-based AI feature metering, soft trial paywall, and remotely configurable paywall copy/features via Firebase Remote Config
- **Shot Tracking Core** -- Full shot lifecycle (plan -> pull -> rate -> recommend), bean batch management, equipment profiles with grinder calibration, and shot-to-insight linking
- **Analytics Pipeline** -- Dual Mixpanel + Firebase Analytics instrumentation, experiment-aware event logging, debounced screen tracking with Firestore progress writes, and Sentry error monitoring with 100% trace sampling
- **Onboarding Flow** -- Multi-step account creation with goal survey, equipment setup, bean addition, and shot time picker -- all A/B testable

### The Result

The product is live on iOS and Android at version 2.0.1 (158 builds), with a complete feature set that spans shot tracking, AI recommendations, audio-based timing, a content discovery feed, and a subscription model. The architecture supports rapid iteration: every AI threshold, paywall parameter, onboarding copy, and feature flag is remotely configurable without an app release.

The technical achievement that I am most proud of is the Relative Grind Setting system. It solves a problem that no other espresso app has tackled: making recommendations meaningful across the long tail of grinder hardware. A recommendation that says "grind finer" is useless. A recommendation that says "move from 2.4 to 2.1 on your DF64" is actionable. RGS makes the second one possible even when the training data came from users with completely different grinders.

The product architecture also demonstrates patterns directly relevant to AI agent building: the Dial In Coach is a human-in-the-loop agent (context -> tool call -> present options -> user accepts/tweaks -> apply), the Enhancement Pipeline is a trigger-based automation workflow, and the Insights Feed is a personalized content ranking system. All of these are patterns that appear in workflow automation and AI agent platforms.

### Tech Stack

**Mobile App**
- Flutter 3.x / Dart (iOS + Android)
- Riverpod + GetX for state management
- Freezed for immutable data models
- Lottie for animations

**Backend & Data**
- Firebase Cloud Functions (Node.js)
- Cloud Firestore (real-time database)
- Firebase Auth
- Firebase Remote Config (feature flags, experiments, thresholds)
- Firebase Crashlytics
- Firebase Cloud Messaging (push notifications)
- Algolia (search)

**AI / ML**
- Custom recommendation engine (Cloud Functions)
- MFCC audio processing (flutter_sound + flutter_sound_processing + aubio)
- Insights ranking algorithm (weighted multi-factor scoring)
- AI catalog enhancement pipeline (Firestore-triggered)

**Analytics & Observability**
- Mixpanel (product analytics, experiment attribution)
- Firebase Analytics (event tracking, screen views)
- Sentry (error tracking, performance monitoring, 100% trace sampling)

**Monetization**
- RevenueCat (subscriptions, in-app purchases)
- Google Mobile Ads (banner ads for free tier)
- Token-based AI feature metering

**Experimentation**
- Custom A/B testing framework
- Firebase Remote Config (variant assignment)
- Typed experiment registry with per-variant funnels
