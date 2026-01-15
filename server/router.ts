import { router, publicProcedure } from './trpc';
import { z } from 'zod';
import { getContentTemplates, getOnsenArea, getThemes } from './googlesheets';
import { searchHotels } from './rakuten';
import { getArticleByPageId, getArticleList } from './articles';

export const appRouter = router({
  // Google Sheets procedures
  sheets: router({
    getContentTemplates: publicProcedure.query(async () => {
      return await getContentTemplates();
    }),

    getOnsenArea: publicProcedure
      .input(z.object({ regionName: z.string() }))
      .query(async ({ input }) => {
        return await getOnsenArea(input.regionName);
      }),

    getThemes: publicProcedure.query(async () => {
      return await getThemes();
    }),
  }),

  // Rakuten Travel API procedures
  rakuten: router({
    searchHotels: publicProcedure
      .input(z.object({
        regionName: z.string(),
        limit: z.number().optional().default(5),
      }))
      .query(async ({ input }) => {
        return await searchHotels(input.regionName, input.limit);
      }),
  }),

  // Articles API - TiDBから記事取得
  articles: router({
    getByPageId: publicProcedure
      .input(z.object({ pageId: z.number() }))
      .query(async ({ input }) => {
        return await getArticleByPageId(input.pageId);
      }),

    list: publicProcedure
      .input(z.object({
        status: z.enum(['draft', 'published']).optional()
      }).optional())
      .query(async ({ input }) => {
        return await getArticleList(input?.status);
      }),
  }),
});

// Export type definition of API
export type AppRouter = typeof appRouter;
