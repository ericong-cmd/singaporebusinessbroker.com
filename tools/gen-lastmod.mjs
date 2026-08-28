/**
 * Builds src/data/lastmod.json: a route -> ISO date map the sitemap uses for
 * real <lastmod> values instead of a blanket changefreq.
 *
 * Content routes take their date from frontmatter, so the sitemap can never
 * disagree with the "Updated ..." line rendered on the page. Static routes take
 * `siteUpdated` from src/data/site.json; bump that when you edit them. Git
 * dates are not used because Vercel builds from an uploaded source tree with no
 * history. Run: npm run lastmod (also runs as prebuild).
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const site = JSON.parse(readFileSync(join(ROOT, 'src/data/site.json'), 'utf8'));
const fallback = site.siteUpdated;
if (!fallback) throw new Error('src/data/site.json needs a "siteUpdated" date (YYYY-MM-DD)');

const iso = (d) => new Date(d).toISOString().slice(0, 10);

/** Pull a date field out of MDX frontmatter without a YAML dependency. */
function frontmatterDate(file) {
  const raw = readFileSync(file, 'utf8');
  const fm = raw.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) return null;
  for (const key of ['updated', 'published']) {
    const m = fm[1].match(new RegExp(`^${key}:\\s*['"]?(\\d{4}-\\d{2}-\\d{2})`, 'm'));
    if (m) return m[1];
  }
  return null;
}

const map = {};
const collections = [
  ['sectors', '/sell'],
  ['guides', '/guides'],
  ['cases', '/case-studies'],
  ['insights', '/insights'],
];

for (const [dir, base] of collections) {
  const full = join(ROOT, 'src/content', dir);
  if (!existsSync(full)) continue;
  let newest = null;
  for (const f of readdirSync(full).filter((f) => f.endsWith('.mdx'))) {
    const slug = f.replace(/\.mdx$/, '');
    const d = frontmatterDate(join(full, f)) ?? fallback;
    map[`${base}/${slug}`] = d;
    if (!newest || d > newest) newest = d;
  }
  // Index pages are as fresh as their newest entry.
  if (base !== '/sell') map[base] = newest ?? fallback;
}

const staticRoutes = ['/', '/sell-your-business', '/valuation', '/buyers', '/about', '/contact', '/book-a-call'];
for (const r of staticRoutes) map[r] = fallback;

const sorted = Object.fromEntries(Object.entries(map).sort(([a], [b]) => a.localeCompare(b)));
writeFileSync(join(ROOT, 'src/data/lastmod.json'), JSON.stringify(sorted, null, 2) + '\n');
console.log(`lastmod: ${Object.keys(sorted).length} routes (fallback ${iso(fallback)})`);
