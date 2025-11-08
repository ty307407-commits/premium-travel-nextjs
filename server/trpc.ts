import { initTRPC } from '@trpc/server';
import superjson from 'superjson';

// tRPCインスタンスの初期化
const t = initTRPC.create({
  transformer: superjson,
});

// エクスポート
export const router = t.router;
export const publicProcedure = t.procedure;
