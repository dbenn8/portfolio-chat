# Burrfect WordPress Site -- AI Builder Summary

## Part 1: n8n AI Product Builder -- Job Fit Evaluation

### Relevance Scores

| Workstream | Score (1-10) | Rationale |
|---|---|---|
| **AI Building / Super Agent** | 3 | Not an AI product, but the public-facing content layer that surfaces AI-enhanced data. The site receives AI-enhanced bean and roaster content from the backend (via Albato webhook automation) and presents it as a searchable recipe book. The `needsEnhancing` -> Perplexity API -> Albato webhook -> WordPress REST API pipeline is an end-to-end AI content delivery system. |
| **AI Trust** | 4 | Demonstrates production integration safety: Cloudflare WAF rules for API access, REST API security (unauthenticated access blocked for core endpoints, allowed for custom public endpoints), `firestore_id` tracking for cross-system consistency, and ToS gating for recipe data. GitHub Actions auto-deploy from main branch ensures reviewable changes. |

### Keywords Hit

- Automation (Albato webhook-to-WordPress pipeline)
- Integration (Firebase -> Albato -> WordPress REST API)
- Proactive suggestions (AI-enhanced bean descriptions automatically published)

### Strongest Talking Points

1. **"The WordPress site is the public-facing layer of a Firebase -> Albato -> WordPress automation pipeline that publishes AI-enhanced espresso content."** The backend's LLM enhancement (Perplexity API) enriches bean/roaster data, which triggers a webhook to Albato, which creates/updates WordPress posts via REST API. This is a real-world workflow automation pipeline similar to what n8n enables.

2. **"I built a custom block theme with REST API extensions, ACF integration, and Cloudflare WAF configuration to enable automated content publishing while keeping recipe data behind a ToS gate."** This shows the full-stack integration thinking needed for production automation systems.

### What to Highlight

- The end-to-end automation pipeline: Firebase Firestore trigger -> AI enhancement -> Albato webhook -> WordPress REST API -> Cloudflare-cached public page
- Custom REST API extensions for `firestore_id` querying (enables Albato to find existing posts for upsert)
- The search feature design: lazy-loaded client-side index, zero server load, Cloudflare edge-cached
- GitHub Actions -> FTP auto-deploy to WPX.net (no SSH access, creative deployment solution)

### What to Downplay

- WordPress is commodity tech -- frame it as "the automation endpoint, not the interesting part"
- The custom theme work (standard WP development)

### Connection to n8n's Product

- **Workflow automation endpoint:** The WordPress site is the "last mile" of an n8n-style automation pipeline (Firebase trigger -> webhook -> REST API CRUD). This demonstrates understanding of how automation tools connect systems.
- **API integration patterns:** Custom REST API extensions with `firestore_id` filtering, ACF field registration with get/update callbacks -- these are the same patterns n8n node builders need to understand.
- **Production automation safety:** Cloudflare WAF rules, IP allowlisting for automation, rate limiting -- the operational concerns of running automated pipelines in production.

---

## Part 2: Portfolio Case Study Draft

### One-Line Hook

"I built the public recipe book at burrfect.io as the endpoint of a Firebase -> AI enhancement -> Albato -> WordPress automation pipeline that publishes AI-enriched espresso content automatically."

### The Problem

Burrfect's mobile app has a growing database of beans, roasters, and dialed-in espresso recipes. But this content was locked inside the app -- invisible to search engines and inaccessible to users before they downloaded. I needed a public-facing content layer that would: (1) surface AI-enhanced bean/roaster descriptions for SEO, (2) publish automatically whenever the backend enhanced content, and (3) keep the valuable recipe parameters (dose, yield, brew time) behind a gate.

### My Role

Solo builder. Designed the content architecture, built the custom WordPress theme, configured the REST API extensions, set up the Albato automation pipeline, and deployed to WPX.net with Cloudflare.

### The Approach

1. **Custom post types for structured content:** `roaster` and `bean` post types with ACF fields, linked by `firestore_id` for cross-system identity. Country taxonomy for geographic organization. Permalink structure: `/recipes/{country}/{roaster}/{bean}/`.
2. **REST API as automation interface:** Custom query parameters for `firestore_id` filtering (so Albato can find existing posts for upsert). ACF fields exposed with both `get_callback` and `update_callback` (without update callback, ACF data via POST is silently ignored -- a non-obvious WordPress gotcha).
3. **Automated publishing pipeline:** Backend AI enhancement -> `beanBatchHistoryToWebsite()` webhook -> Albato receives event -> Albato calls WordPress REST API to create/update post. The backend sends the Firestore document ID and collection name; Albato handles the REST API mapping.
4. **Content gating:** Recipe parameters are behind a Terms of Service acceptance gate -- the public page shows the bean name, roaster, origin, description, but dose/yield/temperature require clicking through ToS.
5. **Client-side search:** Lazy-loaded JSON index of all roaster/bean names. Search icon triggers fetch, then instant client-side filtering with highlighted matches. Cloudflare caches the index at the edge.

### What I Built

**Custom Block Theme** (`burrfect-rebuilt/wp-content/themes/burrfect-theme/`):
- Block theme with `theme.json` configuration for WordPress 6.x
- Templates: `front-page.html`, `single-bean.html`, `single-roaster.html`, `archive-roaster.html`
- Parts: `header.html`, `footer.html`
- Custom image sizes for recipe thumbnails

**REST API Extensions** (`inc/rest-api.php`):
- `firestore_id` query parameter for both roaster and bean endpoints
- ACF field exposure with get + update callbacks
- Security: unauthenticated access blocked for `wp/v2/*`, allowed for `burrfect/v1/*`
- ToS gate and rate limiting for recipe-gated endpoint

**Post Types & Taxonomies** (`inc/post-types.php`, `inc/taxonomies.php`, `inc/acf-fields.php`):
- `roaster` and `bean` custom post types (registered via ACF in production to avoid conflicts)
- `country` taxonomy for geographic organization
- Custom permalink structure with country/roaster/bean hierarchy

**Search Feature** (designed in `docs/plans/2026-02-15-search-design.md`):
- Phase 1: Name-based quick-jump search (client-side)
- PHP generates JSON index of all published content
- Cache invalidation on `save_post_roaster` / `save_post_bean` hooks
- Lazy fetch on first search interaction (zero homepage impact)
- Future: attribute-based discovery (origin, process, tasting notes)

**Infrastructure:**
- WPX.net hosting (no SSH/WP-CLI, managed environment)
- GitHub Actions -> FTP auto-deploy on merge to main
- Cloudflare Pro with WAF skip rules for Albato automation IPs
- Defense branch workflow (work in Defense -> merge to main -> auto-deploy)

### The Result

- Live at burrfect.io with automatically published espresso content
- End-to-end automation: Firebase AI enhancement -> webhook -> WordPress (no manual content entry)
- SEO-visible content for beans and roasters indexed by Google
- Recipe parameters protected behind ToS gate
- Automated deployment via GitHub Actions on merge

### Tech Stack

- **CMS:** WordPress 6.x (custom block theme, ACF Pro for structured fields)
- **Hosting:** WPX.net (managed WordPress)
- **CDN/Security:** Cloudflare Pro (caching, WAF rules, IP allowlisting)
- **Automation:** Albato (webhook receiver -> WordPress REST API)
- **Deployment:** GitHub Actions -> FTP to WPX.net
- **Backend triggers:** Firebase Cloud Functions -> Albato webhooks
- **Theme:** PHP 8.2, block templates, custom REST API extensions
