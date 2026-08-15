/** Tokens ported verbatim from prototype/tailwind.config.js in the handoff. */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  darkMode: 'media',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        ink: { DEFAULT: '#0e1a2b', 2: '#2b3a4f', 3: '#5b687a' },
        paper: { DEFAULT: '#f6f7f4', 2: '#eef0ec' },
        line: '#dfe3dc',
        accent: { DEFAULT: '#0f6b4f', 2: '#0c5740', soft: '#e3f1ea' },
        // Dark-mode surfaces, lifted from the prototype's .dk-* helper classes
        // so they can be expressed as Tailwind `dark:` variants instead.
        night: { DEFAULT: '#0b121c', 2: '#111a27', core: '#121c2a', soft: '#12261f' },
      },
      maxWidth: { wrap: '1280px' },
      boxShadow: {
        soft: '0 24px 60px -30px rgba(14,26,43,0.25)',
        frame: '0 40px 80px -40px rgba(14,26,43,0.35)',
        pill: '0 8px 40px -12px rgba(14,26,43,0.18)',
        bezel: 'inset 0 1px 1px rgba(255,255,255,0.6)',
        bezelSoft: 'inset 0 1px 1px rgba(255,255,255,0.4)',
      },
      transitionTimingFunction: { ease: 'cubic-bezier(0.32,0.72,0,1)' },
      borderRadius: { core: 'calc(2rem - 0.375rem)', 'core-lg': 'calc(2rem - 0.5rem)' },
    },
  },
  plugins: [],
};
