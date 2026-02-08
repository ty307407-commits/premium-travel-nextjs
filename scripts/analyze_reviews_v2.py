#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.0 Flash (New SDK) 口コミ分析スクリプト
"""

from google import genai
from google.genai import types
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector

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

def get_rakuten_review_content(url):
    """
    楽天の口コミページからコンテンツを取得
    """
    # URL変換
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
            for review in reviews[:15]:  # 最新15件
                text = review.get_text(strip=True)
                # 日付や投稿者情報もあれば含める
                extracted_text += f"- {text}\n\n"
                count += 1
        else:
            # フォールバック
            extracted_text = soup.get_text(strip=True)[:10000]
            count = -1
            
        return extracted_text, target_url, count

    except Exception as e:
        print(f"❌ HTML取得エラー: {e}")
        return None, target_url, 0

def analyze_hotel_reviews(hotel_id, hotel_name, review_url):
    """
    1旅館の口コミを分析
    """
    print(f"\n🚀 分析開始: {hotel_name} (ID: {hotel_id})")
    
    # 1. HTML取得
    content, final_url, count = get_rakuten_review_content(review_url)
    
    if not content:
        print("❌ 口コミ取得失敗")
        return None
        
    print(f"📄 口コミ取得成功: {count}件分 ({len(content)}文字)")
    
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
  "overall_summary": "300文字程度の魅力的な要約。プロのライターが書いたような文章で。",
  "positive_keywords": [
    {{"word": "絶景", "count": 10, "context": "露天風呂からの富士山が最高"}},
    {{"word": "食事", "count": 8, "context": "金目鯛の煮付けが絶品"}}
  ],
  "negative_keywords": [
    {{"word": "Wi-Fi", "count": 3, "context": "部屋で繋がりにくい", "severity": "中"}}
  ],
  "persona_match": {{
    "couple": {{"score": 90, "reason": "記念日プランの満足度が高い"}},
    "family": {{"score": 70, "reason": "子供向け設備は少ないが大人は満足"}}
  }},
  "trust_score": 85,
  "last_analyzed": "{datetime.now().strftime('%Y-%m-%d')}"
}}
"""
    
    try:
        # 新しいSDKでの呼び出し
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        result_json = response.text
        # JSONパース確認
        data = json.loads(result_json)
        
        print("✅ Gemini分析成功")
        return data
        
    except Exception as e:
        print(f"❌ Geminiエラー: {e}")
        return None

def test_run():
    # テスト対象: ホテル四季彩
    hotel_id = 30152
    hotel_name = "奥日光 ホテル四季彩"
    review_url = "https://img.travel.rakuten.co.jp/image/tr/api/hs/RmfmX/?f_hotel_no=13462"
    
    result = analyze_hotel_reviews(hotel_id, hotel_name, review_url)
    
    if result:
        print("\n=== 分析結果（プレビュー） ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # ここで本来はTiDBに保存
        save_to_tidb(hotel_id, result)

def save_to_tidb(hotel_id, data):
    try:
        conn = mysql.connector.connect(**TIDB_CONFIG)
        cursor = conn.cursor()
        
        # テーブルがなければ作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hotel_review_analysis_v2 (
                hotel_id INT PRIMARY KEY,
                analysis_json JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # 保存
        sql = """
            INSERT INTO hotel_review_analysis_v2 (hotel_id, analysis_json)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE analysis_json = VALUES(analysis_json)
        """
        cursor.execute(sql, (hotel_id, json.dumps(data, ensure_ascii=False)))
        conn.commit()
        
        print("💾 TiDB保存完了")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ DB保存エラー: {e}")

if __name__ == "__main__":
    test_run()
