import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // 法的ページと特別なページは専用ルートで処理
    const specialPages = ['/company', '/privacy', '/about', '/contact'];

    // パスがspecialPagesに完全一致する場合は、そのまま通す
    if (specialPages.includes(pathname)) {
        return NextResponse.next();
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         * - icon.svg (icon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico|icon.svg).*)',
    ],
};
