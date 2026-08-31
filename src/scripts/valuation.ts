/**
 * Valuation estimator. Logic matches CLAUDE.md and the approved prototype:
 *   EV        = normalised EBITDA x sector multiple range
 *   adjust    = dependency high -15%, low +5%; years < 3 -10%
 *               revenue < S$1m caps the upper multiple at 40% of the range
 *   lead score  hot  = revenue >= S$3m AND profit > 0
 *                      AND timeline <= 18 months AND ownership >= 50%
 *               warm = revenue S$1m to S$3m, or timeline > 18 months
 *               cold = revenue < S$1m
 */
import { event } from './analytics';
import multiples from '../data/multiples.json';

type Band = { low: number; high: number };
const RANGES: Record<string, Band> = Object.fromEntries(
  multiples.sectors.map((s) => [s.name, { low: s.low, high: s.high }])
);

export type Lead = {
  sector: string;
  revenue: number;
  ebitda: number;
  years: number;
  ownership: number;
  dependency: 'low' | 'med' | 'high';
  timeline: number;
  name: string;
  phone: string;
  email: string;
};

export type Estimate = {
  evLow: number;
  evHigh: number;
  multipleLow: number;
  multipleHigh: number;
  score: 'hot' | 'warm' | 'cold';
  valuable: boolean;
};

export function estimate(lead: Omit<Lead, 'name' | 'phone' | 'email'>): Estimate {
  const band = RANGES[lead.sector] ?? { low: 3, high: 5 };
  const ebitda = Math.max(0, lead.ebitda);

  let adj = 1;
  if (lead.dependency === 'high') adj -= 0.15;
  if (lead.dependency === 'low') adj += 0.05;
  if (lead.years < 3) adj -= 0.1;

  let mLow = band.low;
  let mHigh = band.high;
  if (lead.revenue < 1) mHigh = band.low + (band.high - band.low) * 0.4;

  const score: Estimate['score'] =
    lead.revenue >= 3 && ebitda > 0 && lead.timeline > 0 && lead.timeline <= 18 && lead.ownership >= 50
      ? 'hot'
      : lead.revenue >= 1
        ? 'warm'
        : 'cold';

  return {
    evLow: ebitda * mLow * adj,
    evHigh: ebitda * mHigh * adj,
    multipleLow: mLow,
    multipleHigh: mHigh,
    score,
    valuable: ebitda > 0,
  };
}

export function formatSGD(v: number): string {
  return v >= 1e6 ? `S$${(v / 1e6).toFixed(1)}m` : `S$${Math.round(v / 1e3)}k`;
}

/** Captured on submit so the CRM can attribute the lead to a campaign. */
export function utmParams(): Record<string, string> {
  const out: Record<string, string> = {};
  const q = new URLSearchParams(location.search);
  for (const k of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid']) {
    const v = q.get(k);
    if (v) out[k] = v;
  }
  if (document.referrer && !document.referrer.includes(location.host)) out.referrer = document.referrer;
  return out;
}

type Track = (event: string, props?: Record<string, unknown>) => void;
const track: Track = (event, props) => {
  const w = window as unknown as { plausible?: Track; dataLayer?: unknown[] };
  w.plausible?.(event, props ? ({ props } as never) : undefined);
  w.dataLayer?.push({ event, ...props });
};

export function initValuation(root: HTMLFormElement) {
  const TOTAL = 3;
  let step = 1;
  let started = false;

  const $ = <T extends HTMLElement>(id: string) => root.querySelector<T>(`[data-v="${id}"]`)!;
  const steps = [...root.querySelectorAll<HTMLFieldSetElement>('fieldset[data-step]')];
  const labels: Record<number, string> = {
    1: 'Step 1 of 3: Your business',
    2: 'Step 2 of 3: Ownership and timing',
    3: 'Step 3 of 3: Where to send your report',
  };

  const sectorSelect = root.querySelector<HTMLSelectElement>('#sector');
  // Pre-select the sector when arriving from a /sell/[sector] page.
  const preset = new URLSearchParams(location.search).get('sector');
  if (preset && sectorSelect) {
    const match = multiples.sectors.find((s) => s.slug === preset);
    if (match) sectorSelect.value = match.name;
  }

  function show(n: number) {
    steps.forEach((f) => {
      const on = Number(f.dataset.step) === n;
      f.classList.toggle('hidden', !on);
      f.classList.toggle('grid', on);
      f.querySelectorAll<HTMLInputElement>('input,select').forEach((el) => (el.tabIndex = on ? 0 : -1));
    });
    $('progress').style.width = `${(n / TOTAL) * 100}%`;
    $('stepLabel').textContent = labels[n];
    $('stepCount').textContent = `${n} / ${TOTAL}`;
    $('back').classList.toggle('invisible', n === 1);
    $('nextLabel').textContent = n === TOTAL ? 'Show my valuation' : 'Continue';
  }

  function validate(n: number) {
    const fs = steps[n - 1];
    let ok = true;
    const invalid: HTMLElement[] = [];
    fs.querySelectorAll<HTMLInputElement | HTMLSelectElement>('[required]').forEach((el) => {
      const input = el as HTMLInputElement;
      const bad =
        input.type === 'checkbox'
          ? !input.checked
          : !input.value ||
            (input.type === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(input.value)) ||
            (input.type === 'tel' && input.value.replace(/\D/g, '').length < 8);
      el.classList.toggle('ring-2', bad);
      el.classList.toggle('ring-red-500', bad);
      el.setAttribute('aria-invalid', String(bad));
      const err = el.closest('.grid')?.querySelector('.err');
      if (err) err.classList.toggle('hidden', !bad);
      if (bad) {
        ok = false;
        invalid.push(el);
      }
    });
    invalid[0]?.focus();
    return ok;
  }

  async function submit() {
    const data = Object.fromEntries(new FormData(root).entries()) as Record<string, string>;
    const lead = {
      sector: data.sector,
      revenue: Number(data.revenue),
      ebitda: Number(data.ebitda),
      years: Number(data.years),
      ownership: Number(data.ownership),
      dependency: (data.dependency ?? 'med') as Lead['dependency'],
      timeline: Number(data.timeline),
    };
    const est = estimate(lead);

    steps.forEach((f) => f.classList.add('hidden'));
    $('navbtns').classList.add('hidden');
    $('progress').style.width = '100%';
    $('stepLabel').textContent = 'Your estimate';
    $('stepCount').textContent = '';

    const result = $('result');
    result.classList.remove('hidden');

    $('basis').textContent = est.valuable
      ? `Based on ${est.multipleLow.toFixed(1)}x to ${est.multipleHigh.toFixed(1)}x normalised earnings for ${lead.sector.toLowerCase()}, adjusted for owner dependency and track record. Full report sent to ${data.email}.`
      : 'Loss-making or breakeven businesses are valued on assets, contracts or strategic fit rather than earnings. An advisor will review and email you a view.';

    const rangeEl = $('range');
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (est.valuable && !reduce) {
      const t0 = performance.now();
      const dur = 1100;
      const tick = (now: number) => {
        const p = Math.min(1, (now - t0) / dur);
        const e = 1 - Math.pow(1 - p, 3);
        rangeEl.textContent = `${formatSGD(est.evLow * e)} to ${formatSGD(est.evHigh * e)}`;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    } else {
      rangeEl.textContent = est.valuable ? `${formatSGD(est.evLow)} to ${formatSGD(est.evHigh)}` : 'Needs a closer look';
    }

    $('hot').classList.toggle('hidden', est.score !== 'hot');
    $('warm').classList.toggle('hidden', est.score === 'hot');

    track('valuation_complete', { sector: lead.sector, score: est.score });
    result.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });

    // Fired here rather than after the fetch: the visitor has the number on
    // screen at this point, which is the outcome worth counting. Whether the
    // report email then goes out is a separate event.
    event('valuation_instant_result', {
      sector: lead.sector,
      score: est.score,
      page: location.pathname,
    });

    // The estimate is already on screen; delivery of the report is the only
    // thing that depends on the network, so a failure here is reported quietly
    // rather than blocking the result the visitor came for.
    try {
      const res = await fetch('/api/valuation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...lead,
          name: data.name,
          phone: data.phone,
          email: data.email,
          consent: data.consent === 'on',
          evLow: Math.round(est.evLow),
          evHigh: Math.round(est.evHigh),
          score: est.score,
          page: location.pathname,
          ...utmParams(),
        }),
      });
      if (!res.ok) throw new Error(String(res.status));
      event('valuation_report_requested', {
        sector: lead.sector,
        score: est.score,
        page: location.pathname,
      });
    } catch {
      $('sendfail').classList.remove('hidden');
    }
  }

  $('next').addEventListener('click', () => {
    if (!validate(step)) return;
    if (step < TOTAL) {
      step += 1;
      show(step);
      track('valuation_step', { step });
    } else {
      void submit();
    }
  });

  $('back').addEventListener('click', () => {
    if (step > 1) {
      step -= 1;
      show(step);
    }
  });

  root.addEventListener('input', () => {
    if (started) return;
    started = true;
    track('valuation_start');
  });

  root.addEventListener('submit', (e) => e.preventDefault());
  show(1);
}
