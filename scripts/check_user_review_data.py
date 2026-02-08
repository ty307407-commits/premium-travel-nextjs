#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user_reviewデータの確認
"""

import mysql.connector
import os
import json
from dotenv import load_dotenv

load_dotenv()

def check_user_review_data():
    """
    TiDBにuser_reviewデータがあるか確認
    """
    conn = mysql.connector.connect(
        host=os.getenv('TIDB_HOST'),
        user=os.getenv('TIDB_USER'),
        password=os.getenv('TIDB_PASSWORD'),
        database=os.getenv('TIDB_DATABASE'),
        port=4000,
        ssl_ca=os.getenv('TIDB_SSL_CA') if os.getenv('TIDB_SSL_CA') else None
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # まずテーブル一覧
    print("=== TiDBのテーブル一覧 ===\n")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {list(table.values())[0]}")
    
    print("\n" + "="*60 + "\n")
    
    # page_dataのカラム確認
    print("=== page_dataのカラム ===\n")
    cursor.execute("DESCRIBE page_data")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col['Field']}: {col['Type']}")
    
    print("\n" + "="*60 + "\n")
    
    # サンプルデータ取得
    print("=== page_dataのサンプル（DETAIL） ===\n")
    cursor.execute("""
        SELECT 
            page_id,
            page_title,
            page_type
        FROM page_data
        WHERE page_type = 'DETAIL'
        LIMIT 1
    """)
    
    sample = cursor.fetchone()
    if sample:
        print(f"Page ID: {sample['page_id']}")
        print(f"Title: {sample['page_title']}")
        
        # すべてのカラムを取得
        cursor.execute(f"""
            SELECT *
            FROM page_data
            WHERE page_id = {sample['page_id']}
        """)
        
        full_data = cursor.fetchone()
        
        print("\n=== 全カラムの内容 ===\n")
        for key, value in full_data.items():
            if value and len(str(value)) > 100:
                print(f"{key}: {str(value)[:100]}... (長さ: {len(str(value))})")
            else:
                print(f"{key}: {value}")
            
            # user_reviewを探す
            if key.lower() == 'user_review' or 'review' in key.lower():
                print(f"\n🎯 発見！ {key}:")
                print(f"内容プレビュー: {str(value)[:500]}")
    
    cursor.close()
    conn.close()


if __name__ == "__main__":
    check_user_review_data()
