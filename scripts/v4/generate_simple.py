#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル記事生成スクリプト
楽天APIから直接ホテルを取得し、DBテーブル依存なしで記事を生成

使用方法:
    python generate_simple.py --onsen "四万温泉" --page-id 4624
"""

import os
import sys
import json
import argparse
import base64
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# TiDB Data API設定
TIDB_API_BASE = "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint"
TIDB_API_PUBLIC_KEY = "S2R9M3V0"
TIDB_API_PRIVATE_KEY = "8cc2d2cd-7567-422a-a9d1-8a96b5643286"


def fetch_hotels_from_rakuten(keyword: str, hits: int = 20) -> List[Dict]:
    """
    楽天トラベルAPIからホテルを検索

    Args:
        keyword: 検索キーワード（温泉地名など）
        hits: 取得件数

    Returns:
        ホテルリスト
    """
    affiliate_id = os.getenv('RAKUTEN_AFFILIATE_ID', '')

    url = "https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426"
    params = {
        "applicationId": "1032556592498781289",  # 楽天アプリID
        "affiliateId": affiliate_id,
        "keyword": keyword,
        "hits": hits,
        "responseType": "large",
        "formatVersion": 2
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            hotels = []
            for item in data.get("hotels", []):
                hotel_info = item.get("hotel", [{}])[0].get("hotelBasicInfo", {})
                if hotel_info:
                    hotels.append({
                        "hotel_no": hotel_info.get("hotelNo"),
                        "hotel_name": hotel_info.get("hotelName", ""),
                        "hotel_special": hotel_info.get("hotelSpecial", ""),
                        "review_average": hotel_info.get("reviewAverage", 0),
                        "review_count": hotel_info.get("reviewCount", 0),
                        "hotel_image_url": hotel_info.get("hotelImageUrl", ""),
                        "address1": hotel_info.get("address1", ""),
                        "address2": hotel_info.get("address2", ""),
                        "access": hotel_info.get("access", ""),
                        "hotel_info_url": hotel_info.get("hotelInformationUrl", "")
                    })
            print(f"✅ 楽天APIから {len(hotels)} 件のホテルを取得")
            return hotels
        else:
            print(f"❌ 楽天API エラー: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 楽天API リクエスト失敗: {e}")
        return []


def generate_with_gemini(prompt: str) -> str:
    """
    Gemini APIで記事を生成

    Args:
        prompt: プロンプト

    Returns:
        生成されたテキスト
    """
    import google.generativeai as genai

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY が必要です")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 65536,
        }
    )

    print("🤖 Gemini APIで記事を生成中...")
    response = model.generate_content(prompt)
    print(f"✅ 生成完了: {len(response.text)} 文字")
    return response.text


def build_prompt(onsen_name: str, hotels: List[Dict]) -> str:
    """
    記事生成用プロンプトを構築

    Args:
        onsen_name: 温泉地名
        hotels: ホテルリスト

    Returns:
        プロンプト文字列
    """
    # ホテル情報をフォーマット
    hotel_info_text = ""
    for i, hotel in enumerate(hotels[:15], 1):  # 最大15件
        hotel_info_text += f"""
### 候補{i}: {hotel.get('hotel_name', '')}
- 評価: {hotel.get('review_average', 'N/A')} ({hotel.get('review_count', 0)}件)
- 特徴: {hotel.get('hotel_special', '')[:300]}...
- アクセス: {hotel.get('access', '')}
"""

    prompt = f"""あなたは温泉旅行の専門ライターです。
以下の条件で、{onsen_name}の温泉旅行記事を作成してください。

## 記事の要件

1. **ターゲット**: 50代夫婦（子育てを終え、経済的に余裕のある層）
2. **テーマ**: 露天風呂付き客室で過ごす贅沢な時間
3. **トーン**: 落ち着いた上品な文体、夫婦の絆を深める旅を提案
4. **文字数**: 15,000〜20,000文字程度の充実した内容

## 記事構成

1. **導入部** (800-1000文字)
   - {onsen_name}の魅力を情緒豊かに紹介
   - 50代夫婦がこの地を選ぶべき理由

2. **温泉地の魅力** (1500-2000文字)
   - 泉質と効能
   - 歴史と文化
   - 周辺の見どころ

3. **厳選宿の紹介** (各宿1500-2000文字 × 5-7軒)
   - 以下の候補から5-7軒を厳選
   - 各宿について詳細に紹介
   - [HOTEL_LINK:宿名] 形式でリンクプレースホルダーを入れる

4. **旅のモデルプラン** (1000-1500文字)
   - 1泊2日または2泊3日のプラン提案

5. **まとめ** (500-800文字)
   - 夫婦旅の価値を訴求

## 候補ホテル情報
{hotel_info_text}

## 出力形式

- Markdown形式で出力
- 見出しは ## と ### を使用
- 各宿の紹介では必ず [HOTEL_LINK:宿名] を含める

## 注意事項

- 実在する宿の情報のみを使用
- 架空の情報は絶対に書かない
- 料金は「お問い合わせください」程度に留める
- SEOを意識したキーワード配置

記事を生成してください。
"""
    return prompt


def save_to_tidb(page_id: int, content: str, title: str) -> bool:
    """
    TiDB Data APIに記事を保存

    Args:
        page_id: ページID
        content: 記事内容
        title: タイトル

    Returns:
        成功: True, 失敗: False
    """
    auth = base64.b64encode(
        f"{TIDB_API_PUBLIC_KEY}:{TIDB_API_PRIVATE_KEY}".encode()
    ).decode()

    url = f"{TIDB_API_BASE}/save_page_content"
    payload = {
        "page_id": page_id,
        "content": content
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            },
            timeout=60
        )

        if response.status_code == 200:
            print(f"✅ TiDBに保存完了: page_id={page_id}")
            return True
        else:
            print(f"❌ TiDB保存エラー: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ TiDB保存エラー: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='シンプル記事生成スクリプト')
    parser.add_argument('--onsen', type=str, required=True, help='温泉地名（例: 四万温泉）')
    parser.add_argument('--page-id', type=int, required=True, help='保存先ページID')
    parser.add_argument('--output-dir', type=str, default='./output', help='出力ディレクトリ')
    parser.add_argument('--no-save', action='store_true', help='TiDBに保存しない')

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"📝 {args.onsen} の記事生成を開始")
    print(f"{'='*60}")

    # Step 1: 楽天APIからホテル取得
    print("\n📊 Step 1: 楽天APIからホテル取得...")
    hotels = fetch_hotels_from_rakuten(args.onsen, hits=20)

    if not hotels:
        print("❌ ホテルが見つかりませんでした")
        sys.exit(1)

    # Step 2: プロンプト構築
    print("\n📝 Step 2: プロンプト構築...")
    prompt = build_prompt(args.onsen, hotels)
    print(f"✅ プロンプト: {len(prompt)} 文字")

    # Step 3: Gemini生成
    print("\n🤖 Step 3: Gemini APIで記事生成...")
    content = generate_with_gemini(prompt)

    # タイトル抽出
    import re
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else f"{args.onsen}の温泉旅行ガイド"

    # Step 4: ファイル出力
    print("\n📁 Step 4: ファイル出力...")
    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Markdown
    md_path = os.path.join(args.output_dir, f"{args.onsen}_{timestamp}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Markdown: {md_path}")

    # JSON
    json_path = os.path.join(args.output_dir, f"{args.onsen}_{timestamp}.json")
    result = {
        "page_id": args.page_id,
        "title": title,
        "onsen_name": args.onsen,
        "content": content,
        "hotels_count": len(hotels),
        "generated_at": datetime.now().isoformat()
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON: {json_path}")

    # Step 5: TiDB保存
    if not args.no_save:
        print("\n📤 Step 5: TiDBに保存...")
        if save_to_tidb(args.page_id, content, title):
            print(f"\n🔗 プレビューURL: https://premium-travel-japan.com/preview?id={args.page_id}")

    print(f"\n{'='*60}")
    print(f"✨ 記事生成完了!")
    print(f"   文字数: {len(content)} 文字")
    print(f"   タイトル: {title}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
