# SEO Ranking Growth Plan — singaporebusinessbroker.com
## Implementation edition for Claude Code (GitHub + Vercel)

**Date**: 28 Aug 2026 (v2 — implementation-ready)
**Goal**: Page-1 (top-5) rankings for Singapore business-sale keywords, feeding TFA's sales funnel with qualified seller leads.
**Strategy (approved)**: Long-tail ladder + quarterly data asset. SBB is the single funnel domain; businessbrokerinsingapore.com (BBIS) 301s into it; thefundingassembly.com (TFA) cross-links in.
**Companion docs** (same folder): `seo-audit-singaporebusinessbroker.md` (findings), `seo-fix-plan-claude-code.md` (critical fixes — run as Session 1 below).

---

# PART A — Instructions to Claude Code (read first)

You are implementing this plan in the website's GitHub repository, deployed on Vercel. Work session by session (Part C). In every session follow this loop:

## A1. Working conventions

1. **Orient before editing.** Detect the framework (`next.config.*` → Next.js, `astro.config.*` → Astro, etc.), the content source (MDX/markdown files, or hardcoded JSX/components), where metadata is generated, and how the sitemap is built (`next-sitemap.config.js` likely, given the live `/sitemap-index.xml` + `/sitemap-0.xml` pattern). State findings before changing anything.
2. **Branch per session**: `git checkout -b seo/<session-slug>` (e.g. `seo/s2-bbis-redirects`). Never commit directly to `main`.
3. **Commit style**: conventional commits, small logical commits (`feat(seo): add FAQPage schema to sector template`).
4. **PR + preview deploy**: push branch, open PR with `gh pr create`. Vercel builds a preview deployment automatically. Put the session's verification results in the PR description.
5. **Verify on the preview URL before merge.** Vercel preview deployments send `X-Robots-Tag: noindex` automatically, so previews are safe — but this also means `curl` checks against previews for robots behavior must target the response BODY meta tags, not headers.
6. **Merge to `main` = production deploy.** After merge, run the session's production verification (A3).
7. **Never invent facts.** Multiples, fees, timelines, sector claims: use only what already exists in the repo content or what Eric supplies. Anything missing → insert `<!-- ERIC-TODO: ... -->` and list it in the PR description. Copy tone: calm, professional, specific — match existing pages.
8. **Metadata rules for all new/edited pages**: title ≤60 chars with target keyword; meta description 140–160 chars with keyword + value proposition; one H1; canonical matching the site's chosen trailing-slash form; page added to sitemap automatically (verify the generator picks it up).

## A2. Vercel-specific mechanics

- **Redirects** (BBIS consolidation, slash unification): prefer framework-native config (`next.config.js` `redirects()` for Next.js) over `vercel.json`; use `vercel.json` `redirects` only if the framework has no native mechanism. All redirects `permanent: true` (308/301).
- **Cross-domain redirect (BBIS → SBB)**: requires the BBIS domain added to the SAME Vercel project (or a tiny separate project that only redirects). Implementation: add `businessbrokerinsingapore.com` + `www` as domains in Vercel project settings (ERIC-TODO: do this in the Vercel dashboard and update BBIS DNS to Vercel), then host-based redirects in config — match on `host` header, map each BBIS path to its SBB equivalent (map in Session 2).
- **Headers**: any `X-Robots-Tag` needs live on specific paths go in `next.config.js` `headers()` / `vercel.json` `headers`.
- **Env vars** (analytics IDs, email-provider API key): reference as `process.env.*`, document the required names in the PR, never commit values. ERIC-TODO sets them in Vercel dashboard (Production + Preview).
- **Forms/API**: valuation calculator submission → a route handler / serverless function (`/api/valuation-report`) that forwards to the email provider. Rate-limit lightly and validate input server-side.

## A3. Standard verification block (run at the end of every session)

```bash
# build passes
npm run build   # or the repo's build command

# on the preview/production URL, for each page touched:
# - exactly one <h1>
# - canonical present and matches sitemap form
# - JSON-LD parses:
curl -s <URL> | grep -o '<script type="application/ld+json">.*</script>' # then JSON.parse each block
# - no img without alt on touched pages
# - sitemap contains/excludes the right URLs
curl -s https://www.singaporebusinessbroker.com/sitemap-0.xml
# - redirects return 301/308 with correct Location (Session 2+)
curl -sI https://businessbrokerinsingapore.com/<path>
```

Report results in the PR. If any check fails, fix before requesting merge.

---

# PART B — Approved strategy (context, do not re-decide)

1. **Domains**: SBB = the transactional funnel. BBIS 301s page-to-page into SBB. TFA main keeps informational content, links into SBB.
2. **Capacity**: 2–4 content pieces/month. Claude Code drafts, Eric reviews for accuracy before merge.
3. **Engagement**: valuation tool is the hero asset — instant on-screen range free, email gates the full report. Every content page embeds or links to it.
4. **E-E-A-T**: company-level only (TFA entity, no named individuals). Revisit at month 6 if head terms stall.
5. **Off-site**: time-only, no spend. Head-term ("business broker singapore") timeline: 9–12 months.
6. **Keyword ladder**: T1 sector long-tails (months 1–4) → T2 question keywords (3–8) → T3 head terms (6–12).

**Honesty constraint (hard rule)**: calculator and content label all ranges as indicative with sources; nothing implies proprietary transaction data until the real dataset ships (Session 8).

---

# PART C — Implementation sessions

Each session = one branch, one PR, one paste-able unit of work. Do them in order; later sessions assume earlier merges.

## Session 1 — Critical fixes
Execute `seo-fix-plan-claude-code.md` (in this folder) end to end: placeholder multiples page noindexed + out of sitemap, JSON-LD (Organization sitewide, FAQPage on home + /sell-your-business, Article on guides, Service on sell pages), image alt pass, trailing-slash unification, homepage title trim, sitemap lastmod, sector meta descriptions. Branch `seo/s1-critical-fixes`. That doc has its own phases and verification.

## Session 2 — BBIS 301 consolidation
Branch `seo/s2-bbis-redirects`.
1. Add host-based permanent redirects (see A2) with this page map:

| BBIS path | → SBB destination |
|---|---|
| `/` | `/` |
| `/sell-your-business-singapore/` | `/sell-your-business/` |
| `/business-valuation-singapore/` | `/valuation/` |
| `/fees/` | `/sell-your-business/#fees` (or the fees section anchor that exists) |
| `/how-it-works/` | `/sell-your-business/` |
| `/sell-your-fnb-business-singapore/` | `/sell/fnb/` |
| `/faq/` | `/sell-your-business/#faq` (or homepage FAQ anchor) |
| `/buy-a-business-singapore/` | `/buyers/` |
| `/contact/` | `/contact/` |
| anything else | `/` |

2. Verify each returns 301/308 with correct `Location` once DNS is live.
3. ERIC-TODO (blocker for this session going live, not for the code): add BBIS domains to the Vercel project + point BBIS DNS at Vercel; afterwards run GSC Change of Address on the BBIS property.

## Session 3 — Valuation calculator (hero asset)
Branch `seo/s3-valuation-calculator`.
1. Rebuild `/valuation` as an interactive client component: sector select (same 20-sector taxonomy as `/sell/*` slugs), annual revenue + EBITDA inputs (S$; sliders or formatted number fields), instant indicative EV range on screen. Multiples table lives in ONE data module (e.g. `src/data/sectorMultiples.ts`) with a `source` + `updated` field per sector — same module Session 8 will later replace with real data. Label output: "Indicative range based on published Singapore SME transaction ranges."
2. Email-gated full report: form (name, email, sector, revenue, EBITDA) → `/api/valuation-report` route handler → email provider API (`process.env.EMAIL_API_KEY`; provider = ERIC-TODO). Report content: range + what moves it + link to relevant sector page + book-a-call CTA. Store nothing beyond the send unless a CRM env var is configured.
3. Compact embed component `<ValuationTeaser sector="fnb" />`: one-line pitch + mini form or link with sector pre-selected via query param (`/valuation?sector=fnb`). Add to all 20 `/sell/*` pages (template-level, one change).
4. Keep the page fast: calculator is the only client-side island; page shell stays server-rendered with existing metadata.
5. Verify: build, Lighthouse performance ≥90 on /valuation, instant result works without email, API route rejects invalid input, teaser renders on 3 sampled sector pages with correct pre-selection.

## Session 4 — Sector rebuild #1: F&B (the template)
Branch `seo/s4-sector-fnb`.
1. Expand `/sell/fnb/` to 1,800–2,500 words with this structure (becomes the template for Sessions 5): intro (keyword in first 100 words) → why owners sell now → who's buying → sector multiple range + what it depends on (from the Session 3 data module — single source of truth) → one worked valuation example labeled "illustrative" → what raises the price → what costs money → 5-question sector FAQ (accordion + FAQPage schema) → ValuationTeaser embed → "Read next" internal links (2 guides + 2 adjacent sectors).
2. Target keywords: "sell F&B business singapore", "restaurant valuation singapore", "how much is a restaurant worth in Singapore" — in title, H2s, FAQ questions where natural. No stuffing.
3. Reuse ALL existing page copy that survives review — expand, don't discard; the current copy's voice is the standard.
4. Draft content from existing repo content + this doc only; mark unknown figures `ERIC-TODO`. Eric reviews the PR before merge (accuracy gate).
5. Verify: standard block + word count + FAQPage schema validates.

## Session 5 (×4, months 2–4) — Sector rebuilds: logistics, education, healthcare, manufacturing
Branches `seo/s5-sector-<slug>`. Same structure as Session 4's approved F&B template. One PR per sector. After these five, refresh the remaining 15 sector pages at ~2/month with the same template, lighter depth (1,200+ words).

## Session 6 — Engagement extras
Branch `seo/s6-engagement`.
1. **Exit-readiness quiz** at `/exit-readiness/`: 10 yes/no/partial questions (owner dependency, ≥3yr clean financials, lease tenure >2yr, customer concentration <30%, documented processes, management depth, recurring revenue, clean cap table, separated personal expenses, growth trend) → score 0–100 → 3 result bands with tailored next steps → valuation CTA. Own metadata targeting "is my business ready to sell". Server-rendered shell, client island for the quiz. Quiz results NOT emailed-gated; CTA leads to /valuation.
2. **Interactive sale timeline** on `/sell-your-business`: the existing 5 stages as a clickable component (click stage → detail panel). Progressive enhancement — stages render as plain content without JS.
3. **FAQ accordions** on any sector/guide page still lacking them (with FAQPage schema, mirroring visible text).
4. Verify: standard block + quiz keyboard-accessible + timeline degrades without JS.

## Session 7 — TFA cross-link edits (separate repo)
Runs in the **thefundingassembly.com repo** (or its CMS — orient first; if content lives in a CMS Claude Code can't reach, output the exact edits as a checklist for Eric instead).
1. Edit the two already-ranking articles ("how to sell a business in Singapore" resources piece; "how to value a business in Singapore") — add 1–2 contextual in-body links each to SBB: `/valuation/` ("get an instant indicative range") and the relevant sector page. Natural anchors, no "click here", no footer-spam.
2. Add one new TFA informational article per month (2–4/mo capacity shared with SBB content): informational intent only (TFA keeps "how/what/why"; SBB keeps "sell/broker/valuation service" — do not cannibalize), each linking once to an SBB money page.
3. Verify links are crawlable `<a href>` (not JS-only), live on production.

## Session 8 — Data asset relaunch (quarterly, gated on real data)
Branch `seo/s8-multiples-data`. **Blocked until Eric supplies real anonymized transaction data or a documented public-sources methodology.**
1. Replace the sample figures in the data module with the real dataset (per-sector: range, n or source basis, quarter).
2. On `/data/sme-multiples-singapore/`: remove the Session-1 noindex, restore to sitemap, add `Dataset` JSON-LD, visible methodology + limitations section, quarter stamp, downloadable CSV generated from the same data module.
3. Add "updated <quarter>" chips wherever sector pages cite multiples (auto from data module).
4. Verify: page indexed (`site:` check after a week), schema validates, CSV matches page table.

## Session 9 — Measurement wiring
Branch `seo/s9-analytics`.
1. Add analytics (GA4 or Plausible — ERIC-TODO picks; env var for the ID) with events: `valuation_instant_result`, `valuation_report_requested`, `book_call_click`, `quiz_completed`.
2. Confirm GSC verification tag/DNS is in place (ERIC-TODO owns the GSC account).
3. Add a `docs/seo-log.md` in the repo: session log + monthly review template (tier keyword positions, impressions, leads, stalled pages, actions). Claude Code appends after every session; Eric pastes GSC numbers monthly.

---

# PART D — Eric-only tasks (not code; Claude Code lists these in PRs when they gate a session)

| When | Task |
|---|---|
| Week 1 | GSC + Bing verification for SBB; submit sitemap |
| Week 1–2 | Vercel: add BBIS domains to project; update BBIS DNS (gates Session 2 going live) |
| Week 2 | Google Business Profile (needs address decision); pick email provider + set env vars |
| Weeks 2–4 | Directory sweep: BusinessForSale.sg, Flippa broker list, SMERGERS profile, finestservices pitch, SBF. Consistent name/phone/URL |
| After Session 2 live | GSC Change of Address on BBIS property |
| Monthly | Review + merge content PRs (accuracy gate); 2 LinkedIn posts repurposing guides; paste GSC numbers into monthly review |
| Quarterly | Supply real multiples data (gates Session 8); pick one data insight, pitch SGSME / Business Times SME / DollarsAndSense / Vulcan Post |
| Month 6 | If head terms stalled: revisit naming advisors (E-E-A-T upgrade) |

---

# PART E — Targets & iteration

**Kill/iterate rule**: any Tier-1 page not improving after 90 days indexed → diagnose intent/title/depth → rewrite or merge. Log in `docs/seo-log.md`.

| Milestone | Target |
|---|---|
| Month 3 | 5 sector long-tails top 10; calculator live; BBIS redirects live; impressions trending up |
| Month 6 | 2+ long-tails top 5; ≥10 valuation leads/month; directories live; TFA links passing traffic |
| Month 9 | T2 question keywords on page 1; first data-asset PR pitch sent |
| Month 12 | "sell my business singapore" top 5; "business broker singapore" page 1; nurture converting leads to calls |

**Risks**: company-level E-E-A-T caps head-term ceiling (month-6 revisit); data asset gated on real data (fallback: public-sources methodology); PR pickup uncertain (ladder doesn't depend on it — PR is upside).
