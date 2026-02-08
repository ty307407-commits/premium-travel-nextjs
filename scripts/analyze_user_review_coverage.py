#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user_reviewデータの詳細調査
"""

import mysql.connector

def analyze_user_review_coverage():
    """
    全ホテルのuser_reviewデータ量を確認
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
        
        # 1. user_reviewの状況確認
        print("\n=== user_review データ状況 ===\n")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_hotels,
                COUNT(CASE WHEN user_review IS NOT NULL AND user_review != '' THEN 1 END) as has_review,
                COUNT(CASE WHEN user_review IS NULL OR user_review = '' THEN 1 END) as no_review,
                AVG(LENGTH(user_review)) as avg_length,
                MIN(LENGTH(user_review)) as min_length,
                MAX(LENGTH(user_review)) as max_length
            FROM hotels
        """)
        
        stats = cursor.fetchone()
        
        print(f"総ホテル数: {stats['total_hotels']}")
        print(f"user_reviewあり: {stats['has_review']} ({stats['has_review']/stats['total_hotels']*100:.1f}%)")
        print(f"user_reviewなし: {stats['no_review']} ({stats['no_review']/stats['total_hotels']*100:.1f}%)")
        print(f"平均文字数: {stats['avg_length']:.0f}文字" if stats['avg_length'] else "平均文字数: 0文字")
        print(f"最小文字数: {stats['min_length']}文字" if stats['min_length'] else "最小文字数: 0文字")
        print(f"最大文字数: {stats['max_length']}文字" if stats['max_length'] else "最大文字数: 0文字")
        
        # 2. サンプル5件を詳しく見る
        print("\n" + "="*60)
        print("\n=== user_review サンプル（5件） ===\n")
        
        cursor.execute("""
            SELECT 
                hotel_name,
                review_count,
                LENGTH(user_review) as review_length,
                user_review
            FROM hotels
            WHERE user_review IS NOT NULL AND user_review != ''
            ORDER BY review_count DESC
            LIMIT 5
        """)
        
        samples = cursor.fetchall()
        
        for i, hotel in enumerate(samples, 1):
            print(f"\n--- {i}. {hotel['hotel_name']} ---")
            print(f"口コミ総数: {hotel['review_count']}件")
            print(f"user_reviewの長さ: {hotel['review_length']}文字")
            print(f"\nuser_review内容:")
            print(hotel['user_review'][:500] + "..." if len(hotel['user_review']) > 500 else hotel['user_review'])
            print()
        
        # 3. 口コミ数別の分布
        print("="*60)
        print("\n=== 口コミ数の分布 ===\n")
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN review_count = 0 THEN '0件'
                    WHEN review_count BETWEEN 1 AND 10 THEN '1-10件'
                    WHEN review_count BETWEEN 11 AND 50 THEN '11-50件'
                    WHEN review_count BETWEEN 51 AND 100 THEN '51-100件'
                    WHEN review_count BETWEEN 101 AND 500 THEN '101-500件'
                    WHEN review_count > 500 THEN '501件以上'
                END as range_group,
                COUNT(*) as hotel_count
            FROM hotels
            GROUP BY range_group
            ORDER BY MIN(review_count)
        """)
        
        distribution = cursor.fetchall()
        
        for row in distribution:
            print(f"{row['range_group']}: {row['hotel_count']}軒")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("\n✅ 完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_user_review_coverage()
