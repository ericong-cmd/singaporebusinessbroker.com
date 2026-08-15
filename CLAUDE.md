# singaporebusinessbroker.com

Sell-side M&A advisory site for Singapore SME owners (S$3m to S$30m). Standalone brand under The Funding Assembly. Objective: high-quality seller leads via free valuation estimator, then confidential call booking.

Read in this order:
1. `docs/design-spec.md` - approved product/site spec (positioning, site map, valuation logic, lead scoring, SEO, tech, phases)
2. `docs/implementation-plan.md` - build tasks in order
3. `docs/build-notes.md` - what is built, where it lives, and every deviation from this file with its reason
4. `prototype/index.html` - approved homepage design (self-contained, open in browser). `prototype/src.html` is the same file before Tailwind was compiled inline; `prototype/tailwind.config.js` holds the design tokens
5. `assets/images.json` - generated photography URLs and where each is used

## Stack (decided, do not change)
- Astro 4+ (static output), Tailwind CSS, MDX content collections
- Serverless endpoint for valuation lead intake (Cloudflare Pages Functions or Vercel Functions)
- Cal.com embed for bookings; HubSpot (free) or Airtable for CRM; Resend for email
- Plausible or GA4 analytics
- Deploy: Cloudflare Pages or Vercel

## Design rules (from approved prototype)
- Fonts: Geist (300/400/500/600) + Geist Mono. Self-host via `@font-face`, `font-display: swap`. Never Inter/Roboto/Arial.
- Icons: Phosphor Light only. Implemented by inlining the official `@phosphor-icons/core` light SVGs through `src/components/Icon.astro` rather than loading the `@phosphor-icons/web` font; see `docs/build-notes.md`. Still no hand-rolled icon artwork.
- Palette (Tailwind tokens in `tailwind.config.mjs`, ported from `prototype/tailwind.config.js`): ink `#0e1a2b`, ink-2 `#2b3a4f`, ink-3 `#5b687a`, paper `#f6f7f4`, paper-2 `#eef0ec`, accent `#0f6b4f`, accent-2 `#0c5740`, accent-soft `#e3f1ea`. ONE accent color, whole site.
- Dark mode via `prefers-color-scheme`. The prototype's `.dk-*` helper classes are ported to Tailwind `dark:` variants with `darkMode: 'media'`; the dark surfaces live under the `night` color token.
- Shapes: pill buttons (`rounded-full`), cards use double-bezel via `src/components/Shell.astro` (outer shell + inner core inset by the shell padding). No 1px grey borders, no dark drop shadows.
- Buttons: `src/components/Button.astro`. Primary = pill with nested icon circle on the right. Hover: icon circle translates/scales. Active: `scale-[0.98]`.
- Motion: easing `cubic-bezier(0.32,0.72,0,1)`. Scroll reveal = blur + fade-up via IntersectionObserver (never `window.addEventListener('scroll')`). Honor `prefers-reduced-motion`.
- Nav: floating glass pill, fixed, detached from top. Mobile: hamburger morphs to X, full-screen blur menu, staggered links.
- Fixed film-grain overlay (`.grain`), `pointer-events-none`.
- Sections `py-28` to `py-40`. Hero `min-h-[100dvh]`, never `h-screen`.
- Copy: no em-dashes anywhere. No "elevate/seamless/unleash". Plain, specific, owner-to-owner tone. Enforced by `npm run lint:copy` against rendered HTML.
- Sample data (stats, case studies, buyer rows, phone number, sector multiples) is placeholder. Keep the `(sample)` markers until real data is supplied.

## Valuation tool (must match prototype behaviour)
Inputs: sector, revenue band, profit (owner salary added back), years operating, ownership %, owner dependency, timeline, name, phone, email, PDPA consent.
Logic: EV = normalised EBITDA x sector multiple range (`src/data/multiples.json`), adjust: dependency high -15%, low +5%, years < 3 -10%, revenue < S$1m caps upper multiple at 40% of range.
Score: hot = revenue >= S$3m AND profit > 0 AND timeline <= 18 months AND ownership >= 50%. Warm = revenue S$1-3m or timeline > 18m. Cold = < S$1m.
Hot -> show inline booking + alert team (email/Slack). Warm -> nurture sequence. Cold -> guide download auto-reply.
Endpoint: `POST /api/valuation` -> validate -> score -> CRM upsert -> transactional email with report -> alert if hot. Capture UTM params.
Implementation: `src/scripts/valuation.ts` (client) and `api/valuation.ts` (server). The server re-scores rather than trusting the client.

## Pages built
`/`, `/sell-your-business`, `/valuation`, `/case-studies` + `[slug]`, `/sell/[sector]` (20), `/guides` + `[slug]` (10), `/data/sme-multiples-singapore`, `/buyers`, `/insights` + `[slug]`, `/about`, `/contact`, `/book-a-call`, `/privacy`, `/terms`, `404`.

## Working rules
- Follow `docs/implementation-plan.md` task order. Commit after each task.
- Port the prototype faithfully; do not redesign. Ask before changing layout or copy.
- Every page: title, meta description, canonical, OG image, JSON-LD (Organization/Service/FAQPage/Article as appropriate).
- Run Lighthouse on `/` and `/valuation` before calling phase 1 done. Targets: LCP < 2.5s, CLS < 0.1, a11y >= 95.
- Zero em-dashes in any rendered string. `npm run lint:copy` before commit.
- `npx astro check` must be clean before commit.
