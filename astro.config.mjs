import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export const SITE = 'https://www.singaporebusinessbroker.com';

export default defineConfig({
  site: SITE,
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [
    tailwind({ applyBaseStyles: false }),
    mdx(),
    sitemap({
      filter: (page) => !/\/(privacy|terms)\/?$/.test(page),
      changefreq: 'weekly',
    }),
  ],
  build: { inlineStylesheets: 'auto' },
  vite: {
    build: { assetsInlineLimit: 1024 },
  },
});
