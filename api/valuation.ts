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
  json, readBody, rateLimited, clientIp, sendEmail, alertSlack, crmUpsert,
  type ApiRequest, type ApiResponse,
} from './_lib.js';
import { sellerReportHtml, sellerReportText, teamAlertHtml, type ReportData } from './_report.js';

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

  // One object feeds both templates, so the seller's report and the team alert
  // can never describe the same lead differently.
  const report: ReportData = {
    name: lead.name,
    email: lead.email,
    phone: lead.phone,
    sector: lead.sector,
    revenue: lead.revenue,
    ebitda: lead.ebitda,
    years: lead.years,
    ownership: lead.ownership,
    dependency: lead.dependency,
    timeline: lead.timeline,
    evLow: lead.evLow,
    evHigh: lead.evHigh,
    range,
    score: band,
    page: lead.page,
    referrer: lead.referrer,
    utm_source: lead.utm_source,
    utm_medium: lead.utm_medium,
    utm_campaign: lead.utm_campaign,
  };

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
      subject: `Your indicative business valuation: ${range}`,
      replyTo: team,
      html: sellerReportHtml(report),
      text: sellerReportText(report),
    }),

    band === 'hot' && team
      ? sendEmail({
          to: team,
          subject: `Hot lead: ${lead.name}, ${lead.sector}, ${range}`,
          replyTo: lead.email,
          html: teamAlertHtml(report),
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
