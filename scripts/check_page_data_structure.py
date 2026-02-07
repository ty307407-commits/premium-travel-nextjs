#!/usr/bin/env python3
"""
page_dataテーブルの構造を確認するスクリプト
"""
import mysql.connector
import json

# TiDB接続設定
config = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test',
    'ssl_verify_cert': False,
    'ssl_verify_identity': False
}

def check_table_structure():
    """page_dataテーブルの構造を確認"""
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    # テーブル構造を取得
    cursor.execute("DESCRIBE page_data")
    columns = cursor.fetchall()
    
    print("=== page_data テーブルの構造 ===\n")
    print(f"{'カラム名':<30} {'型':<20} {'NULL':<10} {'キー':<10} {'デフォルト':<15}")
    print("-" * 90)
    
    for col in columns:
        print(f"{col['Field']:<30} {col['Type']:<20} {col['Null']:<10} {col['Key']:<10} {str(col['Default']):<15}")
    
    print(f"\n総カラム数: {len(columns)}")
    
    # 新しいカラムの存在確認
    column_names = [col['Field'] for col in columns]
    new_columns = ['page_level', 'parent_page_id', 'category_code', 'primary_kw', 'must_have_sections']
    
    print("\n=== 新カラムの存在確認 ===")
    for new_col in new_columns:
        exists = new_col in column_names
        status = "✅ 存在" if exists else "❌ 未追加"
        print(f"{new_col:<30} {status}")
    
    # サンプルデータを1件取得
    cursor.execute("SELECT * FROM page_data LIMIT 1")
    sample = cursor.fetchone()
    
    print("\n=== サンプルデータ（1件目） ===")
    if sample:
        for key, value in sample.items():
            # 長いテキストは省略
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"{key}: {value}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_table_structure()
