# singaporebusinessbroker.com

Sell-side M&A advisory site for Singapore SME owners. Astro 4 static output,
Tailwind, MDX content collections, and two Vercel serverless endpoints for lead
intake.

Read `CLAUDE.md` first, then `docs/build-notes.md` for what is built and every
deviation from the spec.

## Quick start

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # static output to dist/
npm run preview
```

Before every commit:

```bash
npx astro check      # must be 0 errors
npm run build
npm run lint:copy    # no em-dashes, banned words or placeholders in rendered copy
```

## Layout

```
src/
  components/        Button, Shell (double bezel), Icon, Eyebrow, PageHeader, Faq, Valuation, Nav, Footer
  components/home/   Homepage sections, ported one-for-one from the prototype
  content/           sectors (20), guides (10), cases (4), insights - MDX with zod schemas
  data/              site, stats, buyers, faq, process, multiples - all JSON, all editable without touching code
  layouts/Base.astro Head, JSON-LD, grain overlay, reveal observer
  pages/             Routes. Dynamic: sell/[sector], guides/[slug], case-studies/[slug], insights/[slug]
  scripts/           valuation.ts - the estimator logic and step machine
  styles/global.css  Fonts, grain, reveal, hamburger, prose
api/                 valuation.ts, contact.ts, _lib.ts (Vercel functions)
assets/              images.json manifest, build-images.mjs
tools/               make-og.mjs (share card), lint-copy.mjs
prototype/           The approved design, for reference. Not built or deployed.
docs/                design-spec.md, implementation-plan.md, build-notes.md
```

## Editing content without touching code

- **Sector pages**: `src/content/sectors/*.mdx`. Frontmatter carries the
  structured blocks (why owners sell, who buys, value drivers, pitfalls); the
  MDX body is the closing prose. The `sector` field must match a slug in
  `src/data/multiples.json` or the build fails the schema check.
- **Guides, case studies, insights**: same pattern under `src/content/`.
- **Buyer board, proof strip, FAQ, process steps**: `src/data/*.json`.
- **Multiples**: `src/data/multiples.json` drives the estimator, the sector
  pages, the sector pill list and the data page. Changing a number there
  changes all four. Regenerate the CSV after editing (it is a static file in
  `public/data/`).
- **Contact details, deal range, enquiry link**: `src/data/site.json`.
  `bookingUrl` is a `mailto:` with a pre-filled subject, not a scheduler link.

## The valuation tool

Logic is in `src/scripts/valuation.ts` and mirrored server side in
`api/valuation.ts`, which re-scores rather than trusting the browser. If you
change the formula, change both, because the client shows the number and the
server decides whether the lead is hot.

The estimate always renders even if the API is unreachable; only the emailed
report depends on the network.

## Integrations

All optional, all environment variables, all no-ops when unset. Copy
`.env.example` and fill in what you have:

| Variable | Effect when set |
|---|---|
| `RESEND_API_KEY`, `MAIL_FROM` | Emails the report to the owner |
| `TEAM_EMAIL` | Hot-lead alerts and contact enquiries |
| `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE` | CRM upsert (swap `crmUpsert` in `api/_lib.ts` for HubSpot) |
| `SLACK_WEBHOOK_URL` | Hot-lead Slack alert |
| `PUBLIC_PLAUSIBLE_DOMAIN` | Adds the analytics script at build time |

With none set the endpoints still validate, score and return 200, so the site
works on a fresh deployment and nothing is silently lost from the front end's
point of view. Check the function logs for `delivery` fields.

Setting `PUBLIC_PLAUSIBLE_DOMAIN` also requires widening the CSP in
`vercel.json` to allow `plausible.io` in `script-src` and `connect-src`.
Without it the site loads nothing from a third-party origin, which is why the
policy can be as tight as it is.

## Deployment

Vercel builds from source so the `api/` functions are compiled alongside the
static output. `main` deploys via `.github/workflows/deploy.yml`, which type
checks, builds and lints the copy first. Needs the `VERCEL_TOKEN` repository
secret. The same script runs locally:

```bash
VERCEL_TOKEN=... python3 deploy_vercel.py
```

DNS at the registrar:

| Type | Name | Value |
|---|---|---|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com |

The apex 308-redirects to `www`.

If you change the inline bootstrap script in `Base.astro`, recompute its
SHA-256 and update `script-src` in `vercel.json`, or every page breaks under
CSP.

## Images

`npm run images` downloads the sources in `assets/images.json`, repairs the
defective hero and emits sized webp. `npm run og` rebuilds the share card and
touch icon (needs Playwright installed separately, see the script). Both are
content tooling, not build steps; the outputs are committed.

Two of the five supplied photographs had hallucinated text baked in and are
handled specially. `docs/build-notes.md` explains what was done and what to
replace.
