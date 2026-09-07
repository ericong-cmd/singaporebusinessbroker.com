# SEO log

Session record and monthly review for singaporebusinessbroker.com, per Part C
Session 9 of `docs/seo-growth-plan.md`.

**The number that matters is enquiries.** Rankings and impressions are leading
indicators; an owner emailing about selling their business is the outcome. Read
the funnel bottom-up when reviewing: enquiries first, then what fed them.

---

## How the funnel is instrumented

Four conversion events fire from `src/scripts/analytics.ts`:

| Event | Fires when | Why it is separate |
|---|---|---|
| `valuation_instant_result` | The range appears on screen | The visitor got what they came for, whether or not the email sends |
| `valuation_report_requested` | `/api/valuation` accepts the lead | A real contact detail was handed over |
| `book_call_click` | Any link to `/book-a-call` is clicked | Intent above a report request |
| `email_enquiry_click` | Any `mailto:` or `tel:` link is clicked | The success metric itself |

`email_enquiry_click` is caught by one delegated listener in `Base.astro`, so
every one of the site's mailto links is counted and links added later need no
extra wiring. The event carries the page path, which is what tells you *which*
content produced the enquiry. It carries the destination address but never the
prefilled subject or body.

**Plan caveat:** Vercel custom events are a paid feature. On Hobby the calls are
accepted and silently dropped, and the dashboard shows page views only. The
instrumentation is correct and costs nothing to leave in place; the events
appear the moment the account moves to Pro. Until then, count enquiries from the
inbox and read page views for traffic.

Server-side, `/api/valuation` already logs a `delivery` object per submission
(`crm`, `ownerMail`, `teamMail`, `slack`), so lead volume is recoverable from
Vercel function logs independently of any analytics plan.

---

## Session log

| Date | Session | What shipped |
|---|---|---|
| 2026-08-15 | Build | Initial 48-page site, valuation estimator, API endpoints |
| 2026-08-28 | S1 critical fixes | JSON-LD graph, slash unification, sitemap lastmod, multiples page noindexed, alt pass, sector meta descriptions |
| 2026-08-28 | Owner data | Real contact details, published fee, three real case studies replacing four samples |
| 2026-08-30 | E-E-A-T | Founder named with LinkedIn `sameAs`; 31 content pages set `reviewed: true` |
| 2026-08-31 | Portrait, checklist | Founder photo; Vercel region `sin1`, framework preset, Speed Insights, Web Analytics |
| 2026-08-31 | S2 BBIS redirects | 18 host-scoped 308s from `businessbrokerinsingapore.com`, code live, DNS pending |
| 2026-08-31 | S9 measurement | Four conversion events, this log |
| 2026-08-31 | S6.1 quiz | `/exit-readiness`, ten questions scored to 100, not email-gated |
| 2026-08-31 | S4, S5, S6.3 sectors | All 20 sector pages to 1,176-1,774 words, five-question FAQ each, adjacent-sector internal links |
| 2026-08-31 | S6.3 guides | Four-question FAQ and CTA band on all 10 guides |
| 2026-08-31 | S6.2 timeline | Interactive five-stage tabs on `/sell-your-business` |
| 2026-08-31 | Off-site | `docs/offsite-plan.md`: NAP block, directory sweep, TFA cross-link instructions |
| 2026-08-31 | GBP | Profile live with a public street address; `PostalAddress` wired into Organization schema, awaiting the exact address and profile URL |
| 2026-08-31 | Cross-domain | `docs/cross-domain-plan.md`: keyword overlap with TFA mapped, five TFA-to-SBB links specified, one SBB-to-TFA link shipped |
| 2026-09-01 | Navigation | Sector directory added to `/guides` (20 links with ranges), exit-readiness CTA added to the home page after the estimator |
| 2026-09-01 | BBIS audit | Live audit of businessbrokerinsingapore.com; redirect map rebuilt to 50 host-scoped rules covering all 13 indexed URLs in both slash forms |

---

## Monthly review template

Copy this block, fill it, keep the history. Paste GSC numbers in rather than
summarising them: the trend is only readable if the numbers are comparable.

```
## Review: <month year>

### Outcome
Enquiries received (inbox count):
Valuation reports requested:
Calls booked:
Best-performing page for enquiries:

### Search Console (28 days)
Total impressions:            (prev: )
Total clicks:                 (prev: )
Average position:             (prev: )

### Tier 1, sector long-tails
| Keyword | Position | Prev | Page |
|---|---|---|---|
| sell F&B business singapore | | | /sell/fnb |
| is my business ready to sell | | | /exit-readiness |
| sell logistics business singapore | | | /sell/logistics |
| sell manufacturing business singapore | | | /sell/manufacturing |
| business valuation singapore | | | /valuation |
| how much is my business worth singapore | | | /valuation |

### Tier 2, question keywords
| Keyword | Position | Prev | Page |
|---|---|---|---|

### Tier 3, head terms
| Keyword | Position | Prev | Page |
|---|---|---|---|
| sell my business singapore | | | / |
| business broker singapore | | | / |

### Stalled pages
Any Tier-1 page indexed 90+ days and not improving. Diagnose intent, title,
or depth, then rewrite or merge. List the decision, not just the observation.

### Actions for next month
1.
2.
3.
```

---

## Standing notes

- **Kill/iterate rule.** A Tier-1 page indexed 90 days without improvement gets
  diagnosed and rewritten or merged. Log the decision here.
- **Do not cannibalise.** TFA keeps informational intent (how, what, why). This
  site keeps transactional intent (sell, broker, valuation service). Two pages
  competing for one query is worse than either alone. As of 2026-08-31 this
  rule is being broken in two places, both on TFA: a second valuation
  calculator at `/valuation-calculator/` competing with `/valuation` here, and
  a `/buyers/` page competing with ours. See `docs/cross-domain-plan.md` Part 1.
  Resolving that is worth more than any of the cross-links.
- **Honesty constraint.** Every multiple on the site is labelled indicative
  until real transaction data ships. Nothing may imply proprietary data before
  then.


---

## BBIS consolidation status, audited 2026-09-01

**The consolidation has not happened yet.** `www.businessbrokerinsingapore.com`
still returns 200 on every page, serves its own sitemap of 13 URLs, and its
canonicals point at itself. The redirect rules in `vercel.json` are inert
because the BBIS domains are not attached to this Vercel project and its DNS
does not point here.

What BBIS currently does, all of it normal:

| Request | Result |
|---|---|
| `http://businessbrokerinsingapore.com/` | 308 to https, then 308 to www, then 200 |
| `https://businessbrokerinsingapore.com/` | 308 to www, then 200 |
| `/contact` (no trailing slash) | 308 to `/contact/` |

Any "Page with redirect" entries in Search Console for BBIS today are these
three internal normalisations. They are excluded-not-indexed by design, not
errors, and there is nothing to fix on them.

### What the audit did change

The redirect map was written against the growth plan's page list, not against
what BBIS actually publishes. Comparing it to the live sitemap found four
indexed URLs with no rule, all falling through to the homepage catch-all:

| BBIS URL | Was | Now |
|---|---|---|
| `/valuation-estimator/` | homepage | `/valuation` |
| `/exit-readiness/` | homepage | `/exit-readiness` |
| `/singapore-sme-valuation-multiples/` | homepage | `/guides/valuation-methods` |
| `/about/` | homepage | `/about` |

A catch-all to the homepage keeps the visitor but throws away the topical
signal, and Google can treat an irrelevant redirect target as a soft 404. The
`/valuation-estimator/` case was the expensive one: it is BBIS's own valuation
tool, the closest thing it has to a ranking commercial page.

`/singapore-sme-valuation-multiples/` deliberately does **not** point at
`/data/sme-multiples-singapore`, which is still noindexed pending real data.
Redirecting a ranking page into a noindexed one discards the equity. Repoint it
there when Session 8 ships.

### Trailing slashes

Every URL in the BBIS sitemap ends in `/`, and this project sets
`trailingSlash: false`, so a rule written as `/fees` risks a normalisation hop
turning each redirect into a two-step chain. Every mapped path is now listed in
both forms, slash first, so the indexed form matches directly. 50 host-scoped
rules: 12 paths in 2 slash forms plus a catch-all, across the apex and www.

### Still gated on the owner

These rules cannot be tested until the BBIS domains are added to this Vercel
project and DNS is repointed. Sequence: attach domains, move DNS, verify each
of the 13 URLs returns a single 308 to the right destination, then run Change
of Address on the BBIS Search Console property.
