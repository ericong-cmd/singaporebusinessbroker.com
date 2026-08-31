# Off-site plan: citations, cross-links and outreach

Part D of `docs/seo-growth-plan.md`, written out as executable tasks.

## What I cannot do, and why it matters

**I cannot build backlinks.** Every item in this document requires someone to
log into an account, submit a form, publish on a domain I do not control, or
speak to a person. There is no code path to any of it.

That is not a limitation worth working around, it is the point. The link
building that can be automated is exactly the link building that does not work
and that Google's spam policies target directly. Directory spam, paid link
placements, private blog networks and reciprocal link schemes are all link
spam under those policies, and the downside is not a wasted afternoon, it is a
manual action against a domain that is your only lead funnel.

So what follows is the honest version: a small number of citations that are
legitimate because they are true, one cross-link opportunity you already own,
and a content asset that can earn links on merit. Everything below needs your
hands.

What I have done instead is build the things links point at: 27,000 words of
sector content, a free readiness tool, a valuation estimator, and an FAQ layer
across 30 pages designed to be quoted by answer engines. Citations amplify
that. They do not substitute for it.

---

## 1. NAP consistency (do this before any submission)

Every listing must use these strings **character for character**. Inconsistent
name, address or phone across citations is the most common reason local signals
fail to consolidate, and it is entirely self-inflicted.

```
Name:     Singapore Business Broker
Phone:    +65 8951 8821
Website:  https://www.singaporebusinessbroker.com
Email:    singaporebusinessbroker@thefundingassembly.com
Entity:   The Funding Assembly Pte Ltd
```

Note the two things people get wrong: the website has `www` and no trailing
slash, and the name is not "Singapore Business Broker Pte Ltd", because that is
not the legal entity. Where a directory demands a legal entity name, use
`The Funding Assembly Pte Ltd` and put `Singapore Business Broker` in the
trading or brand name field.

**Address decision still outstanding.** Several directories require a street
address, and Google Business Profile effectively does. Until you decide whether
to publish one, those listings cannot be completed consistently. See the
`ERIC-TODO` marker in `src/lib/schema.ts` where the `PostalAddress` block goes.

### Description blocks to paste

Keep these consistent too. Short version, for fields with tight limits:

> Sell-side M&A advisory for Singapore SME owners. We advise on business sales
> from S$3m to S$30m, with a free valuation estimate and a confidential process.

Long version, where a paragraph is allowed:

> Singapore Business Broker is the sell-side M&A practice of The Funding
> Assembly Pte Ltd. We act for Singapore SME owners selling businesses valued
> between S$3m and S$30m, running a confidential process from valuation through
> buyer approach to completion. Our fee is success-based at 1 to 5 percent with
> no upfront cost and a S$100,000 minimum. A free valuation estimator is
> available at singaporebusinessbroker.com/valuation.

---

## 2. Directory and citation sweep

Ordered by value. These are legitimate because we genuinely are what we would
be claiming to be, which is the test that separates a citation from spam.

| Priority | Where | What to do | Notes |
|---|---|---|---|
| 1 | Google Business Profile | Create, verify, use the NAP block above | Needs the address decision. Then paste the URL into `profiles.googleBusinessProfile` in `src/data/site.json` and I will wire it into `sameAs` |
| 2 | LinkedIn company page | Create or claim, website field set to the URL above | Also set the **Website** field on your personal profile to the site, which makes the `sameAs` link on `/about` reciprocal |
| 3 | Bing Places | Import from Google Business Profile once live | Two minutes once GBP exists |
| 4 | SMERGERS | Broker profile | Genuine deal-flow value beyond the link |
| 5 | BusinessForSale.sg | Broker listing | Same |
| 6 | Singapore Business Federation | Membership listing if TFA is a member | Only if genuinely a member |
| 7 | Flippa broker directory | Broker profile | Lower relevance to S$3m to S$30m deals, still legitimate |

Do not buy listings on general "top 10 companies in Singapore" sites. They are
paid placements, they carry no weight, and the sites they sit on are frequently
already discounted.

**After each submission**, note the date and URL in the log below, because you
will need to update all of them if the phone number or address ever changes.

| Directory | Submitted | Live URL | Verified |
|---|---|---|---|
| | | | |

---

## 3. The Funding Assembly cross-links (Session 7)

This is the single highest-value off-site item available, because you control
both ends and the linking domain is topically relevant with existing authority.

It runs in the **thefundingassembly.com** repository or CMS, which this session
cannot reach, so it is written as instructions rather than code.

### 3.1 Edit the two already-ranking articles

Add one or two contextual in-body links each. Place them mid-article where the
text naturally raises the question, never in a footer or a link block.

**Article: how to sell a business in Singapore**
- Where the article discusses working out what a business is worth, link the
  phrase "get an indicative range" to
  `https://www.singaporebusinessbroker.com/valuation`
- Where it discusses whether a business is ready, link "ten point readiness
  check" to `https://www.singaporebusinessbroker.com/exit-readiness`

**Article: how to value a business in Singapore**
- Where sector multiples are mentioned, link "sector by sector multiple ranges"
  to the relevant `https://www.singaporebusinessbroker.com/sell/<sector>` page
- Where normalised earnings are explained, link to
  `https://www.singaporebusinessbroker.com/guides/valuation-methods`

Requirements: real `<a href>` elements, not JavaScript click handlers, or they
will not be crawled. Descriptive anchor text, never "click here". No `nofollow`.

### 3.2 Keep the two sites off each other's keywords

The rule, so the sites do not compete with each other:

- **TFA keeps informational intent.** How, what, why. Explanatory articles.
- **This site keeps transactional intent.** Sell, broker, valuation service.

Two pages from the same owner competing for one query is worse than either
alone, and Google will pick one for you if you do not pick for yourself.

### 3.3 Ongoing

One new TFA article per month, informational, each linking once to a money page
here. That is a link a month from a relevant domain, permanently, at no cost.

---

## 4. Earning links rather than placing them

The only durable link building is publishing something worth citing. Two assets
are close to ready.

**The multiples dataset.** Blocked until you supply real transaction data or
agree a documented public-sources methodology. This is the asset with genuine
press potential: Singapore SME transaction multiples by sector, updated
quarterly, is a story SGSME, Business Times SME and DollarsAndSense could each
run. It is also the item most likely to attract natural links from accountants
and corporate finance blogs. See Session 8 of the growth plan.

**The exit-readiness check.** Already live. A free scoring tool with no email
gate is linkable in a way a services page is not. Worth mentioning in any
conversation with an accountant, lawyer or corp sec who advises SME owners,
because it is genuinely useful to their clients and costs them nothing to share.

### Referral partner outreach

Accountants, corporate secretaries and SME lawyers are the highest-quality
referral source in this business, and the link is a secondary benefit to the
referral itself. A template that does not read like outreach:

> Subject: A free valuation tool your SME clients might use
>
> Hi [name],
>
> We advise Singapore SME owners on selling their businesses, typically in the
> S$3m to S$30m range. We have put a free valuation estimator and a ten point
> exit-readiness check on our site, both of which give a result immediately with
> no email required.
>
> A fair number of your clients are probably two or three years from thinking
> about an exit, and these give them a straight answer without a sales call.
> Happy for you to point anyone at them.
>
> If it is ever useful, I am glad to look at a specific situation informally.
>
> [signature with the NAP block]

Send individually. A mail merge to fifty accountants is spam and reads like it.

---

## 5. What to expect, honestly

The growth plan puts head terms at nine to twelve months, and that is realistic
rather than pessimistic. "Business broker singapore" is contested by
established domains. What should move sooner is the long-tail: sector queries
like "sell F&B business singapore" and question queries like "how long does it
take to sell a business in Singapore", which the sector and FAQ content is
built for.

Track it in `docs/seo-log.md`, monthly, and judge the content by enquiries
rather than by position. A page ranking third and producing no email is worth
less than a page ranking eleventh that produces two.
