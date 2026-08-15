/**
 * Copy lint. CLAUDE.md: "Zero em-dashes in any rendered string. Grep before
 * commit." Also catches the banned marketing vocabulary and leftover
 * placeholder brackets. Runs against dist/, so it checks what actually ships
 * rather than what is in source.
 *
 * npm run build && npm run lint:copy
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist');

const RULES = [
  { name: 'em dash', re: /—/g },
  { name: 'en dash', re: /–/g },
  { name: 'banned word', re: /\b(elevate|elevating|seamless|seamlessly|unleash|unleashing|leverage as a verb)\b/gi },
  { name: 'placeholder bracket', re: /\[(TODO|TBC|VERBATIM|confirm|insert|xxx|\+65 X)/gi },
  { name: 'lorem ipsum', re: /\blorem ipsum\b/gi },
];

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (extname(p) === '.html') out.push(p);
  }
  return out;
}

/** Text nodes only: scripts, styles and attributes are not rendered prose. */
function visibleText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ');
}

let failures = 0;
let files = 0;

try {
  statSync(DIST);
} catch {
  console.error('dist/ not found. Run `npm run build` first.');
  process.exit(2);
}

for (const file of walk(DIST)) {
  files += 1;
  const text = visibleText(readFileSync(file, 'utf8'));
  for (const rule of RULES) {
    const hits = [...text.matchAll(rule.re)];
    if (!hits.length) continue;
    failures += hits.length;
    const rel = file.slice(ROOT.length + 1);
    for (const h of hits.slice(0, 3)) {
      const ctx = text.slice(Math.max(0, h.index - 45), h.index + 45).replace(/\s+/g, ' ').trim();
      console.error(`${rel}: ${rule.name} -> ...${ctx}...`);
    }
    if (hits.length > 3) console.error(`${rel}: ${rule.name} -> +${hits.length - 3} more`);
  }
}

console.log(`\nchecked ${files} rendered pages`);
if (failures) {
  console.error(`FAIL: ${failures} copy violation(s)`);
  process.exit(1);
}
console.log('PASS: no em-dashes, banned words or placeholders in rendered copy');
