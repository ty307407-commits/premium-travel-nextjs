#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDBに保存された分析結果を確認
"""

import mysql.connector
import json

# DB設定
TIDB_CONFIG = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test'
}

def check_results():
    conn = mysql.connector.connect(**TIDB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # 最新10件を取得
    cursor.execute("""
        SELECT h.hotel_name, a.analysis_json, a.updated_at
        FROM hotel_review_analysis_v2 a
        JOIN hotels h ON a.hotel_id = h.hotel_no
        ORDER BY a.updated_at DESC
        LIMIT 3
    """)
    
    results = cursor.fetchall()
    
    print(f"\n✅ 最新の分析結果（{len(results)}件）\n")
    print("="*60)
    
    for r in results:
        data = json.loads(r['analysis_json'])
        print(f"\n🏨 {r['hotel_name']}")
        print(f"🕒 更新: {r['updated_at']}")
        
        print("\n[📊 レーダーチャートデータ]")
        print(f"Type: {type(data)}")
        if isinstance(data, list):
            print("Warning: Data is a list, taking first element")
            data = data[0]
            
        print(json.dumps(data.get('radar_chart_data', {}), indent=2))
        
        print("\n[📝 要約]")
        print(data.get('overall_summary', '')[:200] + "...")
        
        print("\n[👍 ポジティブキーワード]")
        for k in data.get('positive_keywords', [])[:3]:
            print(f"- {k.get('word')} ({k.get('count')}件): {k.get('context')}")
            
        print("\n" + "-"*40)
        
    conn.close()

if __name__ == "__main__":
    check_results()
