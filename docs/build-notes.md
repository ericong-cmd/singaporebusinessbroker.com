# Build notes

What was built against `docs/implementation-plan.md`, where it lives, and every
deviation from `CLAUDE.md` with the reason. Read this before changing anything
that looks wrong: several of the odd-looking choices are deliberate and the
reasoning is here.

## Status against the plan

**Phase 1 (foundation, homepage, valuation): complete.**

| Task | Where |
|---|---|
| 1. Scaffold, tokens, fonts, icons | `astro.config.mjs`, `tailwind.config.mjs`, `public/fonts/`, `src/components/Icon.astro` |
| 2. Layout, nav, footer | `src/layouts/Base.astro`, `src/components/Nav.astro`, `Footer.astro` |
| 3. Primitives | `Button.astro`, `Shell.astro`, `Eyebrow.astro`, `PageHeader.astro`, reveal script in `Base.astro` |
| 4. Homepage sections | `src/components/home/*`, data in `src/data/*.json` |
| 5. Valuation tool | `src/components/Valuation.astro`, `src/scripts/valuation.ts` |
| 6. API | `api/valuation.ts`, `api/contact.ts`, `api/_lib.ts`, `.env.example` |
| 7. `/valuation` page | `src/pages/valuation.astro` |
| 8. Booking, contact, about, legal | `book-a-call`, `contact`, `about`, `privacy`, `terms` |
| 9. Analytics, SEO, schema, sitemap | `Base.astro`, `@astrojs/sitemap`, `public/robots.txt` |
| 10. QA | see "Verification" below |

**Phase 2 (content engine): mostly complete.**

| Task | Where |
|---|---|
| 11. Content collections | `src/content/config.ts` (sectors, guides, cases, insights) |
| 12. 20 sector pages | `src/content/sectors/*.mdx`, template `src/pages/sell/[sector].astro` |
| 13. 10 guides | `src/content/guides/*.mdx`, template `src/pages/guides/[slug].astro` |
| 14. Case studies | `src/content/cases/*.mdx` (4 anonymised samples) |
| 15. Multiples data page | `src/pages/data/sme-multiples-singapore.astro` + CSV in `public/data/` |
| 16. Buyer board | `src/pages/buyers.astro`, `src/data/buyers.json` |
| 17. Insights | `src/pages/insights/`, one seed article |
| 18. Internal linking | sector to guides and valuation, guides to each other, footer, multiples table to sector pages |

Not done from Phase 2: the buyer **registration form** posts to `/api/contact`
with `enquiry=buyer` rather than a separate `/api/buyer` endpoint. One endpoint
with a type field was simpler than two near-identical ones.

**Phase 3 (launch): partially done.** Deployment, redirects and 404 are in
place. Search Console, Google Business Profile, nurture sequences, the paid
test and replacing sample data with real TFA figures are all owner tasks.

## Deviations from CLAUDE.md, and why

1. **Icons are inlined SVG, not the icon webfont.** `CLAUDE.md` asks for
   `@phosphor-icons/web` (light). That package is a ~46 MB install whose light
   webfont would be a render-blocking download for the fourteen glyphs this
   site uses, against an LCP budget of 2.5s set in the same document.
   `src/components/Icon.astro` inlines the identical official Phosphor Light
   paths from `@phosphor-icons/core` at build time. Same artwork, nothing
   hand-rolled, no font request. Total shipped JS across the whole site is
   about 8.6 KB as a result.

2. **One bento cell lost its photograph.** The prototype puts photos in two
   cells of the "Most owners sell once" bento. Of the five images in
   `assets/images.json`, two are unusable (below), and of the three clean ones
   the hero and the featured case study each need one. The small span-7 cell
   therefore uses the icon-and-text card already established by the three cells
   beside it. Restore the photo when a clean render exists.
   See `src/components/home/WhyUs.astro`.

3. **`Section.astro` was not kept.** The plan lists it as a spacing primitive,
   but every section carries the prototype's exact spacing classes so that the
   port stays faithful, which left the component unused. Dead code is worse
   than a missing primitive.

4. **A skip link was added.** Not in the prototype. The nav is a fixed pill
   with no in-page landmark before it, so keyboard users had no way past it.

5. **The booking script is bundled, not inlined.** `book-a-call.astro` first
   used `define:vars` to pass the Cal.com URL into its script. `define:vars`
   forces `is:inline`, which the production CSP blocked, so the booking button
   was dead on the deployed site. The URL now rides on a `data-booking-url`
   attribute and the script is a normal bundled module covered by
   `script-src 'self'`. Only one inline script remains site-wide, and its hash
   is pinned in `vercel.json`. Adding another inline script means adding
   another hash, so prefer a data attribute.

6. **Reveal animations are gated on `html.js`.** An inline script sets the
   class before first paint. Without it, a JavaScript error anywhere would
   leave every `.reveal` element at `opacity: 0` and the page would render
   blank. With the gate, a JS failure shows everything unanimated.

## The images

`assets/images.json` lists five generated photographs. Two came out of the
generator with hallucinated text baked in and could not be used as delivered:

- **`hero-owner.png`**: a fake browser header bar across the top with garbled
  words in it, plus two blocks of garbled lettering across the middle of the
  frame. Patching the lettering was tried and looked like a censor bar. What
  ships instead is the largest 5:4 window that sits entirely above the text
  band, which is a clean and usable editorial portrait, though tighter than the
  original composition and only 731px wide at source. See
  `assets/build-images.mjs`.
- **`og-share.png`**: split-screen artifact, garbled text and a hallucinated
  "M&A" logo. Discarded entirely. `tools/make-og.mjs` composes the share card
  instead from the clean `deal-meeting` photograph plus real type in Geist.

Both should be replaced when clean renders are available. The other three
(`deal-meeting`, `industrial-estate`, `logistics-warehouse`) are clean and are
used as the manifest intended, resized to webp at two widths each.

Regenerate everything with `npm run images` and `npm run og`.

## Sample data still to replace

Everything marked `(sample)` on the site, plus:

- `src/data/multiples.json` — sector ranges carried over from the prototype.
  Replace with TFA transaction data and update `updated` to the current quarter.
- `src/data/stats.json`, `src/data/buyers.json` — proof strip and buyer board.
- `src/content/cases/*.mdx` — four illustrative deals. Real anonymised
  transactions should replace them, keeping `sample: false`.
- `src/data/site.json` — `bookingUrl` points at a placeholder Cal.com handle
  (`cal.com/singaporebusinessbroker/30min`). Until it is a real booking link
  the button on `/book-a-call` opens a dead calendar. `frame-src` in
  `vercel.json` already allows cal.com; change it if you use another scheduler.
- All 20 sector files and 10 guides carry `reviewed: false` in frontmatter.
  They are drafts written to be publishable but they have not been read by a
  person who does these deals. Flip to `true` as they are reviewed.

## Verification performed

Against the built output, not the dev server:

- `npx astro check`: 0 errors, 0 warnings.
- `npm run lint:copy`: 49 rendered pages, no em-dashes, banned words or
  placeholder brackets.
- Every page rendered at 1440px, 820px and 390px in both light and dark: no
  console errors, no failed requests, no horizontal overflow.
- Contrast sampled on every text node against its composited background in
  both schemes: no failures. One flag remains on the bento headline, which is
  white text over a photograph and a dark scrim that the sampler cannot see.
- Heading order, single `<h1>`, `lang`, duplicate ids, image `alt` and
  accessible names on links and buttons: clean on every page.
- Valuation tool end to end: step validation blocks empty steps; a hot lead
  (logistics, S$5-10m revenue, S$1.2m profit, low dependency, 12 months, 100%)
  returns S$4.4m to S$6.9m and shows the booking CTA; a cold lead (retail,
  under S$1m, high dependency, 2 years) returns S$169k to S$209k with the
  upper multiple capped, and shows the warm panel; `?sector=childcare`
  pre-selects the sector; with the API unreachable the estimate still renders
  and a fallback contact line appears.
- CSP from `vercel.json` applied to the pages: no violations; the estimator,
  the reveal observer, the mobile menu and the booking button all still work.
  The single inline script's hash was checked against the deployed HTML.
- Against the live deployment: all 16 routes 200 (404 for an unknown path),
  fonts, images, CSV, sitemap and robots served, security headers and
  immutable caching present, all five vanity redirects 308 correctly, and both
  endpoints exercised: GET 405, malformed body 400, consent false 400, a hot
  lead scored `hot`, a cold lead scored `cold`, contact accepted. With no
  integration env vars set every delivery reports `skipped`, as designed.

Lighthouse itself was not run: no Chrome measurement harness is available in
this environment. The proxies for it are the payload numbers above, the
absence of third-party origins, and explicit `width`/`height` on every image
for CLS. Run it before calling Phase 1 signed off.
