#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.0 FlashでURLから口コミ取得テスト（HTML取得版）
"""

import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup

# Gemini API設定
genai.configure(api_key='AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM')

def get_rakuten_review_content(hotel_id, url):
    """
    楽天の口コミページからコンテンツを取得
    """
    # URLの修正（imgサーバーの場合は標準URLに変換）
    if "img.travel.rakuten.co.jp" in url:
        # hotel_idがあればそれを使う（もしURLに含まれていれば抽出）
        import re
        match = re.search(r'hotel_no=(\d+)', url)
        if match:
            hotel_id = match.group(1)
        
        target_url = f"https://review.travel.rakuten.co.jp/hotel/voice/{hotel_id}/"
        print(f"🔄 URL変換: {url} -> {target_url}")
    else:
        target_url = url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML解析して本文のみ抽出（トークン節約 & ノイズ除去）
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 楽天トラベルの口コミ本文エリア（サイト構造に合わせて調整）
        reviews = soup.find_all('dl', class_='commentRep')
        
        extracted_text = ""
        if reviews:
            for review in reviews[:10]:  # 最大10件
                text = review.get_text(strip=True)
                extracted_text += f"- {text}\n\n"
        else:
            # 構造が変わっている場合のフォールバック（全体からテキスト抽出）
            extracted_text = soup.get_text(strip=True)[:10000]
            
        return extracted_text, target_url

    except Exception as e:
        print(f"❌ HTML取得エラー: {e}")
        return None, target_url

def test_gemini_url_reading():
    """
    GeminiがHTML解析できるかテスト
    """
    
    # テスト対象
    hotel_id = "13462"  # DBにあったID（ホテル四季彩）
    # DBにあるURL
    db_url = "https://img.travel.rakuten.co.jp/image/tr/api/hs/RmfmX/?f_hotel_no=13462"
    hotel_name = "奥日光 ホテル四季彩"
    
    print(f"🚀 Gemini テスト開始 (HTML取得 -> 分析)\n")
    
    # 1. HTML取得
    content, final_url = get_rakuten_review_content(hotel_id, db_url)
    
    if not content:
        print("❌ コンテンツ取得失敗")
        return False
        
    print(f"📄 コンテンツ取得成功（{len(content)}文字）")
    # print(f"内容プレビュー: {content[:200]}...")
    
    # 2. Gemini分析
    prompt = f"""
以下の楽天トラベルの口コミページの内容を分析してください：

旅館名: {hotel_name}
URL: {final_url}

【取得された口コミテキスト】
{content}

【タスク】
1. 最新の口コミから具体的な声を3件抽出
2. 高評価のポイント（キーワード）
3. 低評価のポイント（改善点）
4. どんな人におすすめか（カップル、家族など）

【出力形式】
JSON形式のみ
"""
    
    try:
        # 安定版モデルを指定
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        print("\n✅ 成功！Geminiの分析結果:\n")
        print(response.text)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Geminiエラー: {e}")
        return False


if __name__ == "__main__":
    test_gemini_url_reading()
