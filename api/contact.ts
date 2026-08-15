/**
 * POST /api/contact
 * Validates a contact enquiry, records it in the CRM and notifies the team.
 */
import { z } from 'zod';
// .js extension required: Vercel compiles functions with moduleResolution nodenext
import {
  json, readBody, rateLimited, clientIp, esc, sendEmail, alertSlack, crmUpsert,
  type ApiRequest, type ApiResponse,
} from './_lib.js';

const Body = z.object({
  enquiry: z.enum(['seller', 'buyer', 'adviser', 'other']),
  name: z.string().min(1).max(120),
  email: z.string().email().max(200),
  phone: z.string().max(40).optional().default(''),
  message: z.string().min(1).max(4000),
  consent: z.literal(true),
  page: z.string().max(200).optional(),
});

export default async function handler(req: ApiRequest, res: ApiResponse): Promise<void> {
  if (req.method !== 'POST') return json(res, { error: 'method_not_allowed' }, 405);
  if (rateLimited(clientIp(req))) return json(res, { error: 'rate_limited' }, 429);

  let body: z.infer<typeof Body>;
  try {
    body = Body.parse(readBody(req));
  } catch {
    return json(res, { error: 'invalid_request' }, 400);
  }

  const team = process.env.TEAM_EMAIL;

  const results = await Promise.allSettled([
    crmUpsert(process.env.AIRTABLE_TABLE ?? 'Leads', {
      Name: body.name,
      Email: body.email,
      Phone: body.phone,
      Score: 'enquiry',
      Source: `contact:${body.enquiry}`,
      Notes: body.message,
      Page: body.page ?? '',
    }),
    team
      ? sendEmail({
          to: team,
          subject: `Enquiry (${body.enquiry}): ${body.name}`,
          replyTo: body.email,
          html: `<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif">
            <p><strong>${esc(body.name)}</strong> &lt;${esc(body.email)}&gt; ${esc(body.phone)}</p>
            <p>Type: ${esc(body.enquiry)}</p>
            <p style="white-space:pre-wrap">${esc(body.message)}</p>
          </div>`,
        })
      : Promise.resolve('skipped' as const),
    alertSlack(`:incoming_envelope: ${body.enquiry} enquiry from *${body.name}* (${body.email})`),
  ]);

  const [crm, mail, slack] = results.map((r) => (r.status === 'fulfilled' ? r.value : 'failed'));
  if ([crm, mail, slack].includes('failed')) {
    console.error('contact delivery partial failure', { crm, mail, slack, email: body.email });
  }
  return json(res, { ok: true, delivery: { crm, mail, slack } });
}
