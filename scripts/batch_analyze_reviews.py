#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.0 Flash (New SDK) 口コミ分析スクリプト - バッチ処理版
全旅館の口コミを並列で取得・分析し、TiDBに保存します。
"""

from google import genai
from google.genai import types
import sys
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

# DB設定
TIDB_CONFIG = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test'
}

# Gemini API設定
API_KEY = "AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
client = genai.Client(api_key=API_KEY)

# 並列数（Gemini 2.0 Flashのレート制限を考慮）
MAX_WORKERS = 10

# スレッドローカルなDB接続（並列処理用）
thread_local = threading.local()

def get_db_connection():
    if not hasattr(thread_local, "connection"):
        thread_local.connection = mysql.connector.connect(**TIDB_CONFIG)
    return thread_local.connection

def get_rakuten_review_content(url):
    """
    楽天の口コミページからコンテンツを取得
    """
    # URL変換 (img.travel... -> review.travel...)
    target_url = url
    if "img.travel.rakuten.co.jp" in url:
        import re
        match = re.search(r'hotel_no=(\d+)', url)
        if match:
            target_url = f"https://review.travel.rakuten.co.jp/hotel/voice/{match.group(1)}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 口コミ本文抽出
        reviews = soup.find_all('dl', class_='commentRep')
        
        extracted_text = ""
        count = 0
        if reviews:
            # 最新20件を取得（分析精度向上のため少し多めに）
            for review in reviews[:20]:
                text = review.get_text(strip=True)
                extracted_text += f"- {text}\n\n"
                count += 1
        else:
            # フォールバック: 全文から抽出（ノイズが多いが何もないよりマシ）
            extracted_text = soup.get_text(strip=True)[:10000]
            count = -1  # 構造化抽出失敗のマーク
            
        return extracted_text, target_url, count

    except Exception as e:
        # print(f"❌ HTML取得エラー: {e}") # ログが汚れるのでコメントアウト
        return None, target_url, 0

def analyze_single_hotel(hotel):
    """
    1旅館の処理（HTML取得 -> 分析 -> DB保存）
    """
    hotel_id = hotel['hotel_no']
    hotel_name = hotel['hotel_name']
    review_url = hotel['review_url']
    
    if not review_url:
        return {"status": "skipped", "reason": "no_url", "id": hotel_id}

    # 1. HTML取得
    content, final_url, count = get_rakuten_review_content(review_url)
    
    if not content or len(content) < 100:
        return {"status": "skipped", "reason": "no_content", "id": hotel_id}
        
    # 2. Gemini 2.0 Flash 分析
    prompt = f"""
あなたはプロのトラベルライター兼データアナリストです。
以下の楽天トラベルの口コミ（最新のもの）を深く分析し、
宿泊検討者が「知りたいこと」を客観的かつ魅力的にまとめてください。

【基本情報】
旅館名: {hotel_name}
ソースURL: {final_url}

【口コミデータ】
{content}

【分析タスク】
以下のJSONフォーマットで出力してください。
全ての項目を埋めてください。

{{
  "overall_summary": "300文字程度の魅力的な要約。プロのライターが書いたような文章で。旅館の特徴、雰囲気、独自の魅力を凝縮してください。",
  "positive_keywords": [
    {{"word": "絶景", "count": 10, "context": "露天風呂からの富士山が最高"}},
    {{"word": "食事", "count": 8, "context": "金目鯛の煮付けが絶品"}}
  ],
  "negative_keywords": [
    {{"word": "Wi-Fi", "count": 3, "context": "部屋で繋がりにくい", "severity": "中"}}
  ],
  "radar_chart_data": {{
     "atmosphere": 4.5,
     "cleanliness": 4.2,
     "onsen_quality": 4.8,
     "meals": 4.6,
     "hospitality": 4.7
  }},
  "persona_match": {{
    "couple": {{"score": 90, "reason": "記念日プランの満足度が高い"}},
    "family": {{"score": 70, "reason": "子供向け設備は少ないが大人は満足"}},
    "solo": {{"score": 80, "reason": "一人でも気兼ねなく過ごせる"}}
  }},
  "trust_score": 85,
  "last_analyzed": "{datetime.now().strftime('%Y-%m-%d')}"
}}
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        result_json = response.text
        data = json.loads(result_json)
        
        # 3. DB保存
        save_to_tidb(hotel_id, data)
        
        return {"status": "success", "id": hotel_id, "name": hotel_name}
        
    except Exception as e:
        return {"status": "error", "reason": str(e), "id": hotel_id}

def save_to_tidb(hotel_id, data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # テーブル作成（存在しない場合）
        # thread safeにするため、ここではCREATE TABLEしないほうが良いが、
        # 念のためIF NOT EXISTSで。本番では事前に作成推奨。
        
        sql = """
            INSERT INTO hotel_review_analysis_v2 (hotel_id, analysis_json)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE analysis_json = VALUES(analysis_json)
        """
        cursor.execute(sql, (hotel_id, json.dumps(data, ensure_ascii=False)))
        conn.commit()
        cursor.close() # コネクションは閉じずに使い回す（ThreadLocal）
        
    except Exception as e:
        print(f"❌ DB保存エラー({hotel_id}): {e}")

def setup_database():
    """
    テーブルを事前に作成
    """
    conn = mysql.connector.connect(**TIDB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel_review_analysis_v2 (
            hotel_id INT PRIMARY KEY,
            analysis_json JSON,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ データベース初期化完了")

def fetch_all_hotels():
    conn = mysql.connector.connect(**TIDB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    # user_reviewがある、またはreview_urlがあるホテルを取得
    # review_countが一定以上のものを優先しても良い
    query = """
        SELECT hotel_no, hotel_name, review_url, onsen_id
        FROM hotels 
        WHERE review_url IS NOT NULL AND review_url != ''
        AND onsen_id IS NOT NULL
        ORDER BY review_count DESC
    """
    cursor.execute(query)
    hotels = cursor.fetchall()
    conn.close()
    print(f"✅ 分析対象ホテル数: {len(hotels)}件")
    return hotels

def main():
    setup_database()
    hotels = fetch_all_hotels()
    
    # 既に分析済みのホテルを確認してスキップするロジックを入れるとベターだが、
    # 今回は上書き更新も考慮して全件実行（またはLIMITをつける）
    
    print(f"🚀 並列処理開始 (Workers: {MAX_WORKERS})")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # tqdmでプログレスバー表示
        futures = {executor.submit(analyze_single_hotel, hotel): hotel for hotel in hotels}
        
        for future in tqdm(as_completed(futures), total=len(hotels)):
            result = future.result()
            if result['status'] == 'success':
                success_count += 1
            elif result['status'] == 'skipped':
                skipped_count += 1
            else:
                error_count += 1
                # エラー詳細が見たければここでprint
                # print(f"Error ({result['id']}): {result['reason']}")

    print("\n=== 完了 ===")
    print(f"成功: {success_count}")
    print(f"スキップ: {skipped_count}")
    print(f"エラー: {error_count}")

if __name__ == "__main__":
    main()
