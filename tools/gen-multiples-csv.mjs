/**
 * Regenerates public/data/sme-multiples-singapore.csv from src/data/multiples.json,
 * so the download can never drift from the table on the page.
 * Run: npm run csv  (also runs as part of prebuild)
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const m = JSON.parse(readFileSync(join(ROOT, 'src/data/multiples.json'), 'utf8'));

const rows = [
  '# Indicative EV / normalised EBITDA multiple ranges for Singapore SME transactions.',
  '# Orientation only, not a measured dataset and not a valuation.',
  '# Source: https://www.singaporebusinessbroker.com/data/sme-multiples-singapore',
  'sector,low_multiple,high_multiple,basis',
  ...m.sectors.map((s) => `"${s.name}",${s.low},${s.high},"${m.basis}"`),
];

mkdirSync(join(ROOT, 'public/data'), { recursive: true });
writeFileSync(join(ROOT, 'public/data/sme-multiples-singapore.csv'), rows.join('\n') + '\n');
console.log(`csv: ${m.sectors.length} sectors`);
