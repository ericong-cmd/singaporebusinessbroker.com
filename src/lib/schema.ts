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
import advisorsData from '../data/advisors.json';

export const SITE_URL = 'https://www.singaporebusinessbroker.com';

export type Advisor = {
  name: string;
  role: string;
  bio: string;
  founder?: boolean;
  credentials?: string[];
  linkedin?: string;
  photo?: string;
};

export const advisors = advisorsData.advisors as Advisor[];
export const personId = (name: string) => `${SITE_URL}/about#${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
export const ORG_ID = `${SITE_URL}/#organization`;
export const WEBSITE_ID = `${SITE_URL}/#website`;

const abs = (path: string) => new URL(path, SITE_URL).href;

export function organization() {
  const founder = advisors.find((a) => a.founder) ?? advisors[0];
  // sameAs is how Google ties this site to the Google Business Profile and any
  // other public profile. Add each URL to site.json as it goes live.
  const sameAs = Object.entries(site.profiles ?? {})
    .filter(([k, v]) => !k.startsWith('_') && typeof v === 'string' && v.trim())
    .map(([, v]) => v as string);
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
    ...(sameAs.length ? { sameAs } : {}),
    ...(founder
      ? { founder: { '@id': personId(founder.name) }, employee: { '@id': personId(founder.name) } }
      : {}),
    // ERIC-TODO: add a PostalAddress block here once a registered address may be
    // published. It must match the Google Business Profile listing exactly
    // (same name, same address, same phone) or the two signals fight each other.
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

/** Person node for a named advisor, referenced by @id from Organization and Article. */
export function person(a: Advisor) {
  return {
    '@type': 'Person',
    '@id': personId(a.name),
    name: a.name,
    jobTitle: a.role,
    description: a.bio,
    worksFor: { '@id': ORG_ID },
    ...(a.credentials?.length ? { hasCredential: a.credentials } : {}),
    ...(a.linkedin ? { sameAs: [a.linkedin] } : {}),
    ...(a.photo ? { image: abs(a.photo) } : {}),
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
  /** Attribute to a named advisor only when a person has actually reviewed the
   *  page. A named byline on unreviewed drafts is the E-E-A-T signal that
   *  backfires the moment a reader finds an error in one. */
  reviewedBy?: Advisor | null;
}) {
  return {
    '@type': 'Article',
    headline: opts.headline,
    description: opts.description,
    author: opts.reviewedBy
      ? { '@id': personId(opts.reviewedBy.name) }
      : { '@type': 'Organization', name: site.name, '@id': ORG_ID },
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
