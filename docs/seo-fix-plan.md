# SEO Fix Plan — singaporebusinessbroker.com (Critical Issues)

> Paste this whole file into a Claude Code session that has the website codebase open.
> Context: this site is the sell-side lead funnel of The Funding Assembly Pte Ltd (Singapore SME M&A advisory). An SEO audit on 28 Aug 2026 scored it 66/100. This plan fixes the critical issues only. Work through the phases in order; each phase ends with a verification step. Do not change copy tone — the site's voice is calm, professional, specific.

---

## Phase 0 — Orient (do this first)

1. Detect the stack: look for `next.config.*`, `astro.config.*`, `gatsby-config.*`, `hugo.toml`, `_config.yml`, or plain HTML. Note where page metadata (title/meta/canonical) is defined — a shared layout/component or per-page frontmatter.
2. Locate these routes in the codebase: `/` (homepage), `/sell-your-business`, `/valuation`, `/about`, `/data/sme-multiples-singapore`, the `/sell/*` sector template (20 pages), the `/guides/*` template (10 pages), and the sitemap generator.
3. List what you found before editing anything.

---

## Phase 1 — Remove the placeholder data (highest priority, trust-critical)

**Problem:** `/data/sme-multiples-singapore/` publishes a "2026-Q3" EV/EBITDA multiples table explicitly labeled *"sample figures… carried over from the approved design prototype and are pending replacement with our own transaction data."* Invented financial data is live on a page meant to be the site's flagship citable asset.

**Fix (do BOTH until real data exists):**
1. Add `noindex` to this page only: `<meta name="robots" content="noindex, follow">`. Keep the page reachable for humans (it demonstrates capability) but out of the index.
2. Remove the page's URL from the sitemap output.
3. Replace the "2026-Q3" label and the prototype-carryover note with an honest banner: "Indicative ranges — our proprietary transaction dataset launches soon. Speak to us for current sector multiples." Remove the fake quarter stamp.
4. Leave a `TODO` comment at the top of the page source: `TODO: restore indexing + sitemap entry + Dataset schema when real multiples data ships`.

**Verify:** page renders, robots meta present, URL absent from generated sitemap, no "sample figures" or prototype text remains anywhere (`grep -ri "prototype\|sample figures" src/`).

---

## Phase 2 — JSON-LD structured data (highest-leverage code fix)

Currently the site has NO structured data except BreadcrumbList on guides. Add the following as JSON-LD `<script type="application/ld+json">` blocks. Prefer a reusable schema component; render server-side (must be in initial HTML, not injected client-side).

### 2a. Organization — sitewide (every page, via layout)
```json
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "@id": "https://www.singaporebusinessbroker.com/#organization",
  "name": "Singapore Business Broker",
  "url": "https://www.singaporebusinessbroker.com/",
  "logo": "https://www.singaporebusinessbroker.com/images/logo.png",
  "image": "https://www.singaporebusinessbroker.com/images/og-share.jpg",
  "telephone": "+65 8951 8821",
  "email": "Contact-us@thefundingassembly.com",
  "areaServed": { "@type": "Country", "name": "Singapore" },
  "parentOrganization": {
    "@type": "Organization",
    "name": "The Funding Assembly Pte Ltd",
    "url": "https://thefundingassembly.com/"
  },
  "description": "Sell-side M&A advisors for Singapore SME owners with S$3m to S$30m businesses. Success-based fees, confidential process, vetted buyer network.",
  "knowsAbout": ["SME mergers and acquisitions", "Business valuation", "Sell-side advisory", "Business succession", "Singapore SME sales"]
}
```
- Fix the logo path to the real logo asset in the repo.
- ERIC-TODO: if a registered address may be published, add an `address` block (PostalAddress) — big local-SEO win, required for Google Business Profile parity.

### 2b. FAQPage — homepage and /sell-your-business
Both pages have a "Questions owners ask first" section. Generate FAQPage schema from the EXACT on-page questions and answers (do not invent new ones; schema must mirror visible content):
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "<question text from page>",
      "acceptedAnswer": { "@type": "Answer", "text": "<answer text from page>" } }
  ]
}
```

### 2c. Article — all 10 /guides/* pages and /insights/* pages
Add to the guide template:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "<page H1>",
  "description": "<page meta description>",
  "author": { "@type": "Organization", "name": "Singapore Business Broker" },
  "publisher": { "@id": "https://www.singaporebusinessbroker.com/#organization" },
  "datePublished": "<from CMS/frontmatter>",
  "dateModified": "<from CMS/frontmatter or git last-commit date>",
  "mainEntityOfPage": "<canonical URL>"
}
```
- If pages have no date field, add `datePublished`/`dateModified` frontmatter now (use git history for initial values) and ALSO render a visible "Updated <Month Year>" line on the page — schema dates must match visible dates.
- ERIC-TODO: once team members are named on /about (Phase 4), switch `author` to a `Person` referencing them.

### 2d. Service — /sell-your-business and the /sell/* sector template
```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Sell-side M&A advisory<, sector-specific on /sell/* pages, e.g. ' for F&B businesses'>",
  "provider": { "@id": "https://www.singaporebusinessbroker.com/#organization" },
  "areaServed": { "@type": "Country", "name": "Singapore" }
}
```

**Verify:** for one page of each type (home, sell-your-business, one guide, one sector page), extract the rendered HTML and validate the JSON-LD parses (`node -e` JSON.parse on each block); confirm blocks appear in server-rendered output, not only after hydration. Then Eric spot-checks with https://validator.schema.org and Google's Rich Results Test after deploy.

---

## Phase 3 — Image alt text (site-wide)

1. Find every `<img>` / image component usage missing `alt` (`grep -rn "<img\|Image" src/ | grep -v "alt="` — adapt to stack).
2. Add descriptive, specific alt text. Pattern: describe what's in the image naturally; include a keyword only where honest. Examples:
   - `hero-owner.webp` → `alt="Singapore SME owner considering the sale of their business"`
   - `deal-meeting.webp` → `alt="Sell-side M&A advisor meeting a business owner in Singapore"`
   - `logistics-warehouse.webp` → `alt="Logistics warehouse operations — sector we sell in Singapore"`
3. Decorative-only images (dividers, backgrounds): use `alt=""` explicitly, never omit the attribute.
4. Confirm the OG image `/images/og-share.jpg` actually exists in the repo and is 1200×630. If missing, flag it — do not invent one.

**Verify:** repeat the grep — zero image elements without an alt attribute.

---

## Phase 4 — E-E-A-T: /about page and author signals

**Problem:** /about names no people, no credentials, no address. For a site asking owners to disclose S$3m–S$30m businesses, anonymous advisors hurt both rankings (YMYL-adjacent) and conversion.

**Code work now:**
1. Build the structure: an "Advisors" section on /about with placeholder-slots (photo, name, role, 2–3 line bio, credentials, LinkedIn link). Mark clearly `ERIC-TODO` — do NOT invent names, bios, photos, or credentials. Ship the section hidden/commented until real content is supplied.
2. Add a visible entity block to /about and the footer: "Singapore Business Broker is the sell-side M&A practice of The Funding Assembly Pte Ltd, Singapore." Make "The Funding Assembly" a real crawlable link to https://thefundingassembly.com/ (footer sitewide).
3. Add author byline component to the guides template: "By <author> · Updated <date>" — wired to the same frontmatter as Phase 2c. Until people are named, byline reads "By the Singapore Business Broker team".

**ERIC-TODO (content, not code):** supply advisor names/bios/photos, credentials, and decide whether to publish the registered address. This is the gating item for full E-E-A-T.

---

## Phase 5 — Technical cleanup (small, do in same session)

1. **Trailing slash consistency:** canonicals emit `/sell-your-business` while the sitemap emits `/sell-your-business/`. Pick the framework's native form, then make canonical tags, sitemap URLs, and all internal links agree, and 301 the other form. Verify: canonical URL of any page character-for-character equals its sitemap entry.
2. **Homepage title:** currently ~82 chars, truncates. Change to: `Business Broker Singapore | Sell Your Business Confidentially` (61 chars). Keep H1 unchanged.
3. **Sitemap hygiene:** emit real `lastmod` (from frontmatter/git date); remove blanket `changefreq: weekly`.
4. **F&B sector meta description:** replace "…most of them sell badly." opener with: `Sell your F&B business in Singapore at the right price. Sector multiples, who's buying, and how to avoid the mistakes that cost sellers money.` Then apply the same pattern (keyword + value + specifics, 140–160 chars) to the other 19 /sell/* pages using each page's own content.

---

## Final verification (run before finishing)

- Build succeeds; no console/build warnings introduced.
- Rendered HTML of home, /sell-your-business, one guide, one sector page each contains: exactly one H1, canonical matching sitemap form, valid JSON-LD (parse test), no missing alt attributes.
- Sitemap: no multiples-data URL, lastmod present, consistent trailing slashes.
- `grep -ri "sample figures\|prototype" src/` returns nothing user-visible.
- Produce a summary diff report: files changed per phase + the list of remaining ERIC-TODO items.

## Out of scope for this session (tracked separately)
Off-site work — Google Business Profile, broker-directory listings (BusinessForSale.sg, Flippa, SMERGERS), cross-links from thefundingassembly.com's ranking articles, real multiples dataset. These gate top-5 for "business broker Singapore" but are not code changes.
