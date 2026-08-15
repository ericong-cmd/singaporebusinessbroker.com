#!/usr/bin/env python3
"""Static site generator for www.singaporebusinessbroker.com.

Emits every page from one shared shell so navigation, schema and CTAs stay
consistent. No dependencies, no build tooling — run `python3 build.py` and
commit the generated HTML.
"""
import json
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.singaporebusinessbroker.com"
NAME = "Singapore Business Broker"
WA_NUMBER = "6589518821"
WA_DISPLAY = "+65 8951 8821"
EMAIL = "eric.ong@thefundingassembly.com"
PARENT = "The Funding Assembly"
PARENT_URL = "https://www.thefundingassembly.com"
LASTMOD = "2026-08-15"

# ---------------------------------------------------------------- helpers

def wa(text):
    return "https://wa.me/%s?text=%s" % (WA_NUMBER, quote(text))


WA_SELLER = wa("Hi, I own a business in Singapore and I'd like a confidential "
               "conversation about selling it. Nothing urgent — I'm exploring.")
WA_BUYER = wa("Hi, I'm looking to acquire a business in Singapore. "
              "Could you tell me what mandates you're working on?")
WA_QUESTION = wa("Hi, I have a question about selling a business in Singapore.")

WA_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
           '<path d="M17.5 14.4c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 '
           '1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61'
           '.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.68-1.62-.93-2.22-.24-.58-.49-.5-.67-.51'
           'h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.5 0 1.47 1.07 2.9 1.22 3.1.15.2 2.1 3.2 5.08 4.49.71.3 '
           '1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.42.25-.7.25-1.3.18-1.42-.08-.13-.28-.2-.58-.35z'
           'M12.05 21.8h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.82 9.82 0 0 1-1.51-5.26c0-5.45 '
           '4.44-9.88 9.9-9.88a9.82 9.82 0 0 1 7 2.9 9.82 9.82 0 0 1 2.9 7c0 5.44-4.45 9.87-9.9 9.87zm8.42-18.3A11.8 '
           '11.8 0 0 0 12.04 0C5.46 0 .1 5.35.1 11.92c0 2.1.55 4.15 1.6 5.96L0 24l6.27-1.64a11.94 11.94 0 0 0 5.77 '
           '1.47c6.58 0 11.94-5.35 11.94-11.92 0-3.18-1.24-6.18-3.5-8.42z"/></svg>')

CHECK = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
         '<path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>')

CHEV = ('<svg class="chev" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>')


def icon(paths, fill=False):
    mode = ('fill="currentColor"' if fill
            else 'fill="none" stroke="currentColor" stroke-width="1.6" '
                 'stroke-linecap="round" stroke-linejoin="round"')
    return ('<svg width="24" height="24" viewBox="0 0 24 24" %s aria-hidden="true">%s</svg>'
            % (mode, paths))


I_LOCK = icon('<rect x="4" y="10" width="16" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>')
I_SHIELD = icon('<path d="M12 3l7 4v5c0 4.5-3 8-7 9-4-1-7-4.5-7-9V7z"/><path d="M9.3 12l2 2 3.4-3.6"/>')
I_DOC = icon('<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>'
             '<path d="M8.5 14h7M8.5 17.5h4"/>')
I_SCALE = icon('<path d="M12 4v16M7 20h10M5 8h14"/><path d="M5 8 2.5 14a3 3 0 0 0 5 0z"/>'
               '<path d="M19 8l2.5 6a3 3 0 0 1-5 0z"/><circle cx="12" cy="5" r="1.4"/>')
I_CHART = icon('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>')
I_USERS = icon('<circle cx="9" cy="8" r="3.2"/><path d="M3 19c0-3.1 2.7-5 6-5s6 1.9 6 5"/>'
               '<path d="M16.5 6.2a3 3 0 0 1 0 5.6M18 19c0-2.1-.8-3.7-2-4.6"/>')
I_CLOCK = icon('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>')
I_HAND = icon('<path d="M12 21a9 9 0 1 0-9-9"/><path d="M3 12H1.5M3 12l2.5-2.5M3 12l2.5 2.5"/>'
              '<path d="M9 12h6M12 9v6"/>')


def faq_block(items):
    out = ['<div class="faq">']
    for i, (q, a) in enumerate(items):
        out.append(
            '<div class="faq-item">'
            '<button class="faq-q" aria-expanded="false" aria-controls="fa-%d">'
            '<span>%s</span>%s</button>'
            '<div class="faq-a" id="fa-%d">%s</div>'
            '</div>' % (i, q, CHEV, i, ''.join('<p>%s</p>' % p for p in a))
        )
    out.append('</div>')
    return '\n'.join(out)


def faq_schema(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip_tags(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip_tags(' '.join(a))}}
            for q, a in items
        ],
    }


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


# ---------------------------------------------------------------- shell

NAV = [
    ("/sell-a-business-singapore/", "Sell"),
    ("/business-valuation-singapore/", "Valuation"),
    ("/exit-planning-singapore/", "Exit Planning"),
    ("/process/", "Process"),
    ("/fees/", "Fees"),
    ("/buy-a-business-singapore/", "Buy"),
]
NAV_EXTRA = [
    ("/sale-readiness/", "Sale-Readiness Scorecard"),
    ("/faq/", "FAQ"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
]

ORG_SCHEMA = {
    "@type": "ProfessionalService",
    "@id": SITE + "/#org",
    "name": NAME,
    "alternateName": "The Funding Assembly",
    "url": SITE + "/",
    "description": ("Sell-side business brokerage and M&A advisory for Singapore SME owners. "
                    "Success-only fees of 1–5%, no upfront cost, confidential no-name marketing "
                    "and buyers screened before any disclosure."),
    "areaServed": {"@type": "Country", "name": "Singapore"},
    "serviceType": ["Business brokerage", "Sell-side M&A advisory", "Business valuation",
                    "Exit and succession planning", "Buy-side search"],
    "knowsAbout": ["business brokerage Singapore", "SME mergers and acquisitions",
                   "business valuation", "EBITDA normalisation", "business succession planning",
                   "due diligence", "share sale agreements"],
    "priceRange": "Success fee 1%–5% of transaction value; minimum SGD 100,000; no upfront fees",
    "telephone": "+6589518821",
    "email": EMAIL,
    "parentOrganization": {"@type": "Organization", "name": PARENT, "url": PARENT_URL},
}

WEBSITE_SCHEMA = {
    "@type": "WebSite",
    "@id": SITE + "/#website",
    "url": SITE + "/",
    "name": NAME,
    "inLanguage": "en-SG",
    "publisher": {"@id": SITE + "/#org"},
}


def breadcrumb_schema(crumbs):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    for i, (path, label) in enumerate(crumbs, start=2):
        items.append({"@type": "ListItem", "position": i, "name": label, "item": SITE + path})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def header_html(active):
    links = '\n'.join(
        '        <li><a href="%s"%s>%s</a></li>'
        % (p, ' aria-current="page"' if p == active else '', l)
        for p, l in NAV)
    mob = '\n'.join('    <a href="%s"%s>%s</a>' % (p, ' aria-current="page"' if p == active else '', l)
                    for p, l in NAV + NAV_EXTRA)
    return """<header class="site-header">
  <div class="nav-wrap">
    <a class="brand" href="/">
      <span class="brand-name">Singapore Business <em>Broker</em></span>
      <span class="brand-sub">Sell-side M&amp;A for SME owners</span>
    </a>
    <nav aria-label="Main">
      <ul class="nav-links">
%s
      </ul>
    </nav>
    <a class="btn btn-primary nav-cta" href="/contact/">Confidential enquiry</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav">
      <svg class="ico-open" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      <svg class="ico-close" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>
    </button>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile">
%s
    <a class="btn btn-wa" href="%s">%s WhatsApp &mdash; confidential</a>
  </nav>
</header>""" % (links, mob, WA_QUESTION, WA_ICON)


FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="foot-grid">
      <div class="foot-brand">
        <span class="brand-name">Singapore Business Broker</span>
        <p>The sell-side brokerage practice of {parent}. Founder-led, success-only, and built so a confidential sale stays confidential.</p>
      </div>
      <div>
        <h2>Sellers</h2>
        <ul>
          <li><a href="/sell-a-business-singapore/">Sell a business</a></li>
          <li><a href="/business-valuation-singapore/">Business valuation</a></li>
          <li><a href="/exit-planning-singapore/">Exit &amp; succession planning</a></li>
          <li><a href="/sale-readiness/">Sale-readiness scorecard</a></li>
        </ul>
      </div>
      <div>
        <h2>The firm</h2>
        <ul>
          <li><a href="/process/">The seven stages</a></li>
          <li><a href="/fees/">Fees</a></li>
          <li><a href="/buy-a-business-singapore/">For buyers</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/faq/">FAQ</a></li>
        </ul>
      </div>
      <div>
        <h2>Talk to us</h2>
        <ul>
          <li><a href="{wa}">WhatsApp {wa_display}</a></li>
          <li><a href="mailto:{email}">{email}</a></li>
          <li><a href="/contact/">Contact page</a></li>
          <li><a href="{parent_url}" rel="noopener">{parent}</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; 2026 {parent}. Singapore.</span>
      <span>Nothing on this site is financial, legal or tax advice. Figures shown are market ranges, not a promise of price or outcome.</span>
    </div>
  </div>
</footer>

<div class="action-bar">
  <a class="wa" href="{wa}">{wa_icon} WhatsApp</a>
  <a href="/contact/">Confidential enquiry</a>
</div>""".format(parent=PARENT, parent_url=PARENT_URL, wa=WA_SELLER,
                 wa_display=WA_DISPLAY, email=EMAIL, wa_icon=WA_ICON)


SHELL = """<!DOCTYPE html>
<html lang="en-SG">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="en_SG">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0E3B2E">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/sourceserif4-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
<noscript><style>
.faq-a{{display:block!important}}.faq-q .chev{{display:none}}
.tool-actions,.score-out{{display:none!important}}.nojs-note{{display:block!important}}
</style></noscript>
<script type="application/ld+json">
{schema}
</script>
</head>
<body>
<script>document.documentElement.className+=' js';</script>
<a class="skip-link" href="#main">Skip to content</a>
<div id="top-sentinel"></div>
{header}
<main id="main">
{body}
</main>
{footer}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def cta_band(heading, lead, primary_label, primary_href, note):
    return """<section class="cta-band">
  <div class="container">
    <div class="cta-inner">
      <div class="reveal">
        <span class="eyebrow">Next step</span>
        <h2>%s</h2>
        <p class="lead">%s</p>
      </div>
      <div class="cta-side reveal" style="--i:1">
        <a class="btn btn-wa" href="%s">%s %s</a>
        <a class="btn btn-brass" href="%s">%s</a>
        <a class="btn btn-ghost" href="mailto:%s">Email instead</a>
        <p class="fineprint">%s</p>
      </div>
    </div>
  </div>
</section>""" % (heading, lead, WA_SELLER, WA_ICON, "WhatsApp " + WA_DISPLAY,
                 primary_href, primary_label, EMAIL, note)


def page_hero(crumbs, h1, lead, buttons=""):
    crumb_html = ""
    if crumbs:
        parts = ['<a href="/">Home</a>']
        for path, label in crumbs[:-1]:
            parts.append('<a href="%s">%s</a>' % (path, label))
        parts.append(crumbs[-1][1])
        crumb_html = '<p class="crumbs">%s</p>' % '<span>/</span>'.join(parts)
    return """<section class="page-hero">
  <div class="container">
    %s
    <h1>%s</h1>
    <p class="lead">%s</p>
    %s
  </div>
</section>""" % (crumb_html, h1, lead, buttons)


def answer_section(paras):
    return """<section class="on-stone" style="padding-top:2.75rem;padding-bottom:2.75rem">
  <div class="container">
    <div class="answer reveal">
      %s
    </div>
  </div>
</section>""" % ''.join('<p>%s</p>' % p for p in paras)


# ---------------------------------------------------------------- shared content

MULTIPLES_TABLE = """<div class="table-wrap">
  <table>
    <caption>Indicative enterprise-value multiples of adjusted EBITDA for Singapore SMEs. Ranges, not quotes — the actual number depends on growth, owner dependence, customer concentration and quality of earnings.</caption>
    <thead><tr><th scope="col">Sector</th><th scope="col">Typical range</th><th scope="col">What moves you to the top of the range</th></tr></thead>
    <tbody>
      <tr><td>Software &amp; technology</td><td>4&times; &ndash; 9&times;</td><td>Recurring revenue, low churn, documented IP</td></tr>
      <tr><td>Healthcare &amp; education</td><td>4&times; &ndash; 7&times;</td><td>Licences transferable, clinician or teacher retention</td></tr>
      <tr><td>Manufacturing &amp; engineering</td><td>3&times; &ndash; 6&times;</td><td>Owned equipment, certifications, long-standing OEM contracts</td></tr>
      <tr><td>Professional &amp; B2B services</td><td>3&times; &ndash; 6&times;</td><td>Contracted or retained revenue, a team that owns the clients</td></tr>
      <tr><td>Logistics &amp; transport</td><td>3&times; &ndash; 5.5&times;</td><td>Fleet condition, route density, contracted volumes</td></tr>
      <tr><td>E-commerce &amp; online</td><td>2.5&times; &ndash; 5.5&times;</td><td>Owned traffic and repeat customers rather than paid acquisition</td></tr>
      <tr><td>F&amp;B &amp; food manufacturing</td><td>2.5&times; &ndash; 5&times;</td><td>Secure tenancy, brand equity, a chef-independent kitchen</td></tr>
      <tr><td>Distribution &amp; wholesale</td><td>2.5&times; &ndash; 5&times;</td><td>Exclusive agencies, working-capital discipline</td></tr>
      <tr><td>Retail &amp; consumer</td><td>2&times; &ndash; 4&times;</td><td>Lease terms, footfall stability, inventory quality</td></tr>
      <tr><td>Construction &amp; M&amp;E</td><td>2&times; &ndash; 4&times;</td><td>BCA grading, order book, project-margin consistency</td></tr>
    </tbody>
  </table>
</div>"""

FEE_TABLE = """<div class="table-wrap">
  <table>
    <caption>Sell-side success fee, charged on transaction value and payable only on completion. Minimum fee S$100,000.</caption>
    <thead><tr><th scope="col">Transaction value</th><th scope="col">Success fee</th><th scope="col">Fee at the top of the band</th></tr></thead>
    <tbody>
      <tr><td>Up to S$5M</td><td><strong>5%</strong></td><td>S$250,000 on a S$5M sale</td></tr>
      <tr><td>S$5M &ndash; S$10M</td><td><strong>4%</strong></td><td>S$400,000 on a S$10M sale</td></tr>
      <tr><td>S$10M &ndash; S$20M</td><td><strong>3%</strong></td><td>S$600,000 on a S$20M sale</td></tr>
      <tr><td>S$20M &ndash; S$50M</td><td><strong>2%</strong></td><td>S$1,000,000 on a S$50M sale</td></tr>
      <tr><td>Above S$50M</td><td><strong>1%</strong></td><td>&mdash;</td></tr>
    </tbody>
  </table>
</div>"""

STAGES = [
    ("Weeks 1&ndash;2", "Confidential discussion and fit",
     "A no-obligation conversation about your goals, your timeline and whether selling now is actually the right move. Some owners leave this call deciding to wait two years — that is a legitimate outcome."),
    ("Weeks 2&ndash;6", "Valuation and preparation",
     "Adjusted EBITDA analysis, comparable multiples, and a defensible asking range. We also fix the cheap things that raise value: tidy accounts, documented processes, contracts in writing."),
    ("Month 2", "Blind marketing materials",
     "A no-name teaser that describes the business without identifying it, and a full information memorandum released only after an NDA is signed."),
    ("Months 2&ndash;4", "Buyer search and screening",
     "Targeted approaches to strategic acquirers, investors and operators. Every buyer is scored on intent, sector fit and financial capability before you are ever introduced."),
    ("Months 4&ndash;5", "Offers and negotiation",
     "Competing interest managed toward a term sheet, with price, deal structure, earn-out and transition terms negotiated from your side of the table."),
    ("Months 5&ndash;7", "Due diligence",
     "A password-controlled data room you own, access granted per buyer and per document, coordinated Q&amp;A, and the momentum management that stops deals dying of slow answers."),
    ("Months 7&ndash;8", "Completion and handover",
     "Sale and purchase agreement, completion mechanics, stamp duty and ACRA filings, and a transition plan that protects your staff and your name."),
]


def stages_html(light=False):
    items = ''.join(
        '<li class="stage reveal" style="--i:%d"><span class="t-meta">%s</span>'
        '<h3>%s</h3><p>%s</p></li>' % (i, meta, title, body)
        for i, (meta, title, body) in enumerate(STAGES))
    return '<ol class="stages%s">%s</ol>' % (' on-light-stages' if light else '', items)


QUALIFY = """<div class="grid-2">
  <div class="panel reveal">
    <h3>We are probably a fit if</h3>
    <ul>
      <li>Revenue is roughly <strong>S$2M&ndash;S$20M</strong> and the business is profitable</li>
      <li>You are genuinely prepared to sell, not testing the water for a number</li>
      <li>Confidentiality matters more to you than speed</li>
      <li>You want the process run properly rather than listed on a marketplace</li>
    </ul>
  </div>
  <div class="panel reveal" style="--i:1">
    <h3>We are probably not a fit if</h3>
    <ul>
      <li>Transaction value would fall below about <strong>S$1.5M&ndash;S$2M</strong> — our S$100,000 minimum fee makes us poor value there</li>
      <li>The business is loss-making with no clear path back</li>
      <li>You want a valuation letter for a bank or a divorce rather than a sale</li>
      <li>You want us to also act for the buyer's interests — we act for the seller</li>
    </ul>
  </div>
</div>
<p class="mt-2 reveal">If we are not the right firm for you, we will say so in the first conversation and point you somewhere more useful. That costs nothing and saves everyone a month.</p>"""

PROOF_BLOCK = """<div class="grid-3">
  <div class="proof reveal">
    <p>Published client references on our parent firm's site are named and checkable: a corporate M&amp;A lawyer at 28 Falcon Law Corporation, the Lee &amp; Lee founders of a 20-year strudel manufacturer, and the founder of a 30-year bottling company.</p>
    <p class="attrib"><a class="textlink" href="{parent_url}" rel="noopener">Read them at {parent}</a></p>
  </div>
  <div class="proof reveal" style="--i:1">
    <p>The strudel manufacturer&rsquo;s sale ran six months end to end, from first conversation to completion — a succession sale where the brand and the team carried on under new ownership.</p>
    <p class="attrib">Completed transaction. We disguise live mandates and never name a client without written permission.</p>
  </div>
  <div class="proof reveal" style="--i:2">
    <p>You will work with Eric Ong, the founder, from the first call to completion — not a business-development person who hands you off once you sign.</p>
    <p class="attrib"><a class="textlink" href="/about/">About the firm and the founder</a></p>
  </div>
</div>""".format(parent_url=PARENT_URL, parent=PARENT)

DUAL_AGENCY = """<div class="callout reveal">
  <h3>Where we stand, said plainly</h3>
  <p>On a sale mandate we act for the seller. Buyers who transact through us pay a separate <strong>1% finder&rsquo;s fee</strong> on transaction value, success-only, for the buy-side process work — screened deal flow, process management and data-room coordination. Both fees are disclosed to both sides before anyone signs anything. If that arrangement does not suit you, say so early and we will tell you honestly whether we are the right firm.</p>
</div>"""


# ---------------------------------------------------------------- pages

PAGES = []


def add(slug, title, desc, body, crumbs=None, extra_schema=None, faqs=None):
    schema_graph = [ORG_SCHEMA, WEBSITE_SCHEMA] if slug == "" else []
    if crumbs:
        schema_graph.append(breadcrumb_schema(crumbs))
    if faqs:
        schema_graph.append(faq_schema(faqs))
    if extra_schema:
        schema_graph.extend(extra_schema)
    PAGES.append({
        "slug": slug, "title": title, "desc": desc, "body": body,
        "schema": {"@context": "https://schema.org", "@graph": schema_graph},
        "active": "/" + slug + "/" if slug else "/",
    })


# ------------------------------------------------------------------ home

HOME_FAQS = [
    ("What does a business broker in Singapore actually charge?",
     ["Our sell-side fee is success-only and tiered: 5% of transaction value up to S$5M, 4% from S$5M to S$10M, 3% from S$10M to S$20M, 2% from S$20M to S$50M and 1% above that, with a minimum fee of S$100,000. There is no retainer and no upfront cost, so a business that does not sell costs you nothing.",
      "That minimum makes us poor value below roughly S$1.5M&ndash;S$2M of transaction value, and we would rather tell you that now than at the end of a first meeting."]),
    ("How do you stop my staff and customers finding out that I am selling?",
     ["Confidentiality here is a mechanism, not a promise. Buyers first see a no-name profile — sector, revenue band, one or two strengths — with nothing that identifies the company. Each buyer is screened for intent and financial capability, then signs an NDA before your name is disclosed.",
      "After that, disclosure is staged and you approve every introduction personally. Sensitive documents sit in a data room whose password you control, with access granted per buyer and per document, and every view logged."]),
    ("How long does it take to sell a business in Singapore?",
     ["Six to eight months is typical for a structured process: one to two months preparing and valuing, two to four months of confidential buyer search and negotiation, and two to three months of due diligence and legal completion.",
      "Deals that move faster usually do so because the seller was already prepared — clean accounts, current statutory records and contracts in order before going to market."]),
    ("How much is my business worth?",
     ["Most profitable Singapore SMEs transact at a multiple of adjusted EBITDA, commonly between 2&times; and 9&times; depending on sector, size, growth and how dependent the business is on the owner. A business with S$800,000 of adjusted EBITDA in a 3&times;&ndash;5&times; sector sits in an indicative S$2.4M&ndash;S$4M range before any adjustment for debt and surplus cash.",
      "That is a starting point, not a valuation. The number that matters is what a screened buyer will actually pay after diligence."]),
    ("Do you also represent the buyer?",
     ["On a sale mandate we act for the seller. Buyers who acquire through us pay a separate 1% finder&rsquo;s fee, success-only, for the buy-side process work. Both fees are disclosed to both sides before anything is signed — we would rather lose a deal than be evasive about that."]),
]

HOME = """<section class="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <h1 class="fx">Sell the business you built &mdash; <em>to the right buyer</em>, at a defensible price.</h1>
        <p class="lead fx fx-2">Singapore Business Broker is the sell-side practice of {parent}. We run a structured seven-stage sale for SME owners, protect your confidentiality by design rather than by assurance, and charge nothing at all unless the business sells.</p>
        <div class="hero-ctas fx fx-3">
          <a class="btn btn-brass" href="/sale-readiness/">Score your sale readiness</a>
          <a class="btn btn-wa" href="{wa}">{wa_icon} WhatsApp &mdash; confidential</a>
        </div>
        <ul class="hero-trust fx fx-4">
          <li>{check} No upfront fees, ever</li>
          <li>{check} Success fee published: 1&ndash;5%</li>
          <li>{check} NDA signed before your name is disclosed</li>
          <li>{check} Founder-led from first call to completion</li>
        </ul>
      </div>
      <aside class="glance fx fx-3" aria-labelledby="glance-h">
        <h2 id="glance-h">At a glance</h2>
        <dl>
          <dt>Sell-side fee</dt>
          <dd>1&ndash;5% of transaction value<span>Success-only. Minimum S$100,000. No retainer.</span></dd>
          <dt>Who we work with</dt>
          <dd>Singapore SMEs, S$2M&ndash;S$20M revenue<span>Poor value below about S$1.5M&ndash;S$2M transaction value.</span></dd>
          <dt>Typical timeline</dt>
          <dd>Six to eight months<span>Seven defined stages, first call to handover.</span></dd>
          <dt>Who acts for whom</dt>
          <dd>We act for the seller<span>Buyers pay a separate 1%. Both fees disclosed to both sides.</span></dd>
        </dl>
        <p class="glance-foot"><a class="textlink" href="/fees/">The full fee table</a> &middot; <a class="textlink" href="/about/">About the firm</a></p>
      </aside>
    </div>
  </div>
</section>

<section class="stat-band">
  <div class="container">
    <div class="stat-grid">
      <div class="reveal"><div class="stat-num">S$0</div><div class="stat-label">Retainer, listing fee or upfront cost</div></div>
      <div class="reveal" style="--i:1"><div class="stat-num">1&ndash;5%</div><div class="stat-label">Published success fee, paid only on completion</div></div>
      <div class="reveal" style="--i:2"><div class="stat-num">6&ndash;8 mths</div><div class="stat-label">Typical structured sale, first call to handover</div></div>
      <div class="reveal" style="--i:3"><div class="stat-num">7 stages</div><div class="stat-label">A defined process, not a listing on a website</div></div>
    </div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="split split-5-7">
      <div class="reveal">
        <span class="eyebrow">What a broker is for</span>
        <h2>Most owners lose money on the process, not on the price.</h2>
      </div>
      <div class="reveal" style="--i:1">
        <p class="lead">An owner who sells once in a lifetime negotiates against a buyer who has done it eleven times. The gap does not usually show up as a lower headline number. It shows up as a re-trade after diligence, an earn-out that never pays, warranties that stay open for three years, and a transition period nobody agreed to in writing.</p>
        <p>Our job is to remove that asymmetry: to bring several capable buyers to the table at the same time so you are negotiating rather than accepting, and to hold the deal together through the six months where most SME transactions quietly die.</p>
      </div>
    </div>
    <div class="grid-3 mt-3">
      <div class="panel panel-hover panel-num reveal">
        <span class="n">01</span>
        <div class="icon-tile">{i_users}</div>
        <h3>Competition, not a single suitor</h3>
        <p>The offer you get from the one buyer who approached you is almost never the best one available. We approach a targeted set of strategic acquirers, investors and operators, and run them to a decision point together.</p>
      </div>
      <div class="panel panel-hover panel-num reveal" style="--i:1">
        <span class="n">02</span>
        <div class="icon-tile">{i_lock}</div>
        <h3>Confidentiality as a mechanism</h3>
        <p>No-name marketing, buyers scored before disclosure, NDA before your company is identified, staged release, and a data room whose password you hold with per-document access logging.</p>
      </div>
      <div class="panel panel-hover panel-num reveal" style="--i:2">
        <span class="n">03</span>
        <div class="icon-tile">{i_shield}</div>
        <h3>Deals held together</h3>
        <p>Most SME deals fail in due diligence, not at the offer. We prepare the answers before the questions arrive, and keep pace up so the buyer never has a quiet month to reconsider.</p>
      </div>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">The process</span>
      <h2>Seven stages, roughly six to eight months</h2>
      <p class="lead">You keep running the business. We run the sale. Every stage has a defined output, so you always know what has been done and what happens next.</p>
    </div>
    {stages}
    <div class="btn-row mt-3 reveal"><a class="btn btn-brass" href="/process/">See each stage in detail</a></div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Fees</span>
      <h2>The fee table, published — not quoted after we have sized you up</h2>
      <p class="lead">You should be able to work out what we would earn from your sale before you ever speak to us. So here it is.</p>
    </div>
    <div class="reveal">{fee_table}</div>
    <div class="mt-2">{dual}</div>
    <div class="btn-row mt-2 reveal"><a class="btn btn-ghost" href="/fees/">How this compares to retainer-based advisers</a></div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="split split-7-5">
      <div class="reveal">
        <span class="eyebrow">Before you go to market</span>
        <h2>Ten questions that decide what your business is worth</h2>
        <p class="lead">Buyers do not pay for last year&rsquo;s profit. They pay for how confident they are that the profit continues without you. Our sale-readiness scorecard walks the ten factors that move that confidence, scores where you stand today, and tells you what to fix first.</p>
        <p>It takes about three minutes, asks for no personal details, and gives you the answer on the page. Nothing is emailed to you and nothing is stored.</p>
        <div class="btn-row mt-2"><a class="btn btn-brass" href="/sale-readiness/">Open the scorecard</a><a class="btn btn-ghost" href="/business-valuation-singapore/">How valuation actually works</a></div>
      </div>
      <div class="reveal" style="--i:1">
        <ul class="deflist">
          <li><span class="dt">Quality of earnings</span><span class="dd">Can a buyer&rsquo;s accountant tie your profit to the bank statements in an afternoon?</span></li>
          <li><span class="dt">Owner dependence</span><span class="dd">What breaks in the first month after you stop answering the phone?</span></li>
          <li><span class="dt">Customer concentration</span><span class="dd">How much of the revenue leaves if one relationship leaves?</span></li>
          <li><span class="dt">Second-line management</span><span class="dd">Is there someone who could run it, and do they know they are that person?</span></li>
          <li><span class="dt">Statutory hygiene</span><span class="dd">Are ACRA filings, registers and past share transfers actually in order?</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="on-stone">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Who we work with</span>
      <h2>We are selective, and here is the number behind that word</h2>
      <p class="lead">Selectivity means a revenue band and a minimum fee, not an adjective. Both are below.</p>
    </div>
    {qualify}
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Proof you can check</span>
      <h2>Before you reply, you will Google us. Here is what you will find.</h2>
      <p class="lead">We are a boutique. That is a real trade-off: you get the founder on every call, and you do not get the deal volume of a large firm. You should weigh both.</p>
    </div>
    {proof}
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Common questions</span>
      <h2>What owners ask first</h2>
    </div>
    <div class="reveal">{faqs}</div>
    <div class="btn-row mt-2 reveal"><a class="btn btn-ghost" href="/faq/">All questions</a></div>
  </div>
</section>

{cta}""".format(
    parent=PARENT, wa=WA_SELLER, wa_icon=WA_ICON, check=CHECK,
    i_users=I_USERS, i_lock=I_LOCK, i_shield=I_SHIELD,
    stages=stages_html(), fee_table=FEE_TABLE, dual=DUAL_AGENCY,
    qualify=QUALIFY, proof=PROOF_BLOCK, faqs=faq_block(HOME_FAQS),
    cta=cta_band(
        "A confidential conversation, before you decide anything",
        "Thirty minutes, no fee, no obligation, and your name goes nowhere. Most first calls end with a plan and a timeline — not a mandate.",
        "Send a confidential enquiry", "/contact/",
        "Prefer to stay anonymous for now? WhatsApp is fine, and you can ask a question without saying which company you own."))

add("", "Singapore Business Broker | Sell Your SME Confidentially, Success-Only Fees",
    "Sell-side business broker in Singapore for SME owners. Structured 7-stage sale, no-name confidential marketing, buyers screened before disclosure, published success-only fees of 1–5% and no upfront cost. Free sale-readiness scorecard.",
    HOME, faqs=HOME_FAQS)


# ------------------------------------------------------------------ sell

SELL_FAQS = [
    ("What is the first step to selling my business in Singapore?",
     ["A confidential conversation about your goals and timeline, followed by an adjusted-EBITDA valuation. Nothing is marketed and no buyer hears anything until you have seen a valuation range and agreed the plan."]),
    ("Should I tell my staff I am selling?",
     ["Not at the start. In most SME sales the team is told after a term sheet is signed and the buyer is committed, and often only the one or two people whose help is needed for due diligence are told before completion.",
      "We plan that announcement with you as part of the transition plan, because how the team hears it affects whether they stay — which affects whether the buyer&rsquo;s price survives."]),
    ("Can I sell only part of my business?",
     ["Yes. Partial sales, majority stakes with a rolled-over minority, and staged exits over two to three years are all normal structures, and they often suit an owner who wants liquidity now and a second bite later. The process is the same; the negotiation is about control, board rights and what happens at the second exit."]),
    ("What if I change my mind halfway through?",
     ["You can stop. It is your business and your decision, and no fee is owed on a sale that does not complete. We would ask for an honest conversation about why, because the reason usually matters — cold feet at term sheet is a very different problem from a buyer behaving badly."]),
]

SELL = page_hero(
    [("/sell-a-business-singapore/", "Sell a business")],
    "How to sell a business in Singapore without your staff finding out",
    "The full process, the confidentiality mechanism, the mistakes that cost owners money, and what it costs to have it run properly.",
    '<div class="btn-row"><a class="btn btn-brass" href="/sale-readiness/">Score your sale readiness</a>'
    '<a class="btn btn-wa" href="%s">%s WhatsApp a question</a></div>' % (WA_SELLER, WA_ICON)
) + answer_section([
    "To sell a business in Singapore confidentially you prepare the financials and statutory records first, agree a defensible valuation range based on adjusted EBITDA, market the business under a no-name profile, screen every buyer for intent and financial capability before disclosing anything, require a signed NDA before your company is named, then run due diligence in a data room you control and complete through a sale and purchase agreement. Done properly it takes six to eight months.",
    "The single decision that most affects both price and confidentiality is whether you go to several screened buyers at once or negotiate with the one who approached you. A competitive process is what turns an offer into a market price.",
]) + """
<section>
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">The fear that stops most owners</span>
      <h2>&ldquo;What happens if word gets out before I&rsquo;m ready?&rdquo;</h2>
      <p class="lead">Staff start looking. Your best customer starts a second supplier relationship. A competitor calls your clients to say you are in trouble. The damage is real, which is why the answer cannot be a reassurance — it has to be a mechanism you can inspect.</p>
    </div>
    <ul class="deflist reveal">
      <li><span class="dt">1. No-name profile</span><span class="dd">Buyers first see sector, revenue band, adjusted EBITDA band and one or two strengths. No company name, no address, no client names, nothing that lets someone identify you from the description.</span></li>
      <li><span class="dt">2. Screening before disclosure</span><span class="dd">Each interested party is scored on acquisition intent, sector fit and evidence of ability to pay before they are told anything more. People browsing do not get past this step.</span></li>
      <li><span class="dt">3. NDA before your name</span><span class="dd">A signed non-disclosure agreement is a precondition of learning which company this is. Not a verbal understanding — a signed document.</span></li>
      <li><span class="dt">4. You approve every introduction</span><span class="dd">No buyer speaks to you, visits your premises or meets your team without your specific approval for that buyer.</span></li>
      <li><span class="dt">5. A data room you control</span><span class="dd">Documents sit behind a password you hold. Access is granted per buyer and per document, sensitive items are released late, and every view is logged.</span></li>
      <li><span class="dt">6. Staged disclosure</span><span class="dd">Customer names, key contracts and staff details are the last things released, usually after a term sheet is signed and the buyer has committed.</span></li>
    </ul>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">What it costs to get this wrong</span>
      <h2>Five mistakes that show up in the final price</h2>
    </div>
    <div class="grid-2">
      <div class="panel reveal"><h3>Negotiating with one buyer</h3><p>An unsolicited approach is flattering and it is also the weakest position you will ever negotiate from. Without an alternative, every concession is one-way.</p></div>
      <div class="panel reveal" style="--i:1"><h3>Going to market unprepared</h3><p>Messy accounts and missing paperwork do not just slow diligence — they give the buyer a documented reason to re-trade the price after you have emotionally committed.</p></div>
      <div class="panel reveal" style="--i:2"><h3>Confusing profit with owner income</h3><p>Until personal expenses, above- or below-market director salary and one-off items are separated out, nobody — including you — knows what the business actually earns.</p></div>
      <div class="panel reveal" style="--i:3"><h3>Being indispensable</h3><p>If the business needs you, the buyer is not buying a business, they are buying a job that depends on you staying. Price and structure both reflect that.</p></div>
      <div class="panel reveal" style="--i:4"><h3>Letting the deal go quiet</h3><p>Momentum is a real asset. A buyer with an unanswered question for three weeks starts wondering what else is slow, and enthusiasm does not survive a quiet month.</p></div>
      <div class="panel reveal" style="--i:5"><h3>Signing a term sheet you have not read properly</h3><p>Exclusivity length, earn-out mechanics, warranty periods and what counts as a material adverse change are all negotiable — before you sign, and almost never after.</p></div>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Timeline</span>
      <h2>What actually happens, month by month</h2>
    </div>
    """ + stages_html() + """
  </div>
</section>

<section>
  <div class="container">
    <div class="split split-7-5">
      <div class="reveal">
        <span class="eyebrow">Worked example</span>
        <h2>Turning stated profit into a number a buyer will underwrite</h2>
        <p>A distribution business reports S$620,000 of net profit before tax. That is not the number a buyer values. Normalisation separates the earnings of the business from the choices of its owner:</p>
        <div class="table-wrap mt-2">
          <table>
            <caption>Illustrative EBITDA normalisation. Figures are an example, not a client.</caption>
            <thead><tr><th scope="col">Item</th><th scope="col">Adjustment</th><th scope="col">Running total</th></tr></thead>
            <tbody>
              <tr><td>Net profit before tax</td><td>&mdash;</td><td>S$620,000</td></tr>
              <tr><td>Add back: interest expense</td><td>+ S$40,000</td><td>S$660,000</td></tr>
              <tr><td>Add back: depreciation and amortisation</td><td>+ S$95,000</td><td>S$755,000</td></tr>
              <tr><td>Add back: owner&rsquo;s salary above market rate</td><td>+ S$180,000</td><td>S$935,000</td></tr>
              <tr><td>Add back: personal motor and travel costs run through the company</td><td>+ S$48,000</td><td>S$983,000</td></tr>
              <tr><td>Add back: one-off legal costs of a settled dispute</td><td>+ S$35,000</td><td>S$1,018,000</td></tr>
              <tr><td>Deduct: market-rate salary for a replacement general manager</td><td>&minus; S$150,000</td><td>S$868,000</td></tr>
              <tr><td>Deduct: one-off gain on disposal of a vehicle</td><td>&minus; S$18,000</td><td>S$850,000</td></tr>
              <tr class="highlight"><td><strong>Adjusted EBITDA</strong></td><td>&mdash;</td><td><strong>S$850,000</strong></td></tr>
            </tbody>
          </table>
        </div>
        <p class="mt-2">At a distribution multiple of 2.5&times;&ndash;5&times;, that is an indicative enterprise value of S$2.13M&ndash;S$4.25M. Equity value then adjusts for debt, surplus cash and a normal level of working capital left in the business at completion.</p>
        <p>Note the two deductions. Adding back an owner&rsquo;s salary without deducting the cost of the manager who replaces him is the most common error in SME valuations, and a buyer&rsquo;s accountant finds it immediately.</p>
      </div>
      <div class="reveal" style="--i:1">
        <div class="callout">
          <h3>Where the multiple lands</h3>
          <p>Within a sector range, the difference between the bottom and the top is mostly the same four things: recurring or contracted revenue, low customer concentration, a management team that is not you, and financial records a buyer can verify quickly.</p>
        </div>
        <div class="callout mt-2">
          <h3>Our focus</h3>
          <p>We work with Singapore businesses of roughly S$2M&ndash;S$20M revenue. Our minimum fee is S$100,000, which makes us the wrong choice below about S$1.5M&ndash;S$2M of transaction value.</p>
        </div>
        <div class="btn-row mt-2"><a class="btn btn-brass" href="/business-valuation-singapore/">Full valuation guide</a></div>
      </div>
    </div>
  </div>
</section>

<section class="on-stone">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>Selling, in practice</h2></div>
    <div class="reveal">""" + faq_block(SELL_FAQS) + """</div>
  </div>
</section>

""" + cta_band(
    "Start with a question, not a mandate",
    "You do not have to tell us which company you own to ask what a sale would look like. Most owners we speak to are twelve to twenty-four months away, and that is exactly the right time to call.",
    "Send a confidential enquiry", "/contact/",
    "No fee and no obligation. If a sale is not right for you now, we will say so.")

add("sell-a-business-singapore",
    "Sell a Business in Singapore | Confidential Sale Process & Costs",
    "How to sell a business in Singapore confidentially: the six-step confidentiality mechanism, the 7-stage process, a worked EBITDA normalisation example, and published success-only fees of 1–5%.",
    SELL, crumbs=[("/sell-a-business-singapore/", "Sell a business")], faqs=SELL_FAQS)


# ------------------------------------------------------------------ valuation

VAL_FAQS = [
    ("How do I value my business in Singapore?",
     ["For a profitable SME, calculate adjusted EBITDA, apply the multiple range for your sector, then adjust for debt, surplus cash and working capital to get equity value. The multiple is set by how transferable and predictable the earnings are, not by how hard you worked for them."]),
    ("Is revenue or profit used to value a business?",
     ["Profit, in almost every case. Revenue multiples are used mainly for high-growth software and for asset-light businesses with recurring subscriptions. For a typical Singapore SME, adjusted EBITDA is the base and revenue is context."]),
    ("Does goodwill get valued separately?",
     ["Not as a separate line in a share sale. Goodwill is already inside the multiple — it is the reason a business earning S$1M is worth four times earnings rather than one. Balance-sheet goodwill from a past acquisition is a different thing and is usually stripped out of the analysis."]),
    ("Will a buyer pay for my growth projections?",
     ["Partly, and only if they are evidenced. A signed contract starting next quarter moves the price. A spreadsheet showing 30% growth because the market is growing does not. Where the gap is genuine, it usually gets bridged with an earn-out rather than cash at completion."]),
    ("Do I need a formal valuation report?",
     ["To sell, no — you need a defensible range and a buyer. Formal valuation reports are for banks, disputes, tax positions and share transfers between related parties. We do not sell valuation reports, which is also why our estimate does not have an incentive to flatter you."]),
]

VAL = page_hero(
    [("/business-valuation-singapore/", "Business valuation")],
    "Business valuation in Singapore: what your SME is actually worth",
    "The method buyers use, the multiple ranges by sector, a worked normalisation example, and the four factors that decide where in the range you land.",
    '<div class="btn-row"><a class="btn btn-brass" href="/sale-readiness/">Score your sale readiness</a>'
    '<a class="btn btn-ghost" href="/sell-a-business-singapore/">The sale process</a></div>'
) + answer_section([
    "Most profitable Singapore SMEs are valued at a multiple of adjusted EBITDA, typically between 2&times; and 9&times; depending on sector, growth, customer concentration and how dependent the business is on its owner. Adjusted EBITDA is your reported profit with interest, tax, depreciation and amortisation added back, personal and one-off items removed, and the owner&rsquo;s pay restated to what a replacement manager would actually cost.",
    "Enterprise value is adjusted EBITDA multiplied by the sector multiple. Equity value — the money you receive — is enterprise value plus surplus cash, less debt, and adjusted for whether working capital at completion is at a normal level.",
]) + """
<section>
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Step one</span>
      <h2>Adjusted EBITDA, calculated the way a buyer&rsquo;s accountant will</h2>
      <p class="lead">Reported profit reflects tax planning and owner preference. Adjusted EBITDA reflects what the business earns for whoever owns it next. The gap between the two is often 30&ndash;60% in an SME — in both directions.</p>
    </div>
    <div class="split">
      <div class="reveal">
        <h3>Added back</h3>
        <ul>
          <li>Interest, tax, depreciation and amortisation</li>
          <li>Owner&rsquo;s remuneration above a market rate for the role</li>
          <li>Family members on payroll beyond the value of their work</li>
          <li>Personal expenses run through the company — vehicle, travel, insurance</li>
          <li>Genuinely non-recurring costs: a settled dispute, a one-off relocation</li>
          <li>Rent paid above market to a property you own personally</li>
        </ul>
      </div>
      <div class="reveal" style="--i:1">
        <h3>Deducted &mdash; the half most sellers skip</h3>
        <ul>
          <li>Market-rate salary for whoever replaces the owner&rsquo;s actual work</li>
          <li>Below-market rent that will reset to market after completion</li>
          <li>One-off gains: asset disposals, insurance recoveries, grants</li>
          <li>Deferred maintenance and capital spend the buyer must fund immediately</li>
          <li>Under-provided items: unused leave, warranty claims, bad debts</li>
        </ul>
      </div>
    </div>
    <div class="callout mt-3 reveal">
      <h3>The error that gets caught every time</h3>
      <p>Adding back a S$300,000 owner&rsquo;s salary and stopping there implies the business runs itself. If the owner does a general manager&rsquo;s job, the buyer deducts a general manager&rsquo;s salary — so the real add-back is the difference, not the whole amount. Presenting the gross add-back does not win an argument; it costs you credibility on every other number in the pack.</p>
    </div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Step two</span>
      <h2>The multiple, by sector</h2>
      <p class="lead">These are the ranges Singapore SME transactions cluster in. Where you sit inside your range is decided by the four factors below, and moving up one turn of the multiple is usually worth more than a year of trading growth.</p>
    </div>
    <div class="reveal">""" + MULTIPLES_TABLE + """</div>
    <div class="grid-4 mt-3">
      <div class="panel reveal"><div class="icon-tile">""" + I_CHART + """</div><h3>Earnings quality</h3><p>Audited or reviewed accounts that reconcile to bank statements, with consistent treatment year to year.</p></div>
      <div class="panel reveal" style="--i:1"><div class="icon-tile">""" + I_HAND + """</div><h3>Owner dependence</h3><p>What proportion of revenue, pricing and technical knowledge sits only with you.</p></div>
      <div class="panel reveal" style="--i:2"><div class="icon-tile">""" + I_USERS + """</div><h3>Customer concentration</h3><p>One client above 25% of revenue is a discussion. Above 40% it is a structural discount or an earn-out.</p></div>
      <div class="panel reveal" style="--i:3"><div class="icon-tile">""" + I_DOC + """</div><h3>Contract security</h3><p>Contracted and recurring revenue with assignable terms, versus repeat business by goodwill alone.</p></div>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="container">
    <div class="split split-7-5">
      <div class="reveal">
        <span class="eyebrow">Step three</span>
        <h2>From enterprise value to the money that reaches you</h2>
        <p class="lead">The multiple gives enterprise value. What lands in your account is a different number, and the difference is where a lot of sellers get an unpleasant surprise late in the process.</p>
        <ul>
          <li><strong>Less debt:</strong> bank loans, hire purchase, director loans owed by the company, unpaid tax</li>
          <li><strong>Plus surplus cash:</strong> cash above what the business needs to operate normally</li>
          <li><strong>Working-capital adjustment:</strong> completion accounts test whether receivables, inventory and payables are at a normal level; below normal and the price adjusts down</li>
          <li><strong>Deal structure:</strong> how much is cash at completion, how much is deferred, how much is contingent on an earn-out you may or may not hit</li>
          <li><strong>Retentions and escrow:</strong> a portion held back against warranty claims, commonly for twelve to twenty-four months</li>
        </ul>
      </div>
      <div class="reveal" style="--i:1">
        <div class="panel">
          <h3>Worth asking early</h3>
          <p>&ldquo;Of the headline price, how much is cash at completion?&rdquo; Two offers at S$5M are not the same offer if one is S$5M cash and the other is S$3M cash plus S$2M of earn-out over three years contingent on targets the buyer will control after completion.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>Valuation questions owners actually ask</h2></div>
    <div class="reveal">""" + faq_block(VAL_FAQS) + """</div>
  </div>
</section>

""" + cta_band(
    "Get a considered range instead of a rule of thumb",
    "Send us the shape of the business — sector, revenue, roughly what it earns — and we will tell you the range we would defend and what would move it. No report to buy, no obligation.",
    "Ask for an indicative range", "/contact/",
    "We work with Singapore businesses of about S$2M–S$20M revenue. Below that we are honestly not the best value.")

add("business-valuation-singapore",
    "Business Valuation Singapore | What Your SME Is Worth (2026 Multiples)",
    "How Singapore SMEs are valued: adjusted EBITDA explained with a worked normalisation example, sector multiple ranges from 2× to 9×, and how enterprise value becomes the cash you actually receive.",
    VAL, crumbs=[("/business-valuation-singapore/", "Business valuation")], faqs=VAL_FAQS)


# ------------------------------------------------------------------ exit planning

EXIT_FAQS = [
    ("When should I start planning my exit?",
     ["Two to three years before you want to leave. That is enough time to reduce owner dependence, clean up the accounts, get statutory records in order and build a second line of management — the four things that move the multiple. Owners who start twelve months out can still sell well; owners who start the week they decide to retire usually sell for less."]),
    ("What are my options besides selling to a third party?",
     ["A management buy-out, a family succession, a partial sale with a rolled-over stake, a merger with a competitor, or a staged exit where you sell a majority now and the balance in three years. Winding down is also a legitimate option and occasionally the right one — a business whose value is entirely the owner may be worth more as an orderly closure than as a discounted sale."]),
    ("How do I hand over to my children without breaking the business?",
     ["Treat it as a transaction with a timeline, not an inheritance. Define the roles, the ownership steps, the valuation and how non-participating siblings are treated, and put it in writing while everyone is on speaking terms. The families where this works are the ones that decided the awkward questions early."]),
    ("Can I stay involved after selling?",
     ["Usually, and often the buyer wants it. Six to twelve months of transition is standard, sometimes with a consultancy arrangement or a non-executive role afterward. What matters is that the terms — time commitment, decision rights, pay — are in the agreement rather than in a friendly understanding."]),
]

EXIT = page_hero(
    [("/exit-planning-singapore/", "Exit planning")],
    "Exit and succession planning for Singapore business owners",
    "Most of the value in a sale is created in the two years before it, not in the negotiation. Here is what to do with that time.",
    '<div class="btn-row"><a class="btn btn-brass" href="/sale-readiness/">Score your sale readiness</a></div>'
) + answer_section([
    "Exit planning is the two-to-three year process of making a business sellable without its owner: reducing owner dependence, normalising and cleaning the financial records, bringing statutory filings and contracts up to date, building a second line of management, and deciding whether the exit is a trade sale, a management buy-out, a family succession or a staged sale.",
    "It matters because the multiple a buyer pays is a measure of confidence that the earnings continue after you leave. Two identical businesses earning S$1M can transact at 3&times; and 5&times; — a S$2M difference — on nothing more than how transferable those earnings look.",
]) + """
<section>
  <div class="container">
    <div class="split split-5-7">
      <div class="reveal">
        <span class="eyebrow">The problem with waiting</span>
        <h2>The best time to prepare is when you have no intention of selling.</h2>
      </div>
      <div class="reveal" style="--i:1">
        <p class="lead">Singapore has a succession wave running through it. A generation of founders who built businesses in the 1980s and 1990s is reaching retirement at the same time, and a good number of them have children with careers of their own.</p>
        <p>The owners who do well in that market are the ones who prepared before they needed to. The ones who struggle are those who decided to sell after a health scare, a partner dispute or a bad year — because every one of those events is visible to a buyer, and each one weakens the position of the person on your side of the table.</p>
        <p>Preparation is not a document. It is a set of changes to how the business runs, and most of them are good for the business whether or not you ever sell.</p>
      </div>
    </div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">A working plan</span>
      <h2>Three years out, one year out, six months out</h2>
    </div>
    <div class="grid-3">
      <div class="panel panel-num reveal">
        <span class="n">36&ndash;24 MONTHS</span>
        <h3>Make it run without you</h3>
        <ul>
          <li>Hand your customer relationships to named people and let them hold</li>
          <li>Promote or hire a second line of management and give them real authority</li>
          <li>Document what only you know: pricing logic, supplier terms, technical method</li>
          <li>Reduce single-customer concentration deliberately, even at some margin cost</li>
          <li>Move informal arrangements onto written contracts</li>
        </ul>
      </div>
      <div class="panel panel-num reveal" style="--i:1">
        <span class="n">24&ndash;12 MONTHS</span>
        <h3>Make the numbers verifiable</h3>
        <ul>
          <li>Take personal expenses out of the company&rsquo;s accounts</li>
          <li>Set your own salary at something close to a market rate for the role</li>
          <li>Get three years of consistent, comparable statements</li>
          <li>Bring ACRA filings, registers of members and controllers, and past share transfers up to date</li>
          <li>Resolve disputes, unstamped transfers and licence issues while there is no deadline</li>
        </ul>
      </div>
      <div class="panel panel-num reveal" style="--i:2">
        <span class="n">12&ndash;6 MONTHS</span>
        <h3>Make the case</h3>
        <ul>
          <li>Agree a valuation range and the evidence behind it</li>
          <li>Assemble the due-diligence pack before buyers ask for it</li>
          <li>Decide what you want after the sale — clean break, transition, or a rolled stake</li>
          <li>Agree with your family and any co-shareholders what &ldquo;yes&rdquo; looks like</li>
          <li>Choose the route: trade sale, management buy-out, succession, staged exit</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="on-stone">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Routes out</span>
      <h2>Five ways this ends, and who each one suits</h2>
    </div>
    <ul class="deflist reveal">
      <li><span class="dt">Trade sale</span><span class="dd">Sale to a competitor, a supplier, a customer or a consolidator. Usually the highest price, because a strategic buyer can fund synergies you cannot. Requires the most careful confidentiality handling, since the best buyer is often someone you compete with.</span></li>
      <li><span class="dt">Financial buyer</span><span class="dd">Private equity, family offices, search funds. Often a partial sale where you retain a stake and take a second payout later. Suits owners with growth ahead of them who want to de-risk now.</span></li>
      <li><span class="dt">Management buy-out</span><span class="dd">Your team buys the business, usually with bank or vendor financing. Best for continuity and staff certainty; typically a lower headline price and more deferred consideration.</span></li>
      <li><span class="dt">Family succession</span><span class="dd">Transfer to the next generation over a defined period. The commercial and the emotional need separating early, and a written plan protects the relationships as much as the business.</span></li>
      <li><span class="dt">Staged exit</span><span class="dd">Sell a majority now, keep a minority, exit fully in three to five years. Gives liquidity and keeps upside — provided the shareholders&rsquo; agreement protects a minority holder properly.</span></li>
    </ul>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>Planning the exit</h2></div>
    <div class="reveal">""" + faq_block(EXIT_FAQS) + """</div>
  </div>
</section>

""" + cta_band(
    "Two years out is the right time to call",
    "The most useful conversation we have is with an owner who is not selling yet. There is nothing to sell you at that stage — just a view on what your business would fetch today and what would change that.",
    "Start a confidential conversation", "/contact/",
    "No fee, no obligation, and nothing leaves the conversation.")

add("exit-planning-singapore",
    "Exit & Succession Planning Singapore | Prepare Your Business to Sell",
    "A three-year exit plan for Singapore SME owners: reduce owner dependence, clean up the financials and statutory records, and choose between a trade sale, MBO, family succession or staged exit.",
    EXIT, crumbs=[("/exit-planning-singapore/", "Exit planning")], faqs=EXIT_FAQS)


# ------------------------------------------------------------------ sale readiness tool

Q_OPTS = [
    ("accounts", "Are your last three years of financial statements clean, consistent and comparable?",
     "Consistent treatment year to year, reconciling to the bank.",
     [("Audited or reviewed", 1.0), ("Compiled, consistent", 0.7),
      ("Compiled, some restatements", 0.35), ("Messy or incomplete", 0.0)]),
    ("ebitda", "Has anyone worked out your adjusted EBITDA — profit separated from owner income?",
     "Personal expenses, owner pay and one-offs identified and quantified.",
     [("Yes, documented", 1.0), ("Roughly, in my head", 0.5),
      ("Not really", 0.2), ("No", 0.0)]),
    ("owner", "If you stopped working tomorrow, what happens in the first three months?",
     "Buyers price this more heavily than almost anything else.",
     [("Runs normally", 1.0), ("Minor disruption", 0.7),
      ("Significant problems", 0.3), ("It stops", 0.0)]),
    ("customers", "What share of revenue comes from your single largest customer?",
     "",
     [("Under 15%", 1.0), ("15&ndash;25%", 0.75), ("25&ndash;40%", 0.4), ("Over 40%", 0.1)]),
    ("contracts", "Are customer and supplier contracts, the tenancy and licences all documented and current?",
     "Including anything with a change-of-control clause.",
     [("All in order", 1.0), ("Mostly", 0.65), ("Patchy", 0.3), ("Largely verbal", 0.0)]),
    ("statutory", "Are ACRA filings, statutory registers and past share transfers up to date and properly stamped?",
     "Annual returns, register of members, register of controllers, board resolutions.",
     [("Yes, confirmed", 1.0), ("I believe so", 0.6), ("Some gaps I know of", 0.25), ("No idea", 0.1)]),
    ("team", "Is there a manager or team who could run day-to-day operations without you?",
     "",
     [("Yes, already doing it", 1.0), ("Yes, with support", 0.7),
      ("One person, partly", 0.35), ("No", 0.0)]),
    ("growth", "How have revenue and profit moved over the last three years?",
     "",
     [("Growing steadily", 1.0), ("Stable", 0.7), ("Uneven", 0.4), ("Declining", 0.15)]),
    ("reason", "How clear are you on why you are selling and what you want afterwards?",
     "Buyers test this, and hesitation reads as a seller who may withdraw.",
     [("Completely clear", 1.0), ("Mostly clear", 0.65),
      ("Still thinking", 0.3), ("Just exploring", 0.1)]),
    ("timeline", "What timeline do you have in mind?",
     "",
     [("12&ndash;24 months", 1.0), ("6&ndash;12 months", 0.85),
      ("Under 6 months", 0.45), ("No timeline yet", 0.5)]),
]


def question_html(idx, name, text, note, opts):
    o = ''.join(
        '<label class="opt"><input type="radio" name="%s" value="%s" required><span>%s</span></label>'
        % (name, v, label) for label, v in opts)
    note_html = '<span class="q-note">%s</span>' % note if note else ''
    return ("""<fieldset class="q-block">
  <legend><span class="kicker-num">%02d</span> &nbsp;%s%s</legend>
  <div class="opts">%s</div>
</fieldset>""" % (idx, text, note_html, o))


READINESS_FORM = """<form id="readiness" class="tool reveal" novalidate>
%s
  <p id="score-error" class="tool-note" role="alert" style="color:#9A2A2A;font-weight:600" hidden></p>
  <p class="nojs-note callout" style="display:none">The scorecard needs JavaScript to calculate your result. If you would rather not enable it, send us your answers by <a class="textlink" href="mailto:%s?subject=%s">email</a> or <a class="textlink" href="%s">WhatsApp</a> and we will score it for you.</p>
  <div class="tool-actions">
    <button type="submit" class="btn btn-brass">Show my score</button>
    <button type="reset" class="btn btn-ghost">Clear</button>
  </div>
  <p class="tool-note">Everything is calculated in your browser. Nothing is sent anywhere, nothing is stored, and we do not ask for your email to see the result.</p>

  <div class="score-out" id="score-out" aria-live="polite">
    <div class="score-head">
      <div class="score-num" id="score-num">0<small>&#8202;/&#8202;100</small></div>
      <span class="score-band" id="score-band">&mdash;</span>
    </div>
    <div class="meter"><i id="score-meter"></i></div>
    <p id="score-summary"></p>
    <h3 id="score-gaps-h" class="mt-2" style="font-size:1.1rem">What to work on first</h3>
    <ul class="gaps mt-1" id="score-gaps"></ul>
    <div class="btn-row mt-2">
      <a class="btn btn-wa" id="score-wa" href="%s">%s Discuss this confidentially</a>
      <a class="btn btn-ghost" id="score-mail" href="mailto:%s">Email the result to us</a>
    </div>
    <p class="tool-note">Sending your score starts a conversation, not a mandate. You do not have to name the company.</p>
  </div>
</form>""" % (
    '\n'.join(question_html(i + 1, n, t, note, o) for i, (n, t, note, o) in enumerate(Q_OPTS)),
    EMAIL, quote("Sale-readiness scorecard answers"), WA_SELLER,
    WA_SELLER, WA_ICON, EMAIL)

READY_FAQS = [
    ("What does the scorecard actually measure?",
     ["The ten factors a buyer&rsquo;s adviser examines before pricing an SME: quality of earnings, owner dependence, customer concentration, contract and statutory hygiene, management depth, trading trend, seller clarity and timeline. It weights them roughly the way buyers do — earnings quality and owner dependence carry the most."]),
    ("Is my information stored or sent anywhere?",
     ["No. The scorecard runs entirely in your browser. There is no form submission, no cookie set by us, no analytics on your answers, and no email required to see the result. If you choose to send us your score, that is a WhatsApp message or an email you write and send yourself."]),
    ("Does a high score mean I should sell now?",
     ["It means you could go to market without leaving obvious money on the table. Whether you should is a separate question about your own plans, the state of your sector and what you would do afterwards — which is what a first conversation is for."]),
]

READINESS = page_hero(
    [("/sale-readiness/", "Sale-readiness scorecard")],
    "Sale-readiness scorecard",
    "Ten questions, about three minutes, and a score out of 100 with the specific gaps that would cost you money in a sale. No email required, nothing stored.",
) + """
<section class="on-stone" style="padding-top:2.5rem">
  <div class="container">
    <div class="split split-7-5">
      <div>
        <div class="section-head" style="margin-bottom:1.5rem">
          <span class="eyebrow">The ten questions</span>
          <h2>Answer honestly — nobody sees this but you</h2>
        </div>
        """ + READINESS_FORM + """
      </div>
      <div>
        <div class="callout reveal">
          <h3>Why these ten</h3>
          <p>They are the factors that decide where in a sector&rsquo;s multiple range a business lands. Moving from the bottom to the top of a 3&times;&ndash;5&times; range on S$1M of earnings is a S$2M difference — considerably more than most owners can add through a year of trading.</p>
        </div>
        <div class="callout mt-2 reveal">
          <h3>What this is not</h3>
          <p>It is not a valuation and it is not advice. It is a structured version of the assessment we would make in a first conversation, so you can do it yourself before deciding whether to have that conversation at all.</p>
        </div>
        <div class="callout mt-2 reveal">
          <h3>Our focus</h3>
          <p>Singapore businesses of roughly S$2M&ndash;S$20M revenue. Minimum fee S$100,000, which makes us poor value below about S$1.5M&ndash;S$2M of transaction value. Worth knowing before you invest three minutes.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">About the tool</span><h2>Questions about the scorecard</h2></div>
    <div class="reveal">""" + faq_block(READY_FAQS) + """</div>
    <div class="btn-row mt-3 reveal">
      <a class="btn btn-ghost" href="/exit-planning-singapore/">The three-year preparation plan</a>
      <a class="btn btn-ghost" href="/business-valuation-singapore/">How valuation works</a>
    </div>
  </div>
</section>

""" + cta_band(
    "Score lower than you expected?",
    "That is the useful outcome. Every gap the scorecard flags is fixable, and fixing it before buyers see the business costs a fraction of what it costs during due diligence.",
    "Talk it through, confidentially", "/contact/",
    "No fee, no obligation, and you do not have to name the company to have the conversation.")

add("sale-readiness",
    "Sale-Readiness Scorecard | Is Your Singapore Business Ready to Sell?",
    "Free 10-question sale-readiness scorecard for Singapore SME owners. Score your business out of 100 on the factors buyers price, and get the specific gaps to fix first. No email required, nothing stored.",
    READINESS, crumbs=[("/sale-readiness/", "Sale-readiness scorecard")], faqs=READY_FAQS)


# ------------------------------------------------------------------ process

PROC_FAQS = [
    ("What do you need from me to get started?",
     ["Three years of financial statements, a short conversation about how the business runs, and your honest view on timing. That is enough to produce a valuation range. Nothing goes to any buyer until you have seen that range and approved the marketing materials."]),
    ("What is an information memorandum?",
     ["The document a screened buyer receives after signing an NDA. It covers the business model, financial history with the normalisation explained, the customer and supplier base in general terms, the team, the assets, the growth case and the reason for sale. It is the document that decides whether a buyer makes an offer, so it is written to be verifiable rather than promotional."]),
    ("Who pays for the lawyers?",
     ["Each side pays its own legal costs. You will need a corporate lawyer for the sale and purchase agreement; we coordinate with them but we do not replace them, and we do not give legal advice. Budget for it in your net-proceeds calculation from the start rather than discovering it at completion."]),
    ("What happens if due diligence turns something up?",
     ["It usually does — that is normal, and it is why preparation matters. The question is whether the issue was disclosed upfront or discovered by the buyer. Disclosed issues get priced or warranted. Discovered issues get used as leverage to re-trade the whole deal, which is a much more expensive conversation."]),
]

PROCESS = page_hero(
    [("/process/", "Process")],
    "The seven stages of a confidential business sale",
    "What happens, in what order, who does what, and roughly how long each stage takes.",
) + answer_section([
    "A structured business sale in Singapore runs through seven stages over roughly six to eight months: a confidential fit discussion, valuation and preparation, blind marketing materials, screened buyer search, offers and negotiation to a term sheet, due diligence in a controlled data room, and legal completion with handover.",
    "The order matters. Every stage exists to make sure a buyer&rsquo;s first substantive question has an answer ready, because unanswered questions are what turn a six-month deal into a twelve-month deal, and twelve-month deals frequently do not complete.",
]) + """
<section class="on-paper">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Stage by stage</span>
      <h2>What happens, and when</h2>
    </div>
    """ + stages_html(light=True) + """
  </div>
</section>

<section class="on-dark">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">Division of labour</span>
        <h2>What we do, and what stays with you</h2>
        <ul class="deflist mt-2">
          <li><span class="dt">We do</span><span class="dd">Valuation, marketing materials, buyer identification and screening, NDA administration, data-room setup and access control, negotiation strategy, term-sheet drafting support, due-diligence coordination, and keeping the timetable moving.</span></li>
          <li><span class="dt">You do</span><span class="dd">Run the business — which is more important than it sounds. A dip in trading during the sale process is the most common cause of a price reduction between term sheet and completion.</span></li>
          <li><span class="dt">Your lawyer does</span><span class="dd">The sale and purchase agreement, warranties and disclosure letter, and completion mechanics. We work alongside them; we do not replace them.</span></li>
          <li><span class="dt">Your accountant does</span><span class="dd">Statements, tax position and completion accounts. Where financial due diligence is heavy, an independent accountant may prepare a vendor pack.</span></li>
        </ul>
      </div>
      <div class="reveal" style="--i:1">
        <span class="eyebrow">Reality check</span>
        <h2>Where deals actually die</h2>
        <div class="panel mt-2"><h3>Diligence surprises</h3><p>Something material the seller knew about and did not disclose. Almost always survivable if raised early; frequently fatal when found by the buyer.</p></div>
        <div class="panel mt-2"><h3>Trading dips mid-process</h3><p>The owner stops selling because they are busy selling the company. Buyers notice, and the price follows the numbers.</p></div>
        <div class="panel mt-2"><h3>Loss of momentum</h3><p>Slow answers, holidays, a lawyer who takes three weeks with a draft. Enthusiasm has a half-life.</p></div>
        <div class="panel mt-2"><h3>Seller&rsquo;s cold feet</h3><p>Common and legitimate — this is a life decision, not a transaction. Better handled by talking about it early than by discovering it at signing.</p></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>About the process</h2></div>
    <div class="reveal">""" + faq_block(PROC_FAQS) + """</div>
  </div>
</section>

""" + cta_band(
    "Stage one costs nothing",
    "The first conversation is a fit discussion: your goals, your timeline, and an honest view on whether selling now serves you. No mandate is signed at that stage, and plenty of owners leave it deciding to wait.",
    "Book a confidential conversation", "/contact/",
    "Thirty minutes. No fee, no obligation, nothing disclosed to anyone.")

add("process", "The Sale Process | 7 Stages of Selling a Business in Singapore",
    "The seven-stage process for selling a Singapore SME confidentially, from first conversation to completion in six to eight months — what happens at each stage and where deals actually fail.",
    PROCESS, crumbs=[("/process/", "Process")], faqs=PROC_FAQS)


# ------------------------------------------------------------------ fees

FEE_FAQS = [
    ("Do you charge a retainer?",
     ["No. There is no retainer, no listing fee, no marketing charge and no monthly cost. The success fee on completion is the whole of our remuneration, which means a business that does not sell costs you nothing but time."]),
    ("What is the minimum fee?",
     ["S$100,000. On a S$2M transaction that is 5% and works out at exactly the tier rate; below roughly S$1.5M&ndash;S$2M the minimum starts to exceed the tier percentage, and at that point we are poor value and will tell you so rather than take the mandate."]),
    ("Is the fee on enterprise value or on what I receive?",
     ["On transaction value — the total consideration for the business, including deferred payments and earn-out amounts as and when they become payable. We will set out exactly how it is calculated in the appointment agreement before you sign, with a worked example on your own numbers."]),
    ("What if the buyer came to me, not through you?",
     ["Then say so at the outset and we will carve that party out of the mandate in writing, or agree a reduced rate if you want us to run the negotiation anyway. What we will not do is claim a full fee on a buyer who was already at your door."]),
    ("Why do buyers pay you as well?",
     ["Because buyers who transact through us receive a service: screened deal flow, a managed process, data-room coordination and a counterparty who answers. That is a 1% finder&rsquo;s fee on transaction value, success-only. It is disclosed to both sides before anyone signs, and on a sale mandate our duty is to the seller."]),
]

FEES = page_hero(
    [("/fees/", "Fees")],
    "Business broker fees in Singapore, published in full",
    "The rate card, the minimum, what it includes, and how it compares to retainer-based advisers and marketplace listings.",
) + answer_section([
    "Business brokers in Singapore typically charge a success fee of 5&ndash;10% of the sale price, and most do not publish their rates. Ours are tiered and published: 5% of transaction value up to S$5M, 4% from S$5M to S$10M, 3% from S$10M to S$20M, 2% from S$20M to S$50M and 1% above S$50M, with a minimum fee of S$100,000 and no upfront cost of any kind.",
    "Buyers who acquire through us pay a separate 1% finder&rsquo;s fee on transaction value, also success-only, for buy-side process work. Both fees are disclosed to both sides before anything is signed.",
]) + """
<section>
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Sell-side</span><h2>The rate card</h2></div>
    <div class="reveal">""" + FEE_TABLE + """</div>
    <div class="callout mt-2 reveal">
      <h3>The minimum, stated honestly</h3>
      <p>The S$100,000 minimum means the effective rate rises below about S$2M of transaction value — at S$1.5M it is 6.7%, at S$1M it is 10%. So we are the wrong firm below roughly S$1.5M&ndash;S$2M, and we would rather you read that here than find out after two meetings. If your business is below that, a smaller local brokerage or a direct sale to a known party will usually serve you better, and we are happy to point you toward the resources on this site regardless.</p>
    </div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Comparison</span><h2>What the alternatives cost</h2></div>
    <div class="table-wrap reveal">
      <table>
        <caption>Typical market structures. Rates vary by firm; check any quote against what is actually included.</caption>
        <thead><tr><th scope="col">Model</th><th scope="col">Typical cost</th><th scope="col">Worth checking</th></tr></thead>
        <tbody>
          <tr><td>Traditional business broker</td><td>5&ndash;10% success fee</td><td>Rates are often unpublished and quoted after the firm has sized up your business</td></tr>
          <tr><td>M&amp;A advisory firm</td><td>Retainer S$5k&ndash;S$25k/month plus a success fee</td><td>You pay the retainer whether or not the business ever sells</td></tr>
          <tr><td>Marketplace listing</td><td>Listing fee or a small commission</td><td>You run the sale yourself: screening, NDAs, negotiation, diligence, and the confidentiality risk</td></tr>
          <tr><td>Doing it yourself</td><td>Legal fees only</td><td>Workable when a buyer is already known to you; expensive when it means negotiating alone against an experienced acquirer</td></tr>
          <tr class="highlight"><td><strong>Singapore Business Broker</strong></td><td><strong>1&ndash;5% success-only, published above</strong></td><td>S$100,000 minimum — unsuitable below about S$1.5M&ndash;S$2M</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="container">
    <div class="split split-7-5">
      <div class="reveal">
        <span class="eyebrow">Included</span>
        <h2>What the success fee covers</h2>
        <ul>
          <li>Valuation analysis and the defensible range behind it</li>
          <li>Preparation guidance before going to market</li>
          <li>No-name teaser and the full information memorandum</li>
          <li>Buyer identification, outreach and capability screening</li>
          <li>NDA administration and staged disclosure control</li>
          <li>Data-room setup, per-document access control and access logging</li>
          <li>Negotiation of price, structure, earn-out and transition terms</li>
          <li>Term-sheet support and due-diligence coordination</li>
          <li>Working alongside your lawyer and accountant through to completion</li>
        </ul>
      </div>
      <div class="reveal" style="--i:1">
        <div class="panel">
          <h3>Not included</h3>
          <p>Your own legal fees, your accountant&rsquo;s fees, any independent valuation report you commission, and stamp duty. These are third-party costs paid directly by you — budget for them in your net proceeds from the start.</p>
        </div>
        <div class="panel mt-2">
          <h3>Buy-side</h3>
          <p>Buyers acquiring through us pay 1% of transaction value, success-only, for buy-side process services.</p>
          <p class="mt-1"><a class="textlink" href="/buy-a-business-singapore/">What buyers get for that</a></p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="on-stone">
  <div class="container">
    <div class="reveal">""" + DUAL_AGENCY + """</div>
    <div class="section-head mt-3 reveal"><span class="eyebrow">Questions</span><h2>About fees</h2></div>
    <div class="reveal">""" + faq_block(FEE_FAQS) + """</div>
  </div>
</section>

""" + cta_band(
    "Ask us what your sale would cost",
    "Tell us roughly what the business earns and we will show you the fee on your own numbers, with the minimum applied, before you commit to anything at all.",
    "Ask about fees", "/contact/",
    "No retainer, no listing fee, no marketing charge. If it does not sell, you owe nothing.")

add("fees", "Business Broker Fees Singapore | Published Success-Only Rates 1–5%",
    "Our full fee table, published: sell-side success fees of 5% down to 1% by transaction value, S$100,000 minimum, zero upfront cost — plus how that compares to retainer-based M&A advisers and marketplace listings.",
    FEES, crumbs=[("/fees/", "Fees")], faqs=FEE_FAQS)


# ------------------------------------------------------------------ buyers

BUY_FAQS = [
    ("What does the 1% buy-side fee cover?",
     ["Access to screened mandates before they are broadly marketed, an information memorandum prepared to a standard your investment committee can use, coordinated management meetings and site visits, data-room access managed per document, and a process that keeps the seller engaged and answering. It is success-only and payable on completion."]),
    ("Do you represent the buyer or the seller?",
     ["On a sale mandate, the seller. The buy-side fee pays for process services, not for advocacy against our own client. Both fees are disclosed to both sides. If you need someone negotiating for you against a seller we represent, engage your own adviser — we will work with them professionally."]),
    ("What information can I get before signing an NDA?",
     ["Sub-sector, revenue band, adjusted EBITDA band, one or two concrete strengths, reason for sale, and the deal-readiness position — for example whether accounts are audited and whether an IM is ready. Enough to decide whether it is worth your time. The company&rsquo;s identity and anything that could identify it comes after the NDA."]),
    ("How quickly can you move if I am ready?",
     ["Where a mandate is already live and prepared, a screened buyer can have the IM within days of an NDA. Where you are registering ahead of a fit, we will come to you when something matches rather than sending you everything."]),
]

BUYER_SUBJ = quote("Buyer registration — acquisition criteria")
BUY_REG_BTNS = (
    '<a class="btn btn-wa" href="%s">%s Register by WhatsApp</a>'
    '<a class="btn btn-ghost" href="mailto:%s?subject=%s">Register by email</a>'
    % (WA_BUYER, WA_ICON, EMAIL, BUYER_SUBJ))
BUY_CTA_BTNS = (
    '<a class="btn btn-wa" href="%s">%s WhatsApp %s</a>'
    '<a class="btn btn-brass" href="mailto:%s?subject=%s">Email your criteria</a>'
    % (WA_BUYER, WA_ICON, WA_DISPLAY, EMAIL, BUYER_SUBJ))

BUY = page_hero(
    [("/buy-a-business-singapore/", "Buy a business")],
    "Buying a business in Singapore",
    "Screened sell-side mandates from owners who have decided to sell, prepared to a standard you can take to an investment committee. Buy-side fee: 1% of transaction value, success-only.",
    '<div class="btn-row"><a class="btn btn-wa" href="%s">%s Register your acquisition criteria</a></div>' % (WA_BUYER, WA_ICON)
) + answer_section([
    "We act for sellers, and buyers who acquire through us pay a separate 1% finder&rsquo;s fee on transaction value, payable only on completion. What that buys is deal flow that has already been filtered: owners who have made the decision to sell, financial information that has been normalised and can be verified, and a process that keeps moving.",
    "Both fees are disclosed to both sides before anything is signed. Our duty on a sale mandate runs to the seller, and we say so up front rather than being asked.",
]) + """
<section>
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Why acquirers waste time</span>
      <h2>The problem is not finding businesses. It is finding sellers.</h2>
      <p class="lead">Most SME deal flow is owners testing a number. They engage, they enjoy the attention, and they withdraw at term sheet — after you have spent six weeks and a diligence budget.</p>
    </div>
    <div class="grid-3">
      <div class="panel reveal"><div class="icon-tile">""" + I_SHIELD + """</div><h3>Committed sellers</h3><p>Every mandate we market has a signed appointment agreement and an owner who has worked through the decision, the valuation range and the timeline before you see anything.</p></div>
      <div class="panel reveal" style="--i:1"><div class="icon-tile">""" + I_DOC + """</div><h3>Prepared information</h3><p>Normalised earnings with the adjustments shown, three years of statements, and an IM written to be checked rather than admired.</p></div>
      <div class="panel reveal" style="--i:2"><div class="icon-tile">""" + I_CLOCK + """</div><h3>A process that moves</h3><p>Coordinated diligence, managed data-room access and a timetable. Slow deals cost you more than expensive ones.</p></div>
    </div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="split split-5-7">
      <div class="reveal">
        <span class="eyebrow">Registering</span>
        <h2>Tell us what you are actually looking for</h2>
      </div>
      <div class="reveal" style="--i:1">
        <p class="lead">We do not run a mailing list. If your criteria match a live or upcoming mandate we will approach you directly; if they do not, we will not fill your inbox.</p>
        <p>Useful to include when you get in touch:</p>
        <ul>
          <li>Sectors and sub-sectors you understand, and any you will not consider</li>
          <li>Revenue and EBITDA range you are targeting</li>
          <li>Cheque size and how it is funded — equity, debt, or a facility already in place</li>
          <li>Whether you want majority, full ownership, or would back a rolled-over owner</li>
          <li>Whether you will run it, install management, or bolt it onto something existing</li>
          <li>Anything you have already looked at, so we do not re-introduce it</li>
        </ul>
        <div class="btn-row mt-2">""" + BUY_REG_BTNS + """</div>
        <p class="tool-note">Corporate development professionals: everything you send is held in confidence, and we do not disclose who is looking at what. If you would rather not put criteria in writing, call and we will note them without a paper trail.</p>
      </div>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">What you can expect to see</span><h2>Before an NDA, and after</h2></div>
    <div class="split">
      <div class="panel reveal">
        <h3>Pre-NDA</h3>
        <ul>
          <li>Sub-sector, not just a broad industry label</li>
          <li>Revenue band and adjusted EBITDA band</li>
          <li>One or two concrete strengths — certifications, contract base, asset position</li>
          <li>Reason for sale</li>
          <li>Deal-readiness: whether accounts are audited, whether an IM is ready</li>
          <li>Process shape and the indicative offer window</li>
        </ul>
      </div>
      <div class="panel reveal" style="--i:1">
        <h3>Post-NDA</h3>
        <ul>
          <li>Full information memorandum</li>
          <li>Three years of statements with the normalisation set out</li>
          <li>Customer and supplier profile, in structure if not always by name</li>
          <li>Management structure and key-person analysis</li>
          <li>Asset register, tenancy and licence position</li>
          <li>Management meeting and site visit, once the seller approves the introduction</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>For buyers</h2></div>
    <div class="reveal">""" + faq_block(BUY_FAQS) + """</div>
  </div>
</section>

<section class="cta-band">
  <div class="container">
    <div class="cta-inner">
      <div class="reveal">
        <span class="eyebrow">Next step</span>
        <h2>Register your criteria</h2>
        <p class="lead">We will come to you when something fits. No mailing list, no drip of irrelevant teasers, and nothing about your search discussed with anyone.</p>
      </div>
      <div class="cta-side reveal" style="--i:1">""" + BUY_CTA_BTNS + """
        <p class="fineprint">Buy-side fee: 1% of transaction value, success-only, disclosed to both sides.</p>
      </div>
    </div>
  </div>
</section>"""

add("buy-a-business-singapore",
    "Buy a Business in Singapore | Screened SME Acquisition Opportunities",
    "Acquisition opportunities from committed Singapore SME sellers, prepared for investment-committee review. Buy-side finder's fee of 1% of transaction value, success-only, disclosed to both sides.",
    BUY, crumbs=[("/buy-a-business-singapore/", "Buy a business")], faqs=BUY_FAQS)


# ------------------------------------------------------------------ about

ABOUT = page_hero(
    [("/about/", "About")],
    "About the firm",
    "Who you would actually be working with, what we are good at, and what we are not.",
) + """
<section>
  <div class="container">
    <div class="split split-7-5">
      <div class="reveal">
        <span class="eyebrow">The firm</span>
        <h2>A boutique sell-side practice, and what that trade-off means</h2>
        <p class="lead">Singapore Business Broker is the sell-side brokerage practice of {parent}, a Singapore M&amp;A advisory founded and led by Eric Ong.</p>
        <p>We are deliberately small. On your mandate you work with the founder from the first conversation to completion — not a business-development person who signs you up and hands you to someone junior. That is the advantage, and you should weigh the corresponding disadvantage honestly: a boutique does not have the deal volume, the research desk or the international coverage of a large corporate finance house. If your business needs a cross-border auction with twenty international bidders, engage a firm built for that.</p>
        <p>What we are built for is the Singapore SME in the S$2M&ndash;S$20M revenue band, where the owner is the business, confidentiality is existential, and the difference between a good outcome and a poor one is whether anyone ran a real process.</p>
      </div>
      <div class="reveal" style="--i:1">
        <div class="callout">
          <h3>Check us before you reply</h3>
          <p>You will, and you should. We are registered in Singapore and our parent firm publishes named client references. If there is something you cannot verify from the outside, ask in the first call and we will answer it directly.</p>
          <p class="mt-1"><a class="textlink" href="{parent_url}" rel="noopener">{parent}</a></p>
        </div>
        <div class="callout mt-2">
          <h2>Talk to us</h2>
          <p>WhatsApp <a href="{wa}">{wa_display}</a><br>Email <a href="mailto:{email}">{email}</a></p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="on-paper">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">How we work</span><h2>Four commitments, each one checkable</h2></div>
    <ul class="deflist reveal">
      <li><span class="dt">We publish our fees</span><span class="dd">The full tier table is on this site. You can calculate what we would earn from your sale before you speak to us, and the number will not change once we have seen your accounts.</span></li>
      <li><span class="dt">We say no</span><span class="dd">If a sale is premature, if the business is below the size where we add value, or if the seller is not actually committed, we say so in the first conversation rather than taking a mandate that will not complete.</span></li>
      <li><span class="dt">We state the agency position unprompted</span><span class="dd">We act for the seller on a sale mandate; buyers pay a separate 1% for process services; both are disclosed to both sides. Nobody has to ask.</span></li>
      <li><span class="dt">We do not name clients without permission</span><span class="dd">Live mandates are described only in disguised terms. Completed transactions are named only where the client has given permission, which is why our published references are few and real rather than many and vague.</span></li>
    </ul>
  </div>
</section>

<section class="on-stone">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Proof</span><h2>What you can verify</h2></div>
    {proof}
  </div>
</section>

{cta}""".format(parent=PARENT, parent_url=PARENT_URL, wa=WA_SELLER, wa_display=WA_DISPLAY,
                email=EMAIL, proof=PROOF_BLOCK,
                cta=cta_band(
                    "Speak to the person who would run your sale",
                    "There is no intake team here. The first call is with the person who would handle the mandate, which is the point of using a boutique in the first place.",
                    "Start a conversation", "/contact/",
                    "Thirty minutes, no fee, no obligation."))

add("about", "About | Singapore Business Broker &mdash; Founder-Led Sell-Side M&A",
    "Singapore Business Broker is the sell-side practice of The Funding Assembly, founded and led by Eric Ong. A boutique working with SME owners in the S$2M–S$20M revenue band — including the trade-offs that come with that.",
    ABOUT, crumbs=[("/about/", "About")])


# ------------------------------------------------------------------ faq

ALL_FAQS = HOME_FAQS + SELL_FAQS + VAL_FAQS[:3] + FEE_FAQS[:3] + PROC_FAQS[:3] + EXIT_FAQS[:2]

FAQ_PAGE = page_hero(
    [("/faq/", "FAQ")],
    "Questions Singapore business owners ask",
    "Fees, confidentiality, valuation, timing and process — answered directly, including the answers that are inconvenient for us.",
) + """
<section class="on-stone">
  <div class="container">
    <div class="reveal">""" + faq_block(ALL_FAQS) + """</div>
    <div class="btn-row mt-3 reveal">
      <a class="btn btn-brass" href="/sale-readiness/">Score your sale readiness</a>
      <a class="btn btn-ghost" href="/contact/">Ask something else</a>
    </div>
  </div>
</section>

""" + cta_band(
    "Question not answered here?",
    "Ask it directly. You do not have to identify your company, and a question is not the start of a sales process.",
    "Ask a question", "/contact/",
    "WhatsApp is usually the fastest route, and it is as confidential as email.")

add("faq", "FAQ | Selling a Business in Singapore — Fees, Confidentiality, Valuation",
    "Direct answers on Singapore business broker fees, keeping a sale confidential from staff and customers, how SMEs are valued, how long a sale takes, and what happens at each stage.",
    FAQ_PAGE, crumbs=[("/faq/", "FAQ")], faqs=ALL_FAQS)


# ------------------------------------------------------------------ contact

CONTACT = page_hero(
    [("/contact/", "Contact")],
    "Start a confidential conversation",
    "No fee, no obligation, and nothing leaves the conversation. You do not have to tell us the name of your company to ask a question.",
) + """
<section class="on-stone" style="padding-top:2.75rem">
  <div class="container">
    <div class="split split-7-5">
      <div class="reveal">
        <div class="tool">
          <span class="eyebrow">Direct lines</span>
          <h2 style="font-size:1.7rem">Three ways to reach us</h2>
          <ul class="deflist mt-2">
            <li><span class="dt">WhatsApp</span><span class="dd"><a class="textlink" href="{wa}">{wa_display}</a><br>Usually the fastest, and the one most owners prefer. Message outside office hours if that suits you better.</span></li>
            <li><span class="dt">Email</span><span class="dd"><a class="textlink" href="mailto:{email}">{email}</a><br>Tell us roughly the sector, the revenue and what you are trying to work out. You do not need to name the company.</span></li>
            <li><span class="dt">Phone</span><span class="dd"><a class="textlink" href="tel:+6589518821">{wa_display}</a><br>If you would rather not put anything in writing at all, call. Nothing is recorded and nothing is written down that you have not agreed to.</span></li>
          </ul>
          <div class="btn-row mt-3">
            <a class="btn btn-wa" href="{wa}">{wa_icon} WhatsApp now</a>
            <a class="btn btn-brass" href="mailto:{email}?subject={subj}">Email us</a>
          </div>
          <p class="tool-note">We reply to enquiries the same working day wherever possible. Your details stay with us — we do not share enquirer information with buyers, partners or anyone else, and there is no mailing list to be added to.</p>
        </div>
      </div>
      <div>
        <div class="callout reveal">
          <h3>What the first conversation covers</h3>
          <p>About thirty minutes: what you have built, what you want afterwards, your timeline, and an honest first view on what the business might fetch and what would change that. No mandate is signed at that stage.</p>
        </div>
        <div class="callout mt-2 reveal">
          <h3>If you are not ready to sell</h3>
          <p>Most owners we speak to are twelve to twenty-four months out. That is the most useful time to call, because it is the window where preparation still changes the price.</p>
        </div>
        <div class="callout mt-2 reveal">
          <h3>If you are a buyer</h3>
          <p>Send your acquisition criteria and we will come to you when a mandate fits. <a class="textlink" href="/buy-a-business-singapore/">What buyers get</a></p>
        </div>
        <div class="callout mt-2 reveal">
          <h3>If you are a professional adviser</h3>
          <p>Lawyers, corporate secretaries, accountants and bankers with a client facing a transition: we work on referral and will keep you informed of anything affecting your client, including bad news, within a working day.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container center narrow">
    <span class="eyebrow center-e">Before you call</span>
    <h2>Two things worth knowing</h2>
    <p class="lead">We work with Singapore businesses of roughly S$2M&ndash;S$20M revenue, and our minimum fee is S$100,000 — which makes us poor value below about S$1.5M&ndash;S$2M of transaction value. If that is your situation, say so and we will point you at something more useful rather than take the meeting.</p>
    <div class="btn-row mt-2" style="justify-content:center">
      <a class="btn btn-ghost" href="/fees/">The full fee table</a>
      <a class="btn btn-ghost" href="/sale-readiness/">Sale-readiness scorecard</a>
    </div>
  </div>
</section>""".format(wa=WA_SELLER, wa_display=WA_DISPLAY, email=EMAIL, wa_icon=WA_ICON,
                     subj=quote("Confidential enquiry"))

add("contact", "Contact | Confidential Business Sale Enquiry — Singapore",
    "Start a confidential conversation about selling your Singapore business. WhatsApp +65 8951 8821 or email — no fee, no obligation, and you do not have to name your company to ask a question.",
    CONTACT, crumbs=[("/contact/", "Contact")],
    extra_schema=[{
        "@type": "ContactPage",
        "url": SITE + "/contact/",
        "mainEntity": {"@id": SITE + "/#org"},
    }])


# ---------------------------------------------------------------- writers

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def render(page):
    canonical = SITE + "/" + (page["slug"] + "/" if page["slug"] else "")
    return SHELL.format(
        title=page["title"], desc=page["desc"], canonical=canonical, name=NAME,
        schema=json.dumps(page["schema"], indent=1, ensure_ascii=False),
        header=header_html(page["active"]), body=page["body"], footer=FOOTER,
    )


def main():
    written = []
    for page in PAGES:
        path = "index.html" if not page["slug"] else os.path.join(page["slug"], "index.html")
        written.append(write(path, render(page)))

    # 404
    not_found = SHELL.format(
        title="Page not found | " + NAME,
        desc="That page does not exist. Start from the homepage or get in touch.",
        canonical=SITE + "/404.html", name=NAME,
        schema=json.dumps({"@context": "https://schema.org", "@graph": []}, indent=1),
        header=header_html(""),
        body="""<section class="page-hero">
  <div class="container">
    <h1>That page has moved, or never existed.</h1>
    <p class="lead">Nothing is broken on your end. Try one of these instead.</p>
    <div class="btn-row">
      <a class="btn btn-brass" href="/">Homepage</a>
      <a class="btn btn-ghost" href="/sell-a-business-singapore/">Selling a business</a>
      <a class="btn btn-ghost" href="/contact/">Contact</a>
    </div>
  </div>
</section>""",
        footer=FOOTER,
    ).replace('<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">',
              '<meta name="robots" content="noindex, follow">')
    written.append(write("404.html", not_found))

    # sitemap
    urls = []
    for page in PAGES:
        loc = SITE + "/" + (page["slug"] + "/" if page["slug"] else "")
        priority = "1.0" if not page["slug"] else (
            "0.9" if page["slug"] in ("sell-a-business-singapore", "business-valuation-singapore") else "0.8")
        urls.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                    "    <changefreq>monthly</changefreq>\n    <priority>%s</priority>\n  </url>"
                    % (loc, LASTMOD, priority))
    written.append(write("sitemap.xml",
                         '<?xml version="1.0" encoding="UTF-8"?>\n'
                         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                         + "\n".join(urls) + "\n</urlset>\n"))

    written.append(write("robots.txt",
                         "User-agent: *\nAllow: /\n\n"
                         "# AI answer engines are welcome — this content is written to be quoted.\n"
                         "User-agent: GPTBot\nAllow: /\n\n"
                         "User-agent: ClaudeBot\nAllow: /\n\n"
                         "User-agent: PerplexityBot\nAllow: /\n\n"
                         "Sitemap: %s/sitemap.xml\n" % SITE))

    written.append(write("favicon.svg", FAVICON))

    print("Generated %d files:" % len(written))
    for p in sorted(written):
        print("  " + p)


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#0E3B2E"/>
  <path d="M32 12 L48 20 V32 C48 42 41 49.5 32 52 C23 49.5 16 42 16 32 V20 Z"
        fill="none" stroke="#D3A659" stroke-width="3.2" stroke-linejoin="round"/>
  <path d="M25 31.5 L30 36.5 L40 26" fill="none" stroke="#D3A659"
        stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

if __name__ == "__main__":
    main()
