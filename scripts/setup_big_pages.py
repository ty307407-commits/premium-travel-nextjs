#!/usr/bin/env python3
"""
BIGページ実装のためのデータベースセットアップスクリプト

1. page_dataテーブルに新カラムを追加
2. BH01（人気温泉地ランキング）のマスターレコードを挿入
"""
import os
import sys

# TiDB接続情報
TIDB_CONFIG = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test'
}

def execute_sql(sql, description=""):
    """SQLを実行（mysql.connectorがない場合はSQL文を出力）"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    print(f"\nSQL:\n{sql}\n")
    
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(**TIDB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(sql)
        conn.commit()
        
        print("✅ 実行成功")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        print("⚠️ mysql.connectorがインストールされていません")
        print("💡 上記のSQLを TiDB Cloud Console で直接実行してください")
        print("   https://tidbcloud.com/console/clusters")
        return False
    
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    return True


def main():
    print("""
╔════════════════════════════════════════════════════════╗
║  BIGページ実装 - データベースセットアップ               ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: 新カラム追加
    alter_table_sql = """
ALTER TABLE test.page_data 
ADD COLUMN IF NOT EXISTS page_level VARCHAR(10) DEFAULT 'LOW',
ADD COLUMN IF NOT EXISTS parent_page_id INT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS category_code VARCHAR(10) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS primary_kw VARCHAR(200) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS must_have_sections TEXT DEFAULT NULL;
    """.strip()
    
    execute_sql(alter_table_sql, "Step 1: page_dataテーブルに新カラムを追加")
    
    # Step 2: BH01のマスターレコード挿入
    insert_bh01_sql = """
INSERT INTO test.page_data (
  page_id,
  page_level,
  parent_page_id,
  category_code,
  primary_kw,
  url_slug,
  page_title,
  meta_description,
  must_have_sections,
  page_template,
  created_at,
  updated_at
) VALUES (
  9001,
  'BIG',
  NULL,
  'BH01',
  '温泉地 ランキング',
  '/onsen-ranking/',
  '人気温泉地ランキング2026【最新版】全国おすすめ温泉地TOP20',
  '日本全国の人気温泉地をランキング形式でご紹介。12,000軒以上の温泉旅館データと最新レビューから厳選したおすすめ温泉地TOP20。目的別・予算別の選び方も解説。',
  '["hero", "intro", "ranking", "guide", "category_links", "faq", "related_articles"]',
  'big_pillar_ranking',
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE
  page_level = 'BIG',
  category_code = 'BH01',
  primary_kw = '温泉地 ランキング',
  updated_at = NOW();
    """.strip()
    
    execute_sql(insert_bh01_sql, "Step 2: BH01（人気温泉地ランキング）のマスターレコードを挿入")
    
    # Step 3: 確認
    verify_sql = """
SELECT 
  page_id,
  page_level,
  category_code,
  primary_kw,
  url_slug,
  page_title
FROM test.page_data
WHERE page_level = 'BIG'
ORDER BY page_id;
    """.strip()
    
    print(f"\n{'='*60}")
    print("📋 Step 3: BIGページの確認")
    print(f"{'='*60}")
    print(f"\nSQL:\n{verify_sql}\n")
    
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(**TIDB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(verify_sql)
        results = cursor.fetchall()
        
        if results:
            print("✅ BIGページが正常に登録されました:\n")
            for row in results:
                print(f"  ID: {row['page_id']}")
                print(f"  レベル: {row['page_level']}")
                print(f"  カテゴリ: {row['category_code']}")
                print(f"  URL: {row['url_slug']}")
                print(f"  タイトル: {row['page_title']}")
                print()
        else:
            print("⚠️ BIGページが見つかりませんでした")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        print("💡 上記のSQLで確認してください")
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    print("""
╔════════════════════════════════════════════════════════╗
║  セットアップ完了                                      ║
║                                                        ║
║  次のステップ:                                         ║
║  1. Next.jsで /onsen-ranking/ ページを作成            ║
║  2. ランキングデータを生成するAPIを実装                ║
║  3. コンテンツをGeminiで生成                           ║
╚════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
