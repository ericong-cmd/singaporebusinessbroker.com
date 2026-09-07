/**
 * Email templates for the valuation endpoint.
 *
 * Two templates, two audiences:
 *   sellerReport  goes to the owner who filled the form. It is a document they
 *                 may forward to a spouse or an accountant, so it explains its
 *                 own arithmetic rather than only stating a number.
 *   teamAlert     goes to TEAM_EMAIL on a hot lead. It replaced a raw JSON
 *                 dump, which was unreadable on a phone at the moment it
 *                 actually matters.
 *
 * Written for email clients, not browsers. That means tables for layout rather
 * than flexbox or grid, every style inline because Gmail strips <style> blocks
 * in many contexts, a system font stack because self-hosted Geist cannot load
 * in an inbox, no images so nothing breaks when remote content is blocked by
 * default, and a hard 600px width. None of these are stylistic preferences;
 * each one is a client that would otherwise render the report badly.
 */
import { esc } from './_lib.js';

const INK = '#0e1a2b';
const INK2 = '#2b3a4f';
const INK3 = '#5b687a';
const PAPER = '#f6f7f4';
const ACCENT = '#0f6b4f';
const ACCENT_SOFT = '#e3f1ea';
const LINE = '#e2e5e0';
const FONT =
  "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif";
const MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace";

export type ReportData = {
  name: string;
  email: string;
  phone: string;
  sector: string;
  revenue: number;
  ebitda: number;
  years: number;
  ownership: number;
  dependency: 'low' | 'med' | 'high';
  timeline: number;
  evLow?: number;
  evHigh?: number;
  range: string;
  score: 'hot' | 'warm' | 'cold';
  page?: string;
  referrer?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
};

const SITE = 'https://www.singaporebusinessbroker.com';
const CONTACT = 'singaporebusinessbroker@thefundingassembly.com';
const MAILTO = `mailto:${CONTACT}?subject=Enquiry%20on%20selling%20my%20business`;

const money = (v: number) =>
  v >= 1e6 ? `S$${(v / 1e6).toFixed(2)}m` : `S$${Math.round(v / 1e3).toLocaleString('en-SG')}k`;

const revenueBand = (r: number) =>
  r >= 30 ? 'Above S$30m' : r >= 10 ? 'S$10m to S$30m' : r >= 3 ? 'S$3m to S$10m'
  : r >= 1 ? 'S$1m to S$3m' : 'Under S$1m';

const dependencyLabel = { low: 'Low', med: 'Moderate', high: 'High' } as const;

const timelineLabel = (m: number) =>
  m <= 6 ? 'Within 6 months' : m <= 12 ? '6 to 12 months'
  : m <= 18 ? '12 to 18 months' : m <= 24 ? '18 to 24 months' : 'More than 2 years';

/** The adjustments the estimator applied, restated so the number is auditable. */
function adjustments(d: ReportData): string[] {
  const out: string[] = [];
  if (d.dependency === 'high') out.push('Owner dependency is high, so the range is reduced by 15 percent. This is the single largest adjustment the estimator makes, because it decides whether a buyer is acquiring a business or a job.');
  if (d.dependency === 'low') out.push('Owner dependency is low, so the range is increased by 5 percent. A business that runs without its owner is worth more per dollar of profit.');
  if (d.years < 3) out.push(`The business has been trading ${d.years === 1 ? 'one year' : `${d.years} years`}, under the three years most buyers want to see, so the range is reduced by 10 percent. Three clean years is the standard look-back and the clock only starts when the first clean year does.`);
  if (d.revenue < 1) out.push('Revenue is under S$1m, so the upper multiple is capped. Smaller businesses attract a narrower buyer pool, mostly individuals buying themselves a job, and that limits the top of the range.');
  if (!out.length) out.push('No downward adjustments applied. The range is the sector range applied to the profit figure you gave.');
  return out;
}

/** What this specific owner should do next, driven by the same score the team sees. */
function nextSteps(d: ReportData): { headline: string; body: string; cta: string } {
  if (d.score === 'hot') {
    return {
      headline: 'You are in the range we act on',
      body: 'Your revenue, profitability and timeline put you squarely in the S$3m to S$30m range we advise on, and your timeline is short enough that preparation and process would overlap. The useful next step is a conversation about what a real process would look like for your business, not another calculator.',
      cta: 'Reply to this email, or write to us directly',
    };
  }
  if (d.score === 'warm') {
    return {
      headline: 'Worth a conversation before you commit to anything',
      body: 'You are close to, or approaching, the range we work in. The question worth answering now is whether preparation would move your number enough to be worth waiting for. That is usually decided by two or three specific things rather than a general improvement in trading.',
      cta: 'Tell us about your business',
    };
  }
  return {
    headline: 'Preparation will be worth more than a process right now',
    body: 'At this size the buyer pool is mostly individuals rather than trade or financial acquirers, and the price is sensitive to how much of the business depends on you. Twelve to eighteen months of deliberate preparation typically moves the number further than going to market would today.',
    cta: 'Ask us what to work on first',
  };
}

const shell = (inner: string, preheader: string) => `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<title>Your indicative business valuation</title>
</head>
<body style="margin:0;padding:0;background:${PAPER};color:${INK};font-family:${FONT};-webkit-font-smoothing:antialiased;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">${esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${PAPER};">
<tr><td align="center" style="padding:24px 12px 40px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%;">
${inner}
</table>
</td></tr></table>
</body></html>`;

const row = (label: string, value: string) => `
<tr>
  <td style="padding:11px 0;border-bottom:1px solid ${LINE};font-size:14px;color:${INK3};">${esc(label)}</td>
  <td align="right" style="padding:11px 0;border-bottom:1px solid ${LINE};font-size:14px;color:${INK};font-weight:500;">${esc(value)}</td>
</tr>`;

const button = (href: string, text: string) => `
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
  <td style="border-radius:999px;background:${ACCENT};">
    <a href="${href}" style="display:inline-block;padding:14px 28px;font-family:${FONT};font-size:15px;font-weight:500;color:#ffffff;text-decoration:none;border-radius:999px;">${esc(text)}</a>
  </td>
</tr></table>`;

/** The report the owner receives. */
export function sellerReportHtml(d: ReportData): string {
  const step = nextSteps(d);
  const adj = adjustments(d);
  const sectorNote = d.evLow != null && d.evHigh != null && d.ebitda > 0;

  return shell(`
<tr><td style="padding:0 0 20px;">
  <span style="font-size:15px;font-weight:600;color:${INK};letter-spacing:-0.01em;">Singapore Business Broker</span>
  <span style="font-size:13px;color:${INK3};"> &middot; sell-side M&amp;A</span>
</td></tr>

<tr><td style="background:#ffffff;border-radius:20px;padding:36px 32px;">
  <p style="margin:0 0 18px;font-size:16px;color:${INK2};">Hello ${esc(d.name)},</p>
  <p style="margin:0 0 28px;font-size:16px;line-height:1.6;color:${INK2};">
    Here is the indicative range for your business, based on the figures you gave us.
  </p>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${ACCENT_SOFT};border-radius:16px;">
    <tr><td style="padding:28px 26px;">
      <p style="margin:0 0 10px;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:${ACCENT};">Indicative enterprise value</p>
      <p style="margin:0;font-family:${MONO};font-size:34px;line-height:1.15;font-weight:600;color:${INK};">${esc(d.range)}</p>
      ${sectorNote ? `<p style="margin:12px 0 0;font-size:13px;color:${INK3};">${esc(money(d.evLow!))} to ${esc(money(d.evHigh!))} on the figures below</p>` : ''}
    </td></tr>
  </table>

  <p style="margin:26px 0 8px;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:${INK3};">What we used</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    ${row('Sector', d.sector)}
    ${row('Annual revenue', revenueBand(d.revenue))}
    ${row('Profit, owner salary added back', money(d.ebitda))}
    ${row('Years operating', String(d.years))}
    ${row('Your shareholding', `${d.ownership}%`)}
    ${row('Owner dependency', dependencyLabel[d.dependency])}
    ${row('Timeline to sell', timelineLabel(d.timeline))}
  </table>

  <p style="margin:30px 0 10px;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:${INK3};">How the number was reached</p>
  <p style="margin:0 0 14px;font-size:15px;line-height:1.65;color:${INK2};">
    We take your profit with the owner salary added back, then apply the indicative multiple range for your
    sector, then adjust for the things buyers price separately.
  </p>
  ${adj.map((a) => `
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 10px;">
    <tr>
      <td width="8" valign="top" style="padding-top:8px;"><div style="width:5px;height:5px;border-radius:50%;background:${ACCENT};"></div></td>
      <td style="padding-left:12px;font-size:14px;line-height:1.6;color:${INK2};">${esc(a)}</td>
    </tr>
  </table>`).join('')}

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:26px 0 0;border-top:1px solid ${LINE};">
    <tr><td style="padding-top:26px;">
      <p style="margin:0 0 10px;font-size:18px;font-weight:600;color:${INK};">${esc(step.headline)}</p>
      <p style="margin:0 0 22px;font-size:15px;line-height:1.65;color:${INK2};">${esc(step.body)}</p>
      ${button(MAILTO, step.cta)}
    </td></tr>
  </table>
</td></tr>

<tr><td style="padding:16px 0 0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:20px;">
    <tr><td style="padding:28px 32px;">
      <p style="margin:0 0 14px;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:${INK3};">Worth reading next</p>
      <p style="margin:0 0 10px;font-size:15px;line-height:1.6;">
        <a href="${SITE}/exit-readiness" style="color:${ACCENT};text-decoration:none;font-weight:500;">The ten point readiness check</a>
        <span style="color:${INK3};"> &middot; scores what a buyer verifies before pricing, in three minutes</span>
      </p>
      <p style="margin:0 0 10px;font-size:15px;line-height:1.6;">
        <a href="${SITE}/guides/valuation-methods" style="color:${ACCENT};text-decoration:none;font-weight:500;">How SME valuations actually work</a>
        <span style="color:${INK3};"> &middot; why normalised earnings differ from reported profit</span>
      </p>
      <p style="margin:0;font-size:15px;line-height:1.6;">
        <a href="${SITE}/guides/preparing-to-sell" style="color:${ACCENT};text-decoration:none;font-weight:500;">Preparing your business for sale</a>
        <span style="color:${INK3};"> &middot; the work that moves the price, in order</span>
      </p>
    </td></tr>
  </table>
</td></tr>

<tr><td style="padding:26px 8px 0;">
  <p style="margin:0 0 14px;font-size:13px;line-height:1.6;color:${INK3};">
    <strong style="color:${INK2};">This is an estimate, not a valuation.</strong> It applies published sector
    multiple ranges to the figures you provided. It cannot see your contracts, customer concentration, lease
    position or management depth, and those are what decide where in the range a business actually lands. It is
    not financial advice and should not be relied on for a transaction.
  </p>
  <p style="margin:0 0 14px;font-size:13px;line-height:1.6;color:${INK3};">
    Singapore Business Broker is the sell-side M&amp;A practice of The Funding Assembly Pte Ltd, Singapore.
    You received this because you requested a valuation estimate at
    <a href="${SITE}/valuation" style="color:${INK3};">singaporebusinessbroker.com</a>.
    Reply with the word unsubscribe and we will remove you.
  </p>
  <p style="margin:0;font-size:13px;color:${INK3};">
    <a href="mailto:${CONTACT}" style="color:${INK3};">${CONTACT}</a> &middot;
    <a href="tel:+6589518821" style="color:${INK3};">+65 8951 8821</a>
  </p>
</td></tr>
`, `${d.range} indicative range for your ${d.sector} business`);
}

/** The alert the team receives on a hot lead. Scannable on a phone. */
export function teamAlertHtml(d: ReportData): string {
  const badge = { hot: '#b4451f', warm: '#8a6a1f', cold: INK3 }[d.score];
  const src = [d.utm_source, d.utm_medium, d.utm_campaign].filter(Boolean).join(' / ');

  return shell(`
<tr><td style="background:#ffffff;border-radius:20px;padding:30px 28px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td style="font-size:20px;font-weight:600;color:${INK};">${esc(d.name)}</td>
      <td align="right">
        <span style="display:inline-block;padding:5px 12px;border-radius:999px;background:${badge};color:#ffffff;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;font-weight:600;">${esc(d.score)}</span>
      </td>
    </tr>
  </table>

  <p style="margin:14px 0 0;font-size:15px;">
    <a href="mailto:${esc(d.email)}" style="color:${ACCENT};text-decoration:none;">${esc(d.email)}</a>
    <span style="color:${INK3};"> &middot; </span>
    <a href="tel:${esc(d.phone.replace(/[^0-9+]/g, ''))}" style="color:${ACCENT};text-decoration:none;">${esc(d.phone)}</a>
  </p>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${ACCENT_SOFT};border-radius:14px;margin:20px 0 4px;">
    <tr><td style="padding:20px 22px;">
      <p style="margin:0 0 6px;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:${ACCENT};">Indicative range</p>
      <p style="margin:0;font-family:${MONO};font-size:26px;font-weight:600;color:${INK};">${esc(d.range)}</p>
    </td></tr>
  </table>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:16px;">
    ${row('Sector', d.sector)}
    ${row('Revenue band', revenueBand(d.revenue))}
    ${row('Adjusted EBITDA', money(d.ebitda))}
    ${row('Years operating', String(d.years))}
    ${row('Shareholding', `${d.ownership}%`)}
    ${row('Owner dependency', dependencyLabel[d.dependency])}
    ${row('Timeline', timelineLabel(d.timeline))}
    ${row('Submitted from', d.page || '/valuation')}
    ${d.referrer ? row('Referrer', d.referrer) : ''}
    ${src ? row('Campaign', src) : ''}
  </table>

  <p style="margin:24px 0 0;font-size:13px;color:${INK3};">Reply to this email to answer ${esc(d.name)} directly.</p>
</td></tr>
`, `${d.score.toUpperCase()} lead: ${d.name}, ${d.sector}, ${d.range}`);
}

/** Plain-text alternative. Some clients prefer it, and spam filters expect it. */
export function sellerReportText(d: ReportData): string {
  const step = nextSteps(d);
  return [
    `Hello ${d.name},`,
    '',
    'Here is the indicative range for your business, based on the figures you gave us.',
    '',
    `INDICATIVE ENTERPRISE VALUE: ${d.range}`,
    '',
    'WHAT WE USED',
    `  Sector: ${d.sector}`,
    `  Annual revenue: ${revenueBand(d.revenue)}`,
    `  Profit, owner salary added back: ${money(d.ebitda)}`,
    `  Years operating: ${d.years}`,
    `  Your shareholding: ${d.ownership}%`,
    `  Owner dependency: ${dependencyLabel[d.dependency]}`,
    `  Timeline to sell: ${timelineLabel(d.timeline)}`,
    '',
    'HOW THE NUMBER WAS REACHED',
    ...adjustments(d).map((a) => `  - ${a}`),
    '',
    step.headline.toUpperCase(),
    step.body,
    '',
    `Reply to this email, or write to ${CONTACT}`,
    '',
    'READ NEXT',
    `  Ten point readiness check: ${SITE}/exit-readiness`,
    `  How SME valuations work: ${SITE}/guides/valuation-methods`,
    `  Preparing your business for sale: ${SITE}/guides/preparing-to-sell`,
    '',
    'This is an estimate, not a valuation. It applies published sector multiple',
    'ranges to the figures you provided. It cannot see your contracts, customer',
    'concentration, lease position or management depth, and those are what decide',
    'where in the range a business actually lands. It is not financial advice.',
    '',
    'Singapore Business Broker, the sell-side M&A practice of The Funding Assembly',
    `Pte Ltd, Singapore. ${CONTACT} | +65 8951 8821`,
    'Reply with the word unsubscribe and we will remove you.',
  ].join('\n');
}
