import { router, publicProcedure } from './trpc';
import { z } from 'zod';
import { getContentTemplates, getOnsenArea, getThemes } from './googlesheets';
import { searchHotels } from './rakuten';

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
});

// Export type definition of API
export type AppRouter = typeof appRouter;
