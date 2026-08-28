/**
 * JSON-LD builders. Every block is rendered server side into the initial HTML
 * by Base.astro, never injected on the client, so crawlers see it without
 * executing JavaScript.
 *
 * Two rules hold throughout:
 *  - Schema must mirror what is visible on the page. FAQ entries come from the
 *    same data the page renders; Article dates come from the same frontmatter
 *    as the visible "Updated ..." byline.
 *  - Everything references the single Organization node by @id rather than
 *    repeating the firm's details, so there is one authoritative entity.
 */
import site from '../data/site.json';

export const SITE_URL = 'https://www.singaporebusinessbroker.com';
export const ORG_ID = `${SITE_URL}/#organization`;
export const WEBSITE_ID = `${SITE_URL}/#website`;

const abs = (path: string) => new URL(path, SITE_URL).href;

export function organization() {
  return {
    '@type': 'ProfessionalService',
    '@id': ORG_ID,
    name: site.name,
    url: `${SITE_URL}/`,
    logo: abs('/images/logo.png'),
    image: abs('/images/og-share.jpg'),
    telephone: site.phoneDisplay,
    email: site.email,
    areaServed: { '@type': 'Country', name: 'Singapore' },
    parentOrganization: {
      '@type': 'Organization',
      name: site.parentLegal,
      url: site.parentUrl,
    },
    description:
      'Sell-side M&A advisors for Singapore SME owners with S$3m to S$30m businesses. ' +
      'Success-based fees, confidential process, vetted buyer network.',
    knowsAbout: [
      'SME mergers and acquisitions',
      'Business valuation',
      'Sell-side advisory',
      'Business succession',
      'Singapore SME sales',
    ],
    // ERIC-TODO: add a PostalAddress block here once a registered address may be
    // published. It is the biggest single local-SEO win outstanding and is
    // required for parity with a Google Business Profile.
  };
}

export function website() {
  return {
    '@type': 'WebSite',
    '@id': WEBSITE_ID,
    url: `${SITE_URL}/`,
    name: site.name,
    inLanguage: 'en-SG',
    publisher: { '@id': ORG_ID },
  };
}

export function service(serviceType: string) {
  return {
    '@type': 'Service',
    serviceType,
    provider: { '@id': ORG_ID },
    areaServed: { '@type': 'Country', name: 'Singapore' },
  };
}

/** Built from the same array the page renders, so the two cannot drift. */
export function faqPage(items: { q: string; a: string }[]) {
  return {
    '@type': 'FAQPage',
    mainEntity: items.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  };
}

export function article(opts: {
  headline: string;
  description: string;
  path: string;
  published: Date;
  modified?: Date;
}) {
  return {
    '@type': 'Article',
    headline: opts.headline,
    description: opts.description,
    // ERIC-TODO: switch author to a Person referencing a named advisor once the
    // Advisors section on /about is populated.
    author: { '@type': 'Organization', name: site.name, '@id': ORG_ID },
    publisher: { '@id': ORG_ID },
    datePublished: opts.published.toISOString().slice(0, 10),
    dateModified: (opts.modified ?? opts.published).toISOString().slice(0, 10),
    mainEntityOfPage: abs(opts.path),
    inLanguage: 'en-SG',
  };
}

/** Mirrors the visible breadcrumb trail rendered by PageHeader. */
export function breadcrumbs(crumbs: { href: string; label: string }[]) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `${SITE_URL}/` },
      ...crumbs.map((c, i) => ({
        '@type': 'ListItem',
        position: i + 2,
        name: c.label,
        item: abs(c.href),
      })),
    ],
  };
}
