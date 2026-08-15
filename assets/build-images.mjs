/**
 * Downloads the handoff photography, repairs the two defective assets, and
 * emits sized webp into public/images. Run: node assets/build-images.mjs
 *
 * Two source images came out of the generator with hallucinated text baked in:
 *   hero-owner.png  a fake browser header bar across the top, plus two blocks
 *                   of garbled lettering across the middle of the frame.
 *   og-share.png    a split-screen artifact, garbled text and a fake "M&A"
 *                   logo. Unusable at any crop.
 * The hero is recovered by cropping the largest 5:4 window that sits entirely
 * above the text band, which yields a clean portrait. The OG card is rebuilt
 * from the (clean) deal-meeting photograph in tools/make-og.mjs instead.
 * Both should be replaced when clean renders are available.
 */
import { readFileSync, mkdirSync, existsSync, rmSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'public/images');
const TMP = join(ROOT, '.image-cache');
mkdirSync(OUT, { recursive: true });
mkdirSync(TMP, { recursive: true });

const manifest = JSON.parse(readFileSync(join(ROOT, 'assets/images.json'), 'utf8'));

async function fetchSource(file, url) {
  const dest = join(TMP, file);
  if (existsSync(dest)) return dest;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${file}: HTTP ${res.status}`);
  const { writeFileSync } = await import('node:fs');
  writeFileSync(dest, Buffer.from(await res.arrayBuffer()));
  return dest;
}

const kb = (p) => `${(statSync(p).size / 1024).toFixed(0)} KB`;

async function emit(pipeline, name, width) {
  const dest = join(OUT, `${name}.webp`);
  await pipeline.clone().resize({ width, withoutEnlargement: false, kernel: 'lanczos3' })
    .webp({ quality: 80, effort: 6 }).toFile(dest);
  console.log(`  ${name}.webp  ${width}w  ${kb(dest)}`);
}

const src = {};
for (const im of manifest.images) src[im.file] = await fetchSource(im.file, im.url);

// hero: drop the fake header bar (179px), then take the largest 5:4 window
// clear of the garbled text band, which begins at y=588 of the remaining frame.
console.log('hero-owner (repaired crop)');
{
  const H = 585, W = Math.round(H * 5 / 4), LEFT = 680;
  const cropped = sharp(src['hero-owner.png'])
    .extract({ left: 0, top: 179, width: 2048, height: 1536 - 179 })
    .extract({ left: LEFT, top: 0, width: W, height: H });
  const buf = await cropped.png().toBuffer();
  await emit(sharp(buf).sharpen({ sigma: 0.7 }), 'hero-owner', 1170);
  await emit(sharp(buf), 'hero-owner@720', 731);
}

console.log('deal-meeting');
await emit(sharp(src['deal-meeting.png']), 'deal-meeting', 1400);
await emit(sharp(src['deal-meeting.png']), 'deal-meeting@800', 800);

console.log('industrial-estate');
await emit(sharp(src['industrial-estate.png']), 'industrial-estate', 1000);
await emit(sharp(src['industrial-estate.png']), 'industrial-estate@640', 640);

console.log('logistics-warehouse');
await emit(sharp(src['logistics-warehouse.png']), 'logistics-warehouse', 900);
await emit(sharp(src['logistics-warehouse.png']), 'logistics-warehouse@560', 560);

// og-share.png from the manifest is discarded: see the header comment.
console.log('\nog-share is built by tools/make-og.mjs (generator output unusable)');
rmSync(TMP, { recursive: true, force: true });
