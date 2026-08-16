/**
 * POST /api/valuation
 *
 * Validates a valuation submission, re-scores it server side (never trusting
 * the client's score), pushes it to the CRM, emails the report to the owner,
 * and alerts the team when the lead is hot.
 *
 * Runs on the Vercel Node runtime alongside the static Astro build, using the
 * Node-style (req, res) signature rather than a web handler.
 */
import { z } from 'zod';
// .js extension required: Vercel compiles functions with moduleResolution nodenext
import {
  json, readBody, rateLimited, clientIp, esc, sendEmail, alertSlack, crmUpsert,
  type ApiRequest, type ApiResponse,
} from './_lib.js';

const Body = z.object({
  sector: z.string().min(2).max(120),
  revenue: z.number().nonnegative().max(1000),
  ebitda: z.number().min(-1e9).max(1e9),
  years: z.number().int().min(0).max(120),
  ownership: z.number().min(0).max(100),
  dependency: z.enum(['low', 'med', 'high']),
  timeline: z.number().min(0).max(120),
  name: z.string().min(1).max(120),
  phone: z.string().min(6).max(40),
  email: z.string().email().max(200),
  consent: z.literal(true),
  evLow: z.number().nonnegative().optional(),
  evHigh: z.number().nonnegative().optional(),
  page: z.string().max(200).optional(),
  utm_source: z.string().max(120).optional(),
  utm_medium: z.string().max(120).optional(),
  utm_campaign: z.string().max(160).optional(),
  utm_term: z.string().max(160).optional(),
  utm_content: z.string().max(160).optional(),
  gclid: z.string().max(200).optional(),
  referrer: z.string().max(400).optional(),
});

function score(b: z.infer<typeof Body>): 'hot' | 'warm' | 'cold' {
  if (b.revenue >= 3 && b.ebitda > 0 && b.timeline > 0 && b.timeline <= 18 && b.ownership >= 50) return 'hot';
  return b.revenue >= 1 ? 'warm' : 'cold';
}

const sgd = (v: number) => (v >= 1e6 ? `S$${(v / 1e6).toFixed(1)}m` : `S$${Math.round(v / 1e3)}k`);

export default async function handler(req: ApiRequest, res: ApiResponse): Promise<void> {
  if (req.method !== 'POST') return json(res, { error: 'method_not_allowed' }, 405);
  if (rateLimited(clientIp(req))) return json(res, { error: 'rate_limited' }, 429);

  let parsed: z.infer<typeof Body>;
  try {
    parsed = Body.parse(readBody(req));
  } catch {
    return json(res, { error: 'invalid_request' }, 400);
  }

  const lead = parsed;
  const band = score(lead);
  const range =
    lead.evLow != null && lead.evHigh != null && lead.ebitda > 0
      ? `${sgd(lead.evLow)} to ${sgd(lead.evHigh)}`
      : 'Needs a closer look';

  const team = process.env.TEAM_EMAIL;

  const results = await Promise.allSettled([
    crmUpsert(process.env.AIRTABLE_TABLE ?? 'Leads', {
      Name: lead.name,
      Email: lead.email,
      Phone: lead.phone,
      Sector: lead.sector,
      'Revenue band (S$m)': lead.revenue,
      'Adjusted EBITDA': lead.ebitda,
      'Years operating': lead.years,
      'Ownership %': lead.ownership,
      'Owner dependency': lead.dependency,
      'Timeline (months)': lead.timeline,
      'EV low': lead.evLow ?? null,
      'EV high': lead.evHigh ?? null,
      Score: band,
      Source: 'valuation',
      Page: lead.page ?? '',
      'UTM source': lead.utm_source ?? '',
      'UTM medium': lead.utm_medium ?? '',
      'UTM campaign': lead.utm_campaign ?? '',
      Referrer: lead.referrer ?? '',
    }),

    sendEmail({
      to: lead.email,
      subject: 'Your indicative business valuation',
      replyTo: team,
      html: `
        <div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:560px;color:#0e1a2b">
          <p>Hello ${esc(lead.name)},</p>
          <p>Thank you for using the estimator. Here is the indicative range for your business.</p>
          <p style="font-size:24px;margin:24px 0"><strong>${esc(range)}</strong></p>
          <p style="font-size:14px;color:#5b687a">
            Sector: ${esc(lead.sector)}<br>
            Years operating: ${esc(lead.years)}<br>
            Owner dependency: ${esc(lead.dependency)}
          </p>
          <p>
            This is an indicative range based on sector transaction multiples applied to the figures you gave us. It is
            not a valuation: it cannot see your contracts, customer concentration or management depth, which are what
            actually decide where in the range a business lands.
          </p>
          <p>This report was sent to you automatically. If you would like an advisor to look at your figures properly, just reply to this email.</p>
          <p style="font-size:12px;color:#5b687a;margin-top:32px">
            Singapore Business Broker, a brand of The Funding Assembly Pte Ltd. You received this because you requested
            a valuation estimate. Reply with "unsubscribe" to be removed.
          </p>
        </div>`,
    }),

    band === 'hot' && team
      ? sendEmail({
          to: team,
          subject: `Hot lead: ${lead.name}, ${lead.sector}, ${range}`,
          replyTo: lead.email,
          html: `<pre style="font-family:ui-monospace,monospace;font-size:13px">${esc(
            JSON.stringify({ ...lead, score: band, range }, null, 2)
          )}</pre>`,
        })
      : Promise.resolve('skipped' as const),

    band === 'hot'
      ? alertSlack(
          `:fire: Hot valuation lead\n*${lead.name}* (${lead.email}, ${lead.phone})\n${lead.sector}, revenue band S$${lead.revenue}m, timeline ${lead.timeline}mo\nRange: ${range}`
        )
      : Promise.resolve('skipped' as const),
  ]);

  // Never fail the request because an integration is down: the visitor already
  // has their number, and losing the lead entirely would be the worse outcome.
  const [crm, ownerMail, teamMail, slack] = results.map((r) =>
    r.status === 'fulfilled' ? r.value : 'failed'
  );
  if ([crm, ownerMail, teamMail, slack].includes('failed')) {
    console.error('valuation delivery partial failure', { crm, ownerMail, teamMail, slack, email: lead.email });
  }

  return json(res, { ok: true, score: band, delivery: { crm, ownerMail, teamMail, slack } });
}
