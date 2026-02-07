// TiDBからMarkdownコンテンツを取得してレンダリングするコンポーネント
import { notFound } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import type { Metadata } from 'next';

// TiDBからページデータを取得
async function getPageData(slug: string) {
    const apiUrl = `https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_by_slug?slug=${encodeURIComponent(slug)}`;

    const auth = Buffer.from('S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286').toString('base64');

    try {
        const response = await fetch(apiUrl, {
            headers: {
                'Authorization': `Basic ${auth}`,
            },
            next: { revalidate: 3600 }, // 1時間キャッシュ
        });

        if (!response.ok) {
            console.error('TiDB API Error:', response.status, response.statusText);
            return null;
        }

        const data = await response.json();

        if (!data.data || !data.data.rows || data.data.rows.length === 0) {
            return null;
        }

        return data.data.rows[0];
    } catch (error) {
        console.error('Failed to fetch page data:', error);
        return null;
    }
}

interface LegalPageProps {
    slug: string;
}

export async function generateMetadata({ slug }: LegalPageProps): Promise<Metadata> {
    const pageData = await getPageData(slug);

    if (!pageData) {
        return {
            title: 'ページが見つかりません | Premium Travel Japan',
        };
    }

    return {
        title: pageData.page_title || 'Premium Travel Japan',
        description: pageData.meta_description || '',
    };
}

export default async function LegalPage({ slug }: LegalPageProps) {
    const pageData = await getPageData(slug);

    if (!pageData || !pageData.temp_full_markdown) {
        notFound();
    }

    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
            <article className="max-w-4xl mx-auto px-4 py-16">
                {/* Markdownコンテンツをレンダリング */}
                <div className="prose prose-lg prose-indigo max-w-none">
                    <ReactMarkdown
                        components={{
                            // カスタムスタイリング
                            h1: ({ children }) => (
                                <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8 pb-4 border-b-2 border-indigo-200">
                                    {children}
                                </h1>
                            ),
                            h2: ({ children }) => (
                                <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mt-12 mb-6">
                                    {children}
                                </h2>
                            ),
                            h3: ({ children }) => (
                                <h3 className="text-xl md:text-2xl font-bold text-gray-700 mt-8 mb-4">
                                    {children}
                                </h3>
                            ),
                            p: ({ children }) => (
                                <p className="text-gray-700 leading-relaxed mb-6">
                                    {children}
                                </p>
                            ),
                            ul: ({ children }) => (
                                <ul className="list-disc pl-6 mb-6 space-y-2 text-gray-700">
                                    {children}
                                </ul>
                            ),
                            li: ({ children }) => (
                                <li className="leading-relaxed">
                                    {children}
                                </li>
                            ),
                            a: ({ href, children }) => (
                                <a
                                    href={href}
                                    className="text-indigo-600 hover:text-indigo-800 underline font-medium"
                                >
                                    {children}
                                </a>
                            ),
                            strong: ({ children }) => (
                                <strong className="font-bold text-gray-900">
                                    {children}
                                </strong>
                            ),
                            hr: () => (
                                <hr className="my-8 border-gray-200" />
                            ),
                        }}
                    >
                        {pageData.temp_full_markdown}
                    </ReactMarkdown>
                </div>

                {/* 最終更新日 */}
                {pageData.updated_at && (
                    <div className="mt-12 pt-6 border-t border-gray-200 text-sm text-gray-500 text-right">
                        最終更新: {new Date(pageData.updated_at).toLocaleDateString('ja-JP')}
                    </div>
                )}

                {/* 戻るボタン */}
                <div className="mt-8 text-center">
                    <a
                        href="/"
                        className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
                    >
                        トップページへ
                    </a>
                </div>
            </article>
        </main>
    );
}
