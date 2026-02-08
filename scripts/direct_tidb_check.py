#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDBデータ確認（直接接続）
"""

import mysql.connector

def check_tidb_data():
    """
    TiDBに接続してuser_reviewデータを確認
    """
    try:
        conn = mysql.connector.connect(
            host='gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
            port=4000,
            user='4VWXcjUowH2PPCE.root',
            password='6KcooGBdpDcmeIGI',
            database='test'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        print("✅ TiDB接続成功！\n")
        print("="*60)
        
        # 1. テーブル一覧
        print("\n=== テーブル一覧 ===\n")
        cursor.execute("SHOW TABLES")
        tables = [list(t.values())[0] for t in cursor.fetchall()]
        for table in tables:
            print(f"- {table}")
        
        # 2. page_dataのカラム
        print("\n" + "="*60)
        print("\n=== page_data のカラム ===\n")
        cursor.execute("DESCRIBE page_data")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col['Field']}: {col['Type']}")
        
        # 3. DETAILページのサンプル
        print("\n" + "="*60)
        print("\n=== DETAILページのサンプル ===\n")
        
        cursor.execute("""
            SELECT *
            FROM page_data
            WHERE page_type = 'DETAIL'
            LIMIT 1
        """)
        
        sample = cursor.fetchone()
        
        if sample:
            print(f"Page ID: {sample['page_id']}")
            print(f"Title: {sample['page_title']}")
            print(f"\n--- 全フィールド ---\n")
            
            for key, value in sample.items():
                if value is None:
                    print(f"{key}: NULL")
                elif isinstance(value, (str, bytes)) and len(str(value)) > 200:
                    print(f"{key}: {str(value)[:200]}... (長さ: {len(str(value))})")
                else:
                    print(f"{key}: {value}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("\n✅ 完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_tidb_data()
