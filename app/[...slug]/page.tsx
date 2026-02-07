import { Metadata } from "next";
import { notFound } from "next/navigation";
import mysql from "mysql2/promise";
import ArticleContent from "./ArticleContent";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

// Force dynamic rendering - this page must query the database at runtime
export const dynamic = "force-dynamic";

// 記事データの型定義
interface ArticleData {
  id: number;
  page_id: number;
  status: string;
  title: string;
  content: string;
  meta_description: string;
  word_count: number;
  generated_at: Date;
  hero_image_url?: string;
}

// TiDB接続設定
const dbConfig = {
  host:
    process.env.TIDB_HOST || "gateway01.ap-northeast-1.prod.aws.tidbcloud.com",
  port: parseInt(process.env.TIDB_PORT || "4000"),
  user: process.env.TIDB_USER || "4VWXcjUowH2PPCE.root",
  password: process.env.TIDB_PASSWORD || "6KcooGBdpDcmeIGI",
  database: process.env.TIDB_DATABASE || "test",
  ssl: {
    minVersion: "TLSv1.2" as const,
    rejectUnauthorized: false,
  },
};

// 記事データを取得する関数
async function getArticleBySlug(slug: string): Promise<ArticleData | null> {
  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    // slugからpage_idを取得
    const [pageRows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT id as page_id, url_slug, hero_image_url
       FROM page_data
       WHERE url_slug LIKE ?`,
      [`%${slug}%`]
    );

    if (pageRows.length === 0) {
      return null;
    }

    // スラッシュを正規化して比較
    const pageInfo = pageRows.find((row) => {
      const normalizedDbSlug = row.url_slug.replace(/^\/|\/$/g, "");
      return normalizedDbSlug === slug;
    });

    if (!pageInfo) {
      return null;
    }

    // 記事を取得
    const [articleRows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT id, page_id, status, title, content, meta_description, word_count, generated_at
       FROM articles
       WHERE page_id = ?
       ORDER BY FIELD(status, 'draft', 'published'), generated_at DESC
       LIMIT 1`,
      [pageInfo.page_id]
    );

    if (articleRows.length === 0) {
      return null;
    }

    return {
      id: articleRows[0].id,
      page_id: articleRows[0].page_id,
      status: articleRows[0].status,
      title: articleRows[0].title,
      content: articleRows[0].content,
      meta_description: articleRows[0].meta_description,
      word_count: articleRows[0].word_count,
      generated_at: articleRows[0].generated_at,
      hero_image_url: pageInfo.hero_image_url,
    } as ArticleData;
  } catch (error) {
    console.error("Database error:", error);
    return null;
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

// SEOメタデータを動的に生成
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<Metadata> {
  const resolvedParams = await params;
  const fullSlug = resolvedParams.slug?.join("/") || "";

  // 法的ページは専用ルートで処理
  const legalPages = ['company', 'privacy', 'about', 'contact'];
  if (legalPages.includes(fullSlug)) {
    return {
      title: "ページが見つかりません | プレミアムトラベル",
    };
  }

  const article = await getArticleBySlug(fullSlug);

  if (!article) {
    return {
      title: "ページが見つかりません | プレミアムトラベル",
    };
  }

  const baseUrl = "https://www.premium-travel-japan.com";

  return {
    title: article.title || "プレミアムトラベル",
    description:
      article.meta_description ||
      "高級温泉旅館の厳選ガイド。露天風呂付き客室で特別な時間を。",
    openGraph: {
      title: article.title,
      description: article.meta_description,
      url: `${baseUrl}/${fullSlug}`,
      siteName: "プレミアムトラベル",
      images: article.hero_image_url
        ? [
          {
            url: article.hero_image_url,
            width: 1200,
            height: 630,
            alt: article.title,
          },
        ]
        : [],
      locale: "ja_JP",
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title: article.title,
      description: article.meta_description,
      images: article.hero_image_url ? [article.hero_image_url] : [],
    },
  };
}

// ページコンポーネント
export default async function ArticlePage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const resolvedParams = await params;
  const fullSlug = resolvedParams.slug?.join("/") || "";

  // 法的ページは専用ルートで処理されるため、ここでは404を返す
  const legalPages = ['company', 'privacy', 'about', 'contact'];
  if (legalPages.includes(fullSlug)) {
    notFound();
  }

  const article = await getArticleBySlug(fullSlug);

  // 記事が見つからない場合
  if (!article) {
    return (
      <main className="min-h-screen bg-white flex flex-col items-center justify-center p-8">
        <div className="bg-red-50 text-red-600 p-6 rounded-lg mb-6 max-w-md w-full text-center">
          <p className="font-medium mb-2">エラー</p>
          <p>ページが見つかりません</p>
          <p className="text-sm mt-2 text-gray-500">URL: /{fullSlug}</p>
        </div>
        <Link href="/">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            ホームに戻る
          </Button>
        </Link>
      </main>
    );
  }

  return <ArticleContent content={article.content || ""} slug={fullSlug} />;
}
