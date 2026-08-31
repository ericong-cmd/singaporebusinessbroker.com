/**
 * Conversion events.
 *
 * The business measures success in enquiries, not sessions, so every event here
 * marks a step towards one: the visitor saw a number, asked for the report,
 * clicked to book, or opened their mail client. Page views alone cannot tell
 * those apart.
 *
 * `track` from @vercel/analytics queues events until the Web Analytics script
 * has loaded and drops them silently if it never does, so calling this is
 * always safe. Note that custom events are a paid Vercel feature: on the Hobby
 * plan the calls are accepted and the dashboard shows page views only. Nothing
 * breaks, the events simply do not appear until the plan is upgraded.
 */
import { track } from '@vercel/analytics';

export type ConversionEvent =
  | 'valuation_instant_result'
  | 'valuation_report_requested'
  | 'book_call_click'
  | 'email_enquiry_click'
  | 'quiz_completed';

type Props = Record<string, string | number | boolean | null>;

export function event(name: ConversionEvent, props?: Props): void {
  try {
    track(name, props);
  } catch {
    // Analytics must never take a page down with it.
  }
}

/**
 * One delegated listener for the whole site rather than a handler per link.
 * There are 60-odd mailto links across the pages and they are the primary
 * conversion, so binding individually would guarantee that a new one added
 * later goes uncounted.
 */
export function trackOutboundClicks(): void {
  document.addEventListener(
    'click',
    (e) => {
      const a = (e.target as HTMLElement | null)?.closest?.('a');
      if (!a) return;
      const href = a.getAttribute('href') ?? '';
      if (href.startsWith('mailto:')) {
        event('email_enquiry_click', {
          page: location.pathname,
          // The address only, never the prefilled subject or body.
          to: href.slice(7).split('?')[0],
        });
      } else if (href === '/book-a-call' || href.startsWith('/book-a-call')) {
        event('book_call_click', { page: location.pathname });
      } else if (href.startsWith('tel:')) {
        event('email_enquiry_click', { page: location.pathname, to: 'phone' });
      }
    },
    { capture: true, passive: true }
  );
}
