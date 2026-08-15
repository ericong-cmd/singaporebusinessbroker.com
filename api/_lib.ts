/**
 * Shared helpers for the Vercel serverless endpoints.
 *
 * Every integration is optional and driven by environment variables. With none
 * set the endpoints still validate, score and log the lead, and return 200, so
 * the front end works on a fresh deployment. See .env.example.
 */

export type Json = Record<string, unknown>;

/**
 * Minimal shapes for Vercel's Node runtime handler arguments. Typed here
 * rather than pulling in @vercel/node, which would add a dependency for two
 * interfaces. The web-standard (Request) => Response signature is NOT used:
 * this runtime passes Node-style objects and a web handler fails at
 * invocation.
 */
export interface ApiRequest {
  method?: string;
  headers: Record<string, string | string[] | undefined>;
  body?: unknown;
}
export interface ApiResponse {
  status(code: number): ApiResponse;
  setHeader(name: string, value: string): void;
  json(body: unknown): void;
}

export function json(res: ApiResponse, body: Json, status = 200): void {
  res.setHeader('cache-control', 'no-store');
  res.status(status).json(body);
}

/** Vercel parses JSON bodies, but be tolerant of a raw string. */
export function readBody(req: ApiRequest): unknown {
  if (typeof req.body === 'string') {
    try {
      return JSON.parse(req.body);
    } catch {
      return undefined;
    }
  }
  return req.body;
}

/** Small fixed-window limiter. Per-instance only, so it blunts casual abuse
 *  rather than a distributed flood; put a WAF in front for anything more. */
const hits = new Map<string, { n: number; reset: number }>();
export function rateLimited(ip: string, limit = 8, windowMs = 60_000): boolean {
  const now = Date.now();
  const rec = hits.get(ip);
  if (!rec || now > rec.reset) {
    hits.set(ip, { n: 1, reset: now + windowMs });
    return false;
  }
  rec.n += 1;
  if (hits.size > 5000) hits.clear();
  return rec.n > limit;
}

export function clientIp(req: ApiRequest): string {
  const h = (name: string): string => {
    const v = req.headers[name];
    return Array.isArray(v) ? (v[0] ?? '') : (v ?? '');
  };
  return h('x-forwarded-for').split(',')[0]?.trim() || h('x-real-ip') || 'unknown';
}

export const esc = (s: unknown): string =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

/** Resend transactional email. No-op when RESEND_API_KEY is unset. */
export async function sendEmail(opts: {
  to: string | string[];
  subject: string;
  html: string;
  replyTo?: string;
}): Promise<'sent' | 'skipped' | 'failed'> {
  const key = process.env.RESEND_API_KEY;
  const from = process.env.MAIL_FROM;
  if (!key || !from) return 'skipped';
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: `Bearer ${key}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from,
        to: Array.isArray(opts.to) ? opts.to : [opts.to],
        subject: opts.subject,
        html: opts.html,
        ...(opts.replyTo ? { reply_to: opts.replyTo } : {}),
      }),
    });
    return res.ok ? 'sent' : 'failed';
  } catch {
    return 'failed';
  }
}

/** Slack incoming webhook alert. No-op when SLACK_WEBHOOK_URL is unset. */
export async function alertSlack(text: string): Promise<'sent' | 'skipped' | 'failed'> {
  const url = process.env.SLACK_WEBHOOK_URL;
  if (!url) return 'skipped';
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return res.ok ? 'sent' : 'failed';
  } catch {
    return 'failed';
  }
}

/**
 * Airtable upsert. No-op unless AIRTABLE_TOKEN and AIRTABLE_BASE_ID are set.
 * HubSpot can be swapped in here without touching the endpoints.
 */
export async function crmUpsert(table: string, fields: Json): Promise<'sent' | 'skipped' | 'failed'> {
  const token = process.env.AIRTABLE_TOKEN;
  const base = process.env.AIRTABLE_BASE_ID;
  if (!token || !base) return 'skipped';
  try {
    const res = await fetch(`https://api.airtable.com/v0/${base}/${encodeURIComponent(table)}`, {
      method: 'POST',
      headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
      body: JSON.stringify({ records: [{ fields }], typecast: true }),
    });
    return res.ok ? 'sent' : 'failed';
  } catch {
    return 'failed';
  }
}
