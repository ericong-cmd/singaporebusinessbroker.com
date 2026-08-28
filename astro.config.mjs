import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import LASTMOD from './src/data/lastmod.json' assert { type: 'json' };

const EXCLUDE = /\/(privacy|terms|data\/sme-multiples-singapore)\/?$/;

export const SITE = 'https://www.singaporebusinessbroker.com';

export default defineConfig({
  site: SITE,
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [
    tailwind({ applyBaseStyles: false }),
    mdx(),
    sitemap({
      // privacy/terms are noindex; the multiples page is noindex until the real
      // dataset ships (see src/pages/data/sme-multiples-singapore.astro).
      filter: (page) => !EXCLUDE.test(page),
      serialize: (item) => {
        // Canonical form has no trailing slash, so the sitemap must match it
        // character for character.
        const url = item.url.replace(/(?<!^https?:\/)\/$/, '');
        const path = new URL(url).pathname.replace(/\/$/, '') || '/';
        return { url, lastmod: LASTMOD[path] ?? LASTMOD['/'] };
      },
    }),
  ],
  build: { inlineStylesheets: 'auto' },
  vite: {
    build: { assetsInlineLimit: 1024 },
  },
});
