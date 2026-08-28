import { defineCollection, z } from 'astro:content';

const sectors = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    /** Must match a slug in src/data/multiples.json so the page can pull its range. */
    sector: z.string(),
    description: z.string(),
    heading: z.string(),
    intro: z.string(),
    whySell: z.array(z.string()).min(2),
    buyers: z.array(z.object({ type: z.string(), wants: z.string() })).min(2),
    drivers: z.array(z.string()).min(2),
    pitfalls: z.array(z.string()).min(2),
    draft: z.boolean().default(false),
    reviewed: z.boolean().default(false),
    updated: z.coerce.date(),
  }),
});

const guides = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    heading: z.string(),
    order: z.number().default(99),
    readingMinutes: z.number().default(6),
    draft: z.boolean().default(false),
    reviewed: z.boolean().default(false),
    updated: z.coerce.date(),
  }),
});

const cases = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    sectorLabel: z.string(),
    revenue: z.string(),
    outcome: z.string(),
    timeToClose: z.string(),
    buyerType: z.string(),
    /** Year the transaction completed. Always shown, so a closed deal can never
     *  be mistaken for a live mandate. */
    completedYear: z.number().int(),
    /** Our capacity on the deal. Stated plainly because advisor and principal
     *  are not the same claim. */
    role: z.string().default('Sell-side advisor'),
    featured: z.boolean().default(false),
    image: z.string().optional(),
    /** Illustrative rather than a real transaction. Real deals set this false. */
    sample: z.boolean().default(false),
    order: z.number().default(99),
    updated: z.coerce.date(),
  }),
});

const insights = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    heading: z.string(),
    published: z.coerce.date(),
    updated: z.coerce.date().optional(),
    draft: z.boolean().default(false),
    reviewed: z.boolean().default(false),
    readingMinutes: z.number().default(5),
  }),
});

export const collections = { sectors, guides, cases, insights };
