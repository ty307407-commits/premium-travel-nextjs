#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB hotelsテーブル確認
"""

import mysql.connector

def check_hotels_table():
    """
    hotelsテーブルにuser_reviewがあるか確認
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
        
        # hotelsテーブルの構造
        print("="*60)
        print("\n=== hotels テーブルの構造 ===\n")
        cursor.execute("DESCRIBE hotels")
        columns = cursor.fetchall()
        
        has_user_review = False
        for col in columns:
            print(f"- {col['Field']}: {col['Type']}")
            if 'review' in col['Field'].lower():
                has_user_review = True
                print(f"  ⭐ 口コミ関連フィールド発見！")
        
        # サンプルデータ
        print("\n" + "="*60)
        print("\n=== サンプルデータ ===\n")
        
        cursor.execute("""
            SELECT *
            FROM hotels
            LIMIT 1
        """)
        
        sample = cursor.fetchone()
        
        if sample:
            print(f"\n--- 全フィールド ---\n")
            
            for key, value in sample.items():
                if value is None:
                    print(f"{key}: NULL")
                elif isinstance(value, (str, bytes)) and len(str(value)) > 300:
                    print(f"{key}: {str(value)[:300]}... (長さ: {len(str(value))})")
                else:
                    print(f"{key}: {value}")
        
        #レコード数確認
        print("\n" + "="*60)
        print("\n=== データ数 ===\n")
        cursor.execute("SELECT COUNT(*) as count FROM hotels")
        count = cursor.fetchone()
        print(f"総ホテル数: {count['count']}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print(f"\n✅ 完了 - user_review: {'あり' if has_user_review else 'なし'}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_hotels_table()
