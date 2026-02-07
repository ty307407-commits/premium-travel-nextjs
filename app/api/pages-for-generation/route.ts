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
  const limit = parseInt(searchParams.get("limit") || "20");

  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    // 記事がまだないページ（url_slugがあるもの）を取得
    const [rows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT p.id as page_id, p.url_slug, p.page_title, p.area_name, p.theme_name
       FROM page_data p
       LEFT JOIN articles a ON a.page_id = p.id
       WHERE p.url_slug IS NOT NULL AND p.url_slug != ''
         AND a.id IS NULL
       ORDER BY p.id
       LIMIT ?`,
      [limit]
    );

    return NextResponse.json({
      count: rows.length,
      message: "Pages available for article generation (no article yet)",
      pages: rows,
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
