/**
 * Turns the five stage panels into a tab interface.
 *
 * The markup ships with every panel visible and the tab strip hidden, so this
 * script only ever removes content that is already redundant. If it fails, the
 * page still reads correctly as sequential sections.
 *
 * Keyboard behaviour follows the ARIA tabs pattern: arrows move between tabs,
 * Home and End jump to the ends, and only the selected tab is in the tab order
 * so a keyboard user tabs into the strip once rather than five times.
 */
export function initTimeline(root: HTMLElement): void {
  const tablist = root.querySelector<HTMLElement>('[data-tl="tablist"]');
  const tabs = [...root.querySelectorAll<HTMLButtonElement>('[data-tl="tab"]')];
  const panels = [...root.querySelectorAll<HTMLElement>('[data-tl="panel"]')];
  if (!tablist || tabs.length === 0 || tabs.length !== panels.length) return;

  tablist.setAttribute('role', 'tablist');
  tablist.setAttribute('aria-label', 'Sale process stages');

  tabs.forEach((tab, i) => {
    const panel = panels[i];
    const id = `tl-tab-${i}`;
    const panelId = `tl-panel-${i}`;
    tab.id = id;
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panelId);
    panel.id = panelId;
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', id);
    panel.setAttribute('tabindex', '0');
  });

  const ACTIVE = ['bg-white/10', 'border-white/45'];

  function select(index: number, focus = false) {
    tabs.forEach((tab, i) => {
      const on = i === index;
      tab.setAttribute('aria-selected', String(on));
      tab.tabIndex = on ? 0 : -1;
      tab.classList.toggle(ACTIVE[0], on);
      tab.classList.toggle(ACTIVE[1], on);
      // hidden rather than a display class, so the panel is genuinely removed
      // from the accessibility tree instead of merely invisible.
      panels[i].hidden = !on;
    });
    if (focus) tabs[index].focus();
  }

  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(i));
    tab.addEventListener('keydown', (e) => {
      const keys: Record<string, number> = {
        ArrowRight: (i + 1) % tabs.length,
        ArrowLeft: (i - 1 + tabs.length) % tabs.length,
        Home: 0,
        End: tabs.length - 1,
      };
      const next = keys[e.key];
      if (next === undefined) return;
      e.preventDefault();
      select(next, true);
    });
  });

  select(0);
}
