# Implementation plan

Work top to bottom. Each task ends with a commit. Check `CLAUDE.md` for rules.

## Phase 1: Foundation + homepage + valuation (target: 2 weeks)

1. **Scaffold**: `npm create astro@latest` (empty, TypeScript strict), add `@astrojs/tailwind`, `@astrojs/mdx`, `@astrojs/sitemap`. Copy tokens from `prototype/tailwind.config.js` into `tailwind.config.mjs`. `darkMode: 'media'`. Add Geist + Geist Mono woff2 to `public/fonts`, `@font-face` in `src/styles/global.css`. Install `@phosphor-icons/web`.
2. **Layout**: `src/layouts/Base.astro` with head (title, description, canonical, OG, JSON-LD slot), grain overlay, `<Nav />`, `<Footer />`. Port floating pill nav + mobile morph menu from prototype into `src/components/Nav.astro` (+ small script). Port footer.
3. **Primitives**: `Button.astro` (variants: primary ink, primary accent, secondary ring, inverse; nested icon circle), `Shell.astro` (double-bezel wrapper with `radius` prop), `Section.astro` (spacing), `Reveal` script (IntersectionObserver, blur fade-up, reduced motion).
4. **Homepage**: port every section of `prototype/index.html` into components under `src/components/home/`: Hero, ProofStrip, WhyUs (bento), Process, ValuationTeaser (embeds tool), CaseStudies (cascade), Sectors, BuyerDemand, FAQ, FinalCTA. Content from `src/data/*.json` (stats, cases, buyers, faq, sectors). Keep `(sample)` markers.
5. **Valuation tool**: `src/components/Valuation.astro` + `src/scripts/valuation.ts` (3-step form, validation, compute, scoring, count-up). Multiples in `src/data/multiples.json`. On submit: `POST /api/valuation` (fetch), optimistic result on screen.
6. **API**: `functions/api/valuation.ts` (Cloudflare) or `api/valuation.ts` (Vercel). Zod validate, score, CRM upsert (HubSpot or Airtable via env), Resend email (report HTML), Slack/email alert on hot. Env vars documented in `.env.example`.
7. **/valuation page**: full-page version of tool + trust copy.
8. **/book-a-call**: Cal.com embed. **/contact**, **/about**, **/privacy** (PDPA), **/terms**.
9. **Analytics + SEO**: Plausible or GA4 snippet, events (valuation_start, valuation_complete, booking_click, form_submit). Sitemap, robots, OG image per page (static `og-share` for now). JSON-LD Organization + Service on `/`, FAQPage on `/` FAQ.
10. **QA**: mobile pass at 390px, dark mode pass, keyboard nav, Lighthouse on `/` and `/valuation`. Fix until targets met. Grep for em-dashes.

## Phase 2: Content engine (target: 2 weeks)

11. **Content collections**: `src/content/sectors/*.mdx`, `guides/*.mdx`, `cases/*.mdx`, `insights/*.mdx` with schemas (title, description, sector, dates, multiples range for sectors).
12. **/sell/[sector]** template: hero with sector name, why owners sell in this sector, who buys, typical multiples (from `multiples.json`), pitfalls, CTA to valuation pre-filled with sector. Seed 20 sector MDX files (drafts, marked for human edit).
13. **/guides/[slug]** template + 10 guides (drafts): preparing to sell, succession planning, valuation methods, deal structures, earn-outs, tax and stamp duty, NDAs and confidentiality, sale timeline, common mistakes, share vs asset sale.
14. **/case-studies** index + `[slug]` (3 to 5 anonymised entries).
15. **/data/sme-multiples-singapore**: table by sector, quarterly date stamp, methodology note, downloadable CSV. Article JSON-LD.
16. **/buyers**: demand board (from `buyers.json`) + buyer registration form (POST `/api/buyer`).
17. **/insights** index + article layout. Set up the weekly content workflow: new MDX via PR.
18. **Internal linking**: sector pages link to guides and valuation; guides link to sector pages; footer links updated.

## Phase 3: Launch (ongoing)

19. Deploy to Cloudflare Pages/Vercel, custom domain, HTTPS, redirects, 404 page.
20. Google Search Console, Google Business Profile, submit sitemap.
21. Replace all `(sample)` data with real TFA figures; download and self-host images (`assets/download.sh`).
22. Nurture emails (6-step) in Resend/HubSpot; hot-lead alert tested end to end.
23. Paid test: Google Ads landing variant of `/valuation` with UTM tracking.
