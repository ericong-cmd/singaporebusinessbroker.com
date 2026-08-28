/**
 * Renders public/images/og-share.jpg (and .webp), public/images/logo.png (the
 * Organization logo referenced by JSON-LD) and the apple-touch-icon.
 *
 * The handoff shipped a generated og-share.png with a split-screen artifact,
 * garbled lettering and a hallucinated "M&A" logo, so it is not used. This
 * composes the card instead: the clean deal-meeting photograph, a scrim, and
 * real type in the site's own font. Run: npm run og
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import sharp from 'sharp';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'public/images');
mkdirSync(OUT, { recursive: true });

const b64 = (p, mime) => `data:${mime};base64,${readFileSync(join(ROOT, p)).toString('base64')}`;
const font = b64('public/fonts/geist-var-latin.woff2', 'font/woff2');
const mono = b64('public/fonts/geistmono-var-latin.woff2', 'font/woff2');
const photo = b64('public/images/deal-meeting.webp', 'image/webp');

const html = `<!doctype html><meta charset="utf-8"><style>
  @font-face{font-family:Geist;src:url('${font}') format('woff2');font-weight:300 600}
  @font-face{font-family:'Geist Mono';src:url('${mono}') format('woff2');font-weight:400 500}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1200px;height:630px;font-family:Geist,sans-serif;overflow:hidden}
  .card{position:relative;width:1200px;height:630px;background:#0e1a2b;color:#f6f7f4}
  .photo{position:absolute;inset:0;background:url('${photo}') center/cover;opacity:.42}
  .scrim{position:absolute;inset:0;background:linear-gradient(100deg,#0e1a2b 32%,rgba(14,26,43,.72) 62%,rgba(14,26,43,.42) 100%)}
  .glow{position:absolute;top:-160px;right:-120px;width:620px;height:620px;border-radius:50%;
        background:rgba(15,107,79,.42);filter:blur(90px)}
  .inner{position:relative;height:100%;padding:72px 80px;display:flex;flex-direction:column;justify-content:space-between}
  .brand{display:flex;align-items:center;gap:16px}
  .mark{width:46px;height:46px;border-radius:50%;background:#f6f7f4;color:#0e1a2b;display:grid;place-items:center;
        font-size:17px;font-weight:500;letter-spacing:-.5px}
  .name{font-size:21px;font-weight:500;letter-spacing:-.2px}
  h1{font-size:66px;line-height:1.04;font-weight:500;letter-spacing:-2.4px;max-width:15ch}
  .accent{color:#7fd1b3}
  .foot{display:flex;align-items:flex-end;justify-content:space-between;gap:40px}
  .sub{font-size:23px;font-weight:300;color:rgba(246,247,244,.72);max-width:34ch;line-height:1.4}
  .pill{font-family:'Geist Mono',monospace;font-size:16px;letter-spacing:.4px;color:#7fd1b3;
        border:1px solid rgba(127,209,179,.42);border-radius:999px;padding:11px 22px;white-space:nowrap}
</style>
<div class="card">
  <div class="photo"></div><div class="scrim"></div><div class="glow"></div>
  <div class="inner">
    <div class="brand"><div class="mark">SB</div><div class="name">Singapore Business Broker</div></div>
    <h1>Sell your business <span class="accent">confidentially</span>, at the right price.</h1>
    <div class="foot">
      <p class="sub">Sell-side M&amp;A for Singapore SME owners. Free valuation estimate.</p>
      <div class="pill">S$3m to S$30m</div>
    </div>
  </div>
</div>`;

const tmp = join(ROOT, '.og.html');
writeFileSync(tmp, html);

let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  console.error(
    'This script needs Playwright, which is not a project dependency because\n' +
    'it is only used to regenerate the share image. Run:\n\n' +
    '  npm i -D playwright && npx playwright install chromium\n'
  );
  process.exit(1);
}
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 2 });
await page.goto(pathToFileURL(tmp).href, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
const buf = await page.screenshot({ type: 'png' });

// Icon: the same mark, so the tab and the share card agree.
const iconHtml = `<!doctype html><meta charset="utf-8"><style>
  @font-face{font-family:Geist;src:url('${font}') format('woff2');font-weight:300 600}
  *{margin:0;padding:0}
  body{width:512px;height:512px;background:#0e1a2b;display:grid;place-items:center;
       font-family:Geist,sans-serif;color:#f6f7f4;font-size:210px;font-weight:500;letter-spacing:-9px}
</style><div>SB</div>`;
const tmpIcon = join(ROOT, '.icon.html');
writeFileSync(tmpIcon, iconHtml);
await page.setViewportSize({ width: 512, height: 512 });
await page.goto(pathToFileURL(tmpIcon).href, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
const iconBuf = await page.screenshot({ type: 'png' });
await browser.close();

await sharp(buf).resize(1200, 630).jpeg({ quality: 86 }).toFile(join(OUT, 'og-share.jpg'));
await sharp(buf).resize(1200, 630).webp({ quality: 84 }).toFile(join(OUT, 'og-share.webp'));
await sharp(iconBuf).resize(180, 180).png().toFile(join(ROOT, 'public/apple-touch-icon.png'));
// Organization logo for JSON-LD. Google wants at least 112px on the short side;
// 512 gives room for rich results and social profiles.
await sharp(iconBuf).resize(512, 512).png().toFile(join(ROOT, 'public/images/logo.png'));

const { unlinkSync } = await import('node:fs');
unlinkSync(tmp);
unlinkSync(tmpIcon);
console.log('wrote og-share.jpg, og-share.webp, logo.png, apple-touch-icon.png');
