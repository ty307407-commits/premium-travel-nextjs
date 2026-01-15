import type { VercelRequest, VercelResponse } from '@vercel/node';
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

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { id } = req.query;

  if (!id || Array.isArray(id)) {
    return res.status(400).json({ error: 'page_id is required' });
  }

  const pageId = parseInt(id);
  if (isNaN(pageId)) {
    return res.status(400).json({ error: 'Invalid page_id' });
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
      return res.status(404).json({ error: 'Article not found', page_id: pageId });
    }

    return res.status(200).json(rows[0]);
  } catch (error) {
    console.error('Database error:', error);
    return res.status(500).json({ error: 'Database connection failed' });
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}
