# singaporebusinessbroker.com — Site Design Spec

Date: 2026-08-15
Owner: Eric Ong (The Funding Assembly)
Status: Approved design, pending implementation plan

## 1. Objective

Generate high-quality inbound leads from Singapore SME owners who want to sell their business. "High quality" = revenue >= S$3m, profitable, realistic timeline (<= 18 months), owner is decision-maker.

Not a marketplace. Not a broker directory. Not a ranking site. A sell-side M&A advisory brand site whose every page funnels toward one action: get a valuation estimate, then book a confidential call.

## 2. Market context (SME M&A, Singapore, < S$30m)

- ~300k SMEs; large cohort of founder-owners aged 55+ with no successor. Succession is the #1 sale trigger; others: burnout, partner exit, PE roll-up cash-out, distress.
- Size bands:
  - < S$1m (F&B, retail, sole props): high volume, low fee, low lead quality. Out of scope except nurture/referral.
  - S$1-5m (services, trading, clinics, education, logistics): viable, fee 5-10% of EV.
  - S$5-30m (lower mid-market): PE bolt-ons, regional strategics, search funds, family offices. Retainer + success fee.
- Buyers: regional strategics, PE platforms, search funds, HNW individuals, foreign buyers seeking SG presence.
- Competitive gap: listing sites serve buyers and DIY sellers; Big 4 / boutique corporate finance start above ~S$30m. Credible sell-side advisor for S$3-30m is underserved.
- Domain is exact-match for "singapore business broker": strong SEO asset for seller-intent queries.

## 3. Positioning

- Brand: Singapore Business Broker. Standalone broker brand under The Funding Assembly (TFA fulfils; TFA credited in footer/about, separate identity).
- Audience: SME owners, S$3-30m revenue or transaction value.
- Promise: confidential, well-run sale process; buyer network; price maximisation.
- Proof: anonymised closed deals / case studies, team credentials, buyer network, methodology.
- Rejected models and why:
  - Business listing marketplace: attracts buyers and fee-avoiding DIY sellers; chicken-and-egg; ops heavy.
  - Broker directory / ranking: seller intent but leads leak to competitors; self-ranking #1 destroys trust.
  - Business-for-sale ranking: buyer traffic only.
- Later (phase 3+): editorial "how to choose a business broker in Singapore" content to catch broker-shopping sellers. Content, not a directory.

## 4. Site map

| Route | Purpose |
|---|---|
| `/` | Home: hero + valuation CTA, proof strip, process, case studies, FAQ, call CTA |
| `/sell-your-business` | Primary money page: process, why us, fee model, timeline, confidentiality |
| `/valuation` | Free valuation estimator (see section 5) |
| `/case-studies`, `/case-studies/[slug]` | Anonymised deals: sector, size band, buyer type, outcome |
| `/sell/[sector]` | ~20 sector landing pages (F&B, logistics, manufacturing, education, healthcare/clinics, IT services, construction, trading/distribution, retail, cleaning/security services, marine/offshore, professional services, e-commerce, engineering, printing/packaging, beauty/wellness, childcare, interior/renovation, automotive, events/media) |
| `/guides/[slug]` | Exit guides: preparing to sell, succession planning, valuation methods, deal structures, earn-outs, tax and stamp duty, NDAs and confidentiality, sale timeline, common mistakes, share vs asset sale |
| `/data/sme-multiples-singapore` | Quarterly SME EBITDA/revenue multiples by sector; backlink magnet |
| `/buyers` | Buyer-demand board ("Buyer seeking F&B chain, S$5-15m") + buyer registration form (secondary lead stream, demonstrates demand to sellers) |
| `/insights`, `/insights/[slug]` | Blog / articles |
| `/about`, `/contact`, `/book-a-call` | Team, contact, Cal.com booking |
| `/privacy`, `/terms` | PDPA-compliant privacy, terms |

## 5. Valuation tool

Inputs (multi-step form):
1. Sector (dropdown, maps to multiple range)
2. Annual revenue band (< S$1m, 1-3m, 3-5m, 5-10m, 10-30m, > 30m)
3. EBITDA or net profit (number or band)
4. Years operating
5. Owner dependency (low / medium / high)
6. Timeline to sell (< 6mo, 6-12mo, 12-18mo, > 18mo, exploring)
7. Ownership % held by respondent
8. Name, email, phone, PDPA consent (gated before result)

Logic:
- Base EV = normalised EBITDA x sector multiple range (low/high from multiples table, maintained as JSON in repo).
- Adjustments: owner dependency high -> -15%; size < S$1m revenue -> lower end of range; years < 3 -> -10%.
- Output: instant on-screen range (e.g. "S$4.2m - S$6.1m") with one-line explanation; full PDF report emailed.

Lead scoring:
- Hot: revenue >= S$3m AND profitable AND timeline <= 18mo AND ownership >= 50% -> show Cal.com booking inline, alert team (Slack/email), human follow-up within 24h.
- Warm: revenue S$1-3m or timeline > 18mo -> nurture sequence (6 emails: prep, timing, buyer types, valuation drivers, mistakes, invite to call).
- Cold: revenue < S$1m -> auto-reply with guide download; optional partner referral.

## 6. Funnel and CRM

- Forms -> serverless endpoint -> CRM (HubSpot free tier or Airtable) -> alerts. UTM captured on every submission.
- Email: Resend or HubSpot for transactional + nurture.
- Booking: Cal.com or Calendly embedded on `/book-a-call` and inline for hot leads.
- Analytics: Plausible or GA4; events for valuation start/complete, booking, form submit.
- PDPA: explicit consent checkbox, privacy policy, data stored in CRM only.

## 7. SEO and content engine

Primary keywords: sell my business singapore, business valuation singapore, business broker singapore, how much is my business worth, sell [sector] business singapore, M&A advisor SME singapore, business succession singapore, business for sale singapore (informational angle only).

Launch content: 20 sector pages, 10 guides, 3-5 case studies, multiples data v1.
Ongoing: 1-2 articles/week, AI-drafted, human-edited, committed as Markdown/MDX via PR.
Technical: schema (Organization, Service, FAQPage, Article, LocalBusiness), sitemap, canonical, OG images, Core Web Vitals green.
Off-page: Google Business Profile, multiples report outreach, SME associations (ASME, SBF), LinkedIn distribution, guest posts on SG business media.

## 8. Tech stack

- Framework: Astro (content-heavy, fast, MDX). Next.js acceptable if team prefers.
- Styling: Tailwind CSS.
- Content: Markdown/MDX in repo (`src/content/`), sector and guide collections.
- Valuation: client-side calc; serverless endpoint (Cloudflare Workers / Vercel Functions) for scoring, CRM push, email trigger, PDF generation.
- Hosting: Cloudflare Pages or Vercel. Git repo (GitHub).
- Integrations: HubSpot/Airtable, Resend, Cal.com, Plausible/GA4.

## 9. Phases

1. Weeks 1-2: brand basics, copy for core pages, valuation v1, CRM + email wiring, analytics, legal pages.
2. Weeks 3-4: 20 sector pages, 10 guides, case studies, multiples data v1, buyer board.
3. Week 5+: launch; Google Business Profile; backlink outreach; weekly content; paid test (Google Ads on seller-intent keywords, LinkedIn); CRO on valuation funnel.

## 10. KPIs

- Hot leads / month (primary)
- Valuation completions, completion rate
- Call bookings, show rate
- Cost per hot lead (paid)
- Organic rankings for primary keywords, organic sessions

## 11. Out of scope

- Public business listings / marketplace
- Broker directory or rankings
- Buyer-side deal room or data room
