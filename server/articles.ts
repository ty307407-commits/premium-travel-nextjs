/**
 * Articles API - TiDB から記事を取得
 */

import mysql from 'mysql2/promise';

// TiDB接続設定
const dbConfig = {
  host: process.env.TIDB_HOST || 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
  port: parseInt(process.env.TIDB_PORT || '4000'),
  user: process.env.TIDB_USER || '4VWXcjUowH2PPCE.root',
  password: process.env.TIDB_PASSWORD || '6KcooGBdpDcmeIGI',
  database: process.env.TIDB_DATABASE || 'test',
  ssl: {
    minVersion: 'TLSv1.2' as const,
    rejectUnauthorized: false
  }
};

export interface Article {
  id: number;
  page_id: number;
  status: 'draft' | 'published';
  title: string | null;
  content: string | null;
  meta_description: string | null;
  word_count: number | null;
  generated_at: string | null;
}

/**
 * ページIDから記事を取得（draftを優先）
 */
export async function getArticleByPageId(pageId: number): Promise<Article | null> {
  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    // まずdraftを探す、なければpublished
    const [rows] = await connection.execute<mysql.RowDataPacket[]>(
      `SELECT id, page_id, status, title, content, meta_description, word_count, generated_at
       FROM articles
       WHERE page_id = ?
       ORDER BY FIELD(status, 'draft', 'published'), generated_at DESC
       LIMIT 1`,
      [pageId]
    );

    if (rows.length === 0) {
      return null;
    }

    return rows[0] as Article;
  } catch (error) {
    console.error('Database error:', error);
    throw error;
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

/**
 * 記事一覧を取得
 */
export async function getArticleList(status?: 'draft' | 'published'): Promise<Article[]> {
  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);

    let query = `SELECT id, page_id, status, title, meta_description, word_count, generated_at
                 FROM articles`;
    const params: any[] = [];

    if (status) {
      query += ' WHERE status = ?';
      params.push(status);
    }

    query += ' ORDER BY generated_at DESC LIMIT 100';

    const [rows] = await connection.execute<mysql.RowDataPacket[]>(query, params);

    return rows as Article[];
  } catch (error) {
    console.error('Database error:', error);
    throw error;
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}
