import { NextRequest, NextResponse } from "next/server";
import mysql from "mysql2/promise";

// Force dynamic rendering - this endpoint must query the database at runtime
export const dynamic = "force-dynamic";

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

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const slug = searchParams.get("slug");

  if (!slug) {
    return NextResponse.json({ error: "slug is required" }, { status: 400 });
  }

  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    // page_dataテーブルからslugでpage_idを取得
    const [pageRows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT id, url_slug, theme_id
       FROM page_data
       WHERE url_slug = ?
       LIMIT 1`,
      [slug]
    );

    if (pageRows.length === 0) {
      return NextResponse.json(
        { error: "Page not found", slug },
        { status: 404 }
      );
    }

    const pageId = pageRows[0].id;

    // articlesテーブルから記事を取得
    const [articleRows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT a.id, a.page_id, a.status, a.title, a.content, a.meta_description, a.word_count, a.generated_at
       FROM articles a
       WHERE a.page_id = ?
       ORDER BY FIELD(a.status, 'draft', 'published'), a.generated_at DESC
       LIMIT 1`,
      [pageId]
    );

    if (articleRows.length === 0) {
      return NextResponse.json(
        { error: "Article not found", page_id: pageId, slug },
        { status: 404 }
      );
    }

    return NextResponse.json({
      ...articleRows[0],
      slug,
      page_info: pageRows[0],
    });
  } catch (error) {
    console.error("Database error:", error);
    return NextResponse.json(
      { error: "Database connection failed" },
      { status: 500 }
    );
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}
