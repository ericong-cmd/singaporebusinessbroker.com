/**
 * Exit-readiness scoring.
 *
 * Ten questions, yes=10 / partly=5 / no=0, so the raw total is already the
 * 0-100 score. Deliberately not email-gated: the score is the hook, and asking
 * for an address before showing it is what makes a visitor close the tab. The
 * conversion ask sits after the result, once they have a reason to act.
 *
 * The questions render as ordinary radio groups, so without JavaScript the page
 * is still a readable checklist. Only the scoring needs this file.
 */
import { event } from './analytics';

export type Band = { min: number; label: string; summary: string; steps: string[] };

const VALUES: Record<string, number> = { yes: 10, partly: 5, no: 0 };

export function scoreOf(form: HTMLFormElement, total: number): number | null {
  const data = new FormData(form);
  let sum = 0;
  let answered = 0;
  for (const [, v] of data.entries()) {
    const val = VALUES[String(v)];
    if (val === undefined) continue;
    sum += val;
    answered += 1;
  }
  return answered === total ? sum : null;
}

export function bandFor(score: number, bands: Band[]): Band {
  // Bands are ordered high to low, so the first threshold met wins.
  return bands.find((b) => score >= b.min) ?? bands[bands.length - 1];
}

export function initQuiz(form: HTMLFormElement, bands: Band[], total: number): void {
  const $ = (id: string) => form.querySelector<HTMLElement>(`[data-q="${id}"]`)!;
  const result = document.querySelector<HTMLElement>('[data-q="result"]')!;
  const progress = $('progress');
  const count = $('count');
  // By id, not a data attribute: the button is rendered by <Button>, which
  // declares its props and would drop an undeclared data-* attribute.
  const submit = document.getElementById('exitsubmit')!;
  const incomplete = $('incomplete');

  const answeredCount = () => {
    const seen = new Set<string>();
    for (const [k] of new FormData(form).entries()) seen.add(k);
    return seen.size;
  };

  const refresh = () => {
    const n = answeredCount();
    count.textContent = `${n} / ${total}`;
    progress.style.width = `${(n / total) * 100}%`;
    if (n === total) incomplete.classList.add('hidden');
  };

  form.addEventListener('change', refresh);
  form.addEventListener('submit', (e) => e.preventDefault());

  submit.addEventListener('click', () => {
    const score = scoreOf(form, total);
    if (score === null) {
      incomplete.classList.remove('hidden');
      // Send focus to the first unanswered question rather than only colouring
      // an error: a keyboard user otherwise has to hunt for the gap.
      const answered = new Set<string>();
      for (const [k] of new FormData(form).entries()) answered.add(k);
      const first = [...form.querySelectorAll<HTMLFieldSetElement>('fieldset[data-name]')].find(
        (f) => !answered.has(f.dataset.name!)
      );
      first?.querySelector<HTMLInputElement>('input')?.focus();
      first?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      return;
    }

    const band = bandFor(score, bands);
    result.querySelector<HTMLElement>('[data-q="score"]')!.textContent = String(score);
    result.querySelector<HTMLElement>('[data-q="label"]')!.textContent = band.label;
    result.querySelector<HTMLElement>('[data-q="summary"]')!.textContent = band.summary;

    const list = result.querySelector<HTMLElement>('[data-q="steps"]')!;
    list.textContent = '';
    for (const step of band.steps) {
      const li = document.createElement('li');
      li.className = 'flex gap-3 text-ink-2 dark:text-[#a9b4c2] font-light';
      const dot = document.createElement('span');
      dot.className = 'mt-2 w-1.5 h-1.5 rounded-full bg-accent dark:bg-[#7fd1b3] shrink-0';
      dot.setAttribute('aria-hidden', 'true');
      const text = document.createElement('span');
      text.textContent = step;
      li.append(dot, text);
      list.append(li);
    }

    result.classList.remove('hidden');
    result.setAttribute('tabindex', '-1');
    result.focus();
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    result.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });

    event('quiz_completed', { score, band: band.label });
  });

  refresh();
}
