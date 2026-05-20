# Merge Duplicates Dashboard -- AI Builder Summary

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Relevance Scores

| Workstream | Score (1-10) | Rationale |
|---|---|---|
| **AI Building / Super Agent** | 4 | Not an AI product, but an internal admin tool that manages the data quality underlying the AI recommendation engine. Fuzzy string matching (Levenshtein + token similarity) for duplicate detection is a lightweight ML technique. The tool directly impacts AI system quality: duplicate beans/roasters fragment the statistics that power the recommendation engine's cascading stats pipeline. |
| **AI Trust** | 6 | Demonstrates data quality discipline critical for trustworthy AI. Dry-run preview before execution, audit logging of every merge, WordPress sync queue for cross-system consistency, and `updateSource: 'script'` to safely bypass Cloud Function triggers. The tool ensures the data feeding the AI models is clean and deduplicated. |

### Keywords Hit

- Human-in-the-loop (side-by-side merge review with radio buttons for field selection)
- Reliability (dry-run preview, batched writes chunked at 500 ops, audit trail)
- Debugging (audit log with filterable history)
- Guardrails (archive losers to `_archived_beans`/`_archived_roasters` for recovery)

### Strongest Talking Points

1. **"I built a data quality tool because I learned that my AI recommendation engine's accuracy depends on clean, deduplicated data."** This shows product maturity. Most builders focus on the model; few invest in the data quality infrastructure that makes models reliable. Duplicate beans fragment the cascading stats pipeline, reducing sample sizes and diluting the signal the meta-model uses for selection.

2. **"The merge handles 6+ Firestore collection cascades, WordPress sync, and audit logging -- with dry-run preview and `updateSource: 'script'` to safely bypass 15+ Cloud Function triggers."** This demonstrates understanding of production systems complexity. A naive merge would trigger infinite loops through the backend's Firestore triggers.

### What to Highlight

- The cross-system consistency problem: Firestore merge -> WordPress deletion queue -> audit log
- Fuzzy matching with combined Levenshtein + token similarity for duplicate detection
- The production safety patterns: dry-run, batched writes, trigger bypass, archival (not deletion)

### What to Downplay

- This is an internal admin tool, not user-facing
- The "AI" is just string similarity, not deep learning

### Connection to n8n's Product

- **Data quality for AI:** n8n's AI features depend on reliable data flowing through workflows. This tool solves the same class of problem: ensuring upstream data quality for downstream AI accuracy.
- **Human-in-the-loop patterns:** Side-by-side comparison with user selection is the same pattern n8n needs for AI output review and correction.
- **Cross-system orchestration:** The merge cascades across Firestore collections and WordPress -- analogous to n8n's multi-step workflow execution with rollback/audit concerns.

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

"I built an admin tool for deduplicating beans and roasters across Firestore and WordPress because my AI recommendation engine's accuracy depends on clean, unfragmented data."

### The Problem

The Burrfect database had hundreds of duplicate beans and roasters created by different users -- "Onyx Coffee Lab" vs "Onyx Coffee" vs "Onyx Coffee Labs". Each duplicate fragmented the recommendation engine's statistics: instead of 50 shots of data for one bean, the system saw 20 for one duplicate and 30 for another, reducing confidence and accuracy in the cascading stats pipeline.

### My Role

Solo builder. Identified the data quality problem through the analytics dashboard, designed the merge logic, built the full-stack admin tool, and deployed it.

### The Approach

1. **Detect duplicates:** Combined Levenshtein distance and token-based similarity scoring. Common suffixes stripped for roasters ("Coffee", "Roasting", "Co"). Blank-roaster duplicates prioritized.
2. **Review with context:** Side-by-side field comparison showing both records. Auto-suggest winner based on non-blank fields and higher `totalUsed` counts. Radio buttons for field-level override.
3. **Execute safely:** Dry-run preview shows exactly what will change. Real execution uses batched writes (chunked at 500) with `updateSource: 'script'` to bypass the 15+ Cloud Function triggers that would otherwise fire.
4. **Cascade everywhere:** Bean merges touch 6+ collections (bean-batches, shots, bean-batch-history, bean-reviews, bean-statsv2, enhancement tracking). Roaster merges cascade further with optional cross-roaster bean dedup.
5. **Keep systems in sync:** WordPress sync queue tracks deleted Firestore IDs for cleanup of the public recipe book.

### What I Built

**Backend API** (`api/`):
- `duplicates.js` -- Fuzzy matching engine with combined Levenshtein + token similarity. Scans all beans and roasters, returns priority-sorted duplicate pairs.
- `merge.js` -- Merge execution with BatchWriter (chunked at 500 ops), field-level merge logic, 6+ collection cascade, archive-not-delete pattern, audit logging to `_merge_audit_log`.
- `audit.js` -- Filterable audit trail of all past merges.
- `wpSyncQueue.js` -- WordPress deletion queue for cross-system consistency.

**Frontend** (`src/`):
- `BeanDuplicates.jsx` / `RoasterDuplicates.jsx` -- Priority-sorted duplicate queues
- `MergeReview.jsx` -- Side-by-side field comparison with radio buttons and auto-suggestions
- `AuditLog.jsx` -- Filterable merge history

**Production Safety:**
- Dry-run mode shows exactly what would change before executing
- `updateSource: 'script'` on all writes to bypass Cloud Function triggers (prevents infinite loops)
- Losers archived to `_archived_beans` / `_archived_roasters` (recoverable, not deleted)
- Batched writes chunked at Firestore's 500-operation limit
- WordPress sync queue for cross-system cleanup

### The Result

- Hundreds of duplicate beans and roasters merged, improving recommendation engine data quality
- Full audit trail of every merge operation
- WordPress recipe book kept in sync with Firestore canonical data
- Zero data loss (all losers archived for recovery)

### Tech Stack

- **Frontend:** React 18 + Vite 5 (SPA with React Router)
- **Backend:** Express.js with Firebase Admin SDK
- **Database:** Firestore (reads all collections, writes with batched operations)
- **Similarity:** Levenshtein distance + token-based Jaccard similarity
- **Deployment:** Appliku (Docker, Node 20)
- **Cross-system:** WordPress sync queue for recipe book cleanup
