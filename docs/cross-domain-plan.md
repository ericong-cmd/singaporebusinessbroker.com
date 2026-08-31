# Cross-domain plan: thefundingassembly.com and singaporebusinessbroker.com

You own both domains. This covers how to link them, and one problem that has to
be fixed first.

**What I could implement:** the singaporebusinessbroker.com side only. TFA is
hosted on AWS outside this repository, so every TFA edit below is written as a
copy-paste instruction rather than code.

---

## Part 1: Fix the keyword overlap first

This matters more than the links, and doing the links first would make it worse.

The two sites currently compete for the same queries. When two domains you own
target one query, Google picks one and suppresses the other. It usually picks
the older, stronger domain, which is TFA. That means the site you want people to
enquire through is being outranked by your own other site.

### Where they collide

| Query intent | TFA page | SBB page | Who should win |
|---|---|---|---|
| what is my business worth, valuation calculator | `/valuation-calculator/` | `/valuation` | **SBB.** It is the funnel. |
| how to value a business in singapore | `/articles/how-to-value-a-business-in-singapore/` | `/guides/valuation-methods` | **TFA.** Informational. |
| business valuation multiples by industry | `/articles/business-valuation-multiples-singapore/` | `/data/sme-multiples-singapore` | **TFA for now.** SBB's page is noindexed until real data ships, so there is no live conflict yet. Revisit at Session 8. |
| what does a business broker do | `/articles/who-are-business-brokers.../` | `/` | **Split.** TFA keeps the explainer, SBB keeps "business broker singapore". |
| mistakes when selling an SME | `/articles/10-hard-truths.../` | `/guides/common-mistakes` | **TFA.** It is the stronger piece. |
| buyers looking to acquire | `/buyers/` | `/buyers` | **Decide.** See below. |
| ebitda vs sde | `/articles/ebitda-vs-sde-business-valuation/` | none | TFA, uncontested. Good. |

### The rule, restated

TFA keeps **informational** intent: how, what, why, explainers, frameworks.
SBB keeps **transactional** intent: sell, broker, valuation service, sector pages.

TFA currently breaks this in two places, and both are worth acting on.

**1. The valuation calculator.** This is the clearest problem. TFA runs a
calculator at `/valuation-calculator/` and SBB runs one at `/valuation`. They
target the same query, and SBB's is the one wired to your lead pipeline, hot
lead alerts and report email.

Recommended fix, in order of preference:

- **Best:** 301 redirect `thefundingassembly.com/valuation-calculator/` to
  `https://www.singaporebusinessbroker.com/valuation`. One tool, all the signals
  consolidated onto the funnel, no work maintaining two calculators.
- **If you want to keep the TFA tool:** add
  `<link rel="canonical" href="https://www.singaporebusinessbroker.com/valuation">`
  to the TFA calculator page. The page keeps working for anyone already on TFA,
  but search consolidates to SBB.
- **Do nothing:** the two keep splitting the query and neither ranks as well as
  one would.

**2. The buyers pages.** Both sites have one. Decide which audience each serves:
if TFA is the platform where buyers register, keep TFA's and point SBB's at it;
if SBB is where sellers learn who the buyers are, they are actually different
pages serving different readers and can coexist. Look at both and pick, rather
than leaving it unexamined.

**3. Where TFA should win, help it win.** For `how to value a business in
singapore` and the `10 hard truths` piece, SBB's competing guides should not be
strengthened further. They stay as supporting content and internal link targets,
which is what they are already doing.

---

## Part 2: The cross-links

Only after Part 1. Six links, all editorial, all in-body.

### Why only six

You own both domains, so restraint is not modesty, it is risk management.
A handful of contextual links between two genuinely related brands is normal.
Sitewide footer links, matching exact-match anchors on every page, or dozens of
reciprocal links start to look like a link scheme, and the downside is a manual
action against the domain that is your only lead funnel.

Rules for all of them: real `<a href>` elements, descriptive anchors, no
`nofollow`, no "click here", placed where the text already raises the question.

### TFA to SBB (the five that matter)

These are the links that pass authority in the direction you need it.

**1. In `/articles/how-to-value-a-business-in-singapore/`**

Under **Step 2: Apply your industry multiple**, after "Every industry trades
within a typical range of multiples.":

```html
<p>Ranges vary widely by sector. Our sell-side practice publishes
<a href="https://www.singaporebusinessbroker.com/sell/fnb">indicative multiple ranges sector by sector</a>,
with what moves a business within each range.</p>
```

**2. In the same article**

Under **Step 4: Read the range, then pressure-test it**, after "The output of
this exercise is a range, not a single number.":

```html
<p>If you would rather not do the arithmetic by hand, you can
<a href="https://www.singaporebusinessbroker.com/valuation">get an indicative range in about two minutes</a>
and have the full report emailed to you.</p>
```

**3. In `/articles/10-hard-truths-about-selling-your-sme-in-singapore-and-how-to-prepare/`**

Under **8. Owner Dependency Is a Deal Killer**:

```html
<p>Owner dependency is one of ten factors a buyer verifies before pricing.
The <a href="https://www.singaporebusinessbroker.com/exit-readiness">exit-readiness check</a>
scores all ten and takes about three minutes.</p>
```

**4. In the same article**

Under **10. Founders Must Be Ready to Let Go**, near "Start early — ideally
12–24 months before your intended exit.":

```html
<p>What to do with those months is specific rather than general.
<a href="https://www.singaporebusinessbroker.com/guides/preparing-to-sell">This preparation guide</a>
sets out the work in the order that moves the price most.</p>
```

**5. In `/articles/ebitda-vs-sde-business-valuation/`**

Wherever the article explains applying a multiple to the chosen earnings figure:

```html
<p>Whichever measure you use, the multiple applied to it is sector-specific.
See <a href="https://www.singaporebusinessbroker.com/guides/valuation-methods">how Singapore SME valuations are actually built</a>.</p>
```

### SBB to TFA (one link, and only one)

I have implemented a single outbound link, from `/guides/valuation-methods` to
TFA's EBITDA vs SDE article.

One, not five, and the reason is worth stating. Outbound links pass authority
away. SBB is the weaker domain and the one you need to rank, so linking it out
to a domain that competes with it on the same queries would be working against
yourself. The one link that survives that test is EBITDA vs SDE, because SBB
does not cover SDE anywhere and has no intention of ranking for it, so the link
is genuinely useful to the reader and costs nothing strategically.

The parent relationship is already expressed twice more, in the footer and on
`/about`, and structurally through `parentOrganization` in the Organization
schema. That is sufficient reciprocity. It does not need reinforcing.

---

## Part 3: Measuring whether it works

Already built, no action needed. The valuation form captures `document.referrer`
for any off-site referrer and passes it to `/api/valuation`, which records it as
`Referrer` in the lead payload and the function log.

So a lead that arrives from a TFA article is attributable without UTM tags. Do
not add UTM parameters to these links: they would append query strings to URLs
you want indexed cleanly, and they are unnecessary when the referrer is already
captured.

To see it: Vercel dashboard, Deployments, the current deployment, Functions,
`api/valuation`. The `Referrer` field shows the TFA article that produced the
lead.

---

## Order of work

1. Decide the valuation calculator question. Redirect or canonical.
2. Decide the buyers page question.
3. Add the five TFA to SBB links.
4. Check each renders as a real `<a href>` in the published HTML, not a
   JavaScript handler, or it will not be crawled.
5. Log the date in `docs/seo-log.md`.
6. From then on, one new TFA article a month, informational, each with one
   contextual link to a money page here.

Step 1 is worth more than steps 3 through 6 combined.
