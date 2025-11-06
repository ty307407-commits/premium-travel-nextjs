import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";
import * as db from "./db";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Content management router
  content: router({
    // Save generated content
    save: publicProcedure
      .input(
        z.object({
          regionName: z.string(),
          themeName: z.string(),
          templateId: z.string(),
          templateName: z.string(),
          content: z.string(),
          wordCount: z.number(),
          hotelNo: z.number().optional(),
          hotelName: z.string().optional(),
        })
      )
      .mutation(async ({ input }) => {
        return await db.saveGeneratedContent(input);
      }),

    // Get generated content
    get: publicProcedure
      .input(
        z.object({
          regionName: z.string(),
          themeName: z.string(),
          templateId: z.string(),
          hotelNo: z.number().optional(),
        })
      )
      .query(async ({ input }) => {
        return await db.getGeneratedContent(
          input.regionName,
          input.themeName,
          input.templateId,
          input.hotelNo
        );
      }),

    // Get all contents for a page
    getAll: publicProcedure
      .input(
        z.object({
          regionName: z.string(),
          themeName: z.string(),
        })
      )
      .query(async ({ input }) => {
        return await db.getAllGeneratedContentsForPage(
          input.regionName,
          input.themeName
        );
      }),
  }),

  // Hotel management router
  hotel: router({
    // Save hotel
    save: publicProcedure
      .input(
        z.object({
          hotelNo: z.number(),
          hotelName: z.string(),
          regionName: z.string(),
          hotelImageUrl: z.string().optional(),
          hotelMinCharge: z.number().optional(),
          address1: z.string().optional(),
          address2: z.string().optional(),
          access: z.string().optional(),
          hotelInformationUrl: z.string().optional(),
          reviewAverage: z.number().optional(),
          reviewCount: z.number().optional(),
          hotelSpecial: z.string().optional(),
        })
      )
      .mutation(async ({ input }) => {
        return await db.saveHotel(input);
      }),

    // Get hotels by region
    getByRegion: publicProcedure
      .input(z.object({ regionName: z.string() }))
      .query(async ({ input }) => {
        return await db.getHotelsByRegion(input.regionName);
      }),
  }),
});

export type AppRouter = typeof appRouter;
