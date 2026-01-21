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
  const id = searchParams.get("id");

  if (!id) {
    return NextResponse.json({ error: "page_id is required" }, { status: 400 });
  }

  const pageId = parseInt(id);
  if (isNaN(pageId)) {
    return NextResponse.json({ error: "Invalid page_id" }, { status: 400 });
  }

  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    const [rows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT id, page_id, status, title, content, meta_description, word_count, generated_at
       FROM articles
       WHERE page_id = ?
       ORDER BY FIELD(status, 'draft', 'published'), generated_at DESC
       LIMIT 1`,
      [pageId]
    );

    if (rows.length === 0) {
      return NextResponse.json(
        { error: "Article not found", page_id: pageId },
        { status: 404 }
      );
    }

    return NextResponse.json(rows[0]);
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
