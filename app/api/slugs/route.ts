import { NextResponse } from "next/server";
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

export async function GET() {
  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    // 記事があるページのslug一覧を取得
    const [rows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT p.id as page_id, p.url_slug, p.page_title, a.title as article_title
       FROM page_data p
       INNER JOIN articles a ON a.page_id = p.id
       WHERE p.url_slug IS NOT NULL AND p.url_slug != ''
       ORDER BY p.id
       LIMIT 20`
    );

    return NextResponse.json({
      count: rows.length,
      slugs: rows,
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
