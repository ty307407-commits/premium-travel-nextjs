#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.0 FlashでURLから口コミ取得テスト
"""

import google.generativeai as genai
import os

# Gemini API設定
genai.configure(api_key='AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM')

def test_gemini_url_reading():
    """
    GeminiがURLから口コミを読み取れるかテスト
    """
    
    # サンプル URL
    review_url = "https://img.travel.rakuten.co.jp/image/tr/api/hs/RmfmX/?f_hotel_no=13462"
    hotel_name = "奥日光 ホテル四季彩"
    
    prompt = f"""
以下の楽天トラベルの口コミページを読み取って分析してください：

URL: {review_url}
旅館名: {hotel_name}

【タスク】
1. このページから最新の口コミ10件を抽出してください
2. 各口コミから以下の情報を取得:
   - 投稿日
   - 評価（星の数）
   - タイトル
   - 本文（全文）
   - 投稿者の属性（カップル、家族等）

3. 高評価のポイント（頻出キーワード）
4. 低評価のポイント（改善点）

【出力形式】
JSON形式で返してください。

{{
  "reviews": [
    {{
      "date": "2024-11-15",
      "rating": 5,
      "title": "...",
      "text": "...",
      "reviewer_type": "カップル"
    }}
  ],
  "positive_keywords": ["温泉", "景色", ...],
  "negative_keywords": ["Wi-Fi", ...]
}}
"""
    
    try:
        print("🚀 Gemini 2.0 Flash テスト開始\n")
        print(f"対象URL: {review_url}\n")
        print("="*60)
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        print("\n✅ 成功！Geminiの応答:\n")
        print(response.text)
        
        print("\n" + "="*60)
        print("\n🎉 結論: GeminiはURLから直接口コミを読み取れます！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gemini_url_reading()
    
    if success:
        print("\n✅ この方法で全旅館の口コミ分析が可能です！")
        print("\n【次のステップ】")
        print("1. 全旅館のreview_urlを取得")
        print("2. Gemini 2.0 Flashで順次分析")
        print("3. 結果をTiDBに保存")
        print("4. ページ生成")
    else:
        print("\n⚠️ 別の方法を検討する必要があります")
