#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 記事生成スクリプト（TiDB Data API版）
直接MySQL接続ではなくHTTP APIを使用
"""

import os
import json
import base64
import requests
from typing import Dict, List, Optional

# TiDB Data API設定
TIDB_API_BASE = "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint"
TIDB_AUTH = base64.b64encode(b'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286').decode()

# 楽天API設定
RAKUTEN_APP_ID = "1029472204308393704"
RAKUTEN_AFFILIATE_ID = "12426598.beaffa49.12426599.e0b47e86"


def fetch_tidb(endpoint: str, params: dict = None) -> List[Dict]:
    """TiDB Data APIからデータを取得"""
    url = f"{TIDB_API_BASE}/{endpoint}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    response = requests.get(
        url,
        headers={"Authorization": f"Basic {TIDB_AUTH}"},
        timeout=60
    )
    data = response.json()
    return data.get('data', {}).get('rows', [])


def fetch_rakuten_hotels(area_code: str, prefecture_code: str, limit: int = 10) -> List[Dict]:
    """楽天APIからホテル情報を取得"""
    url = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426"
    params = {
        'applicationId': RAKUTEN_APP_ID,
        'affiliateId': RAKUTEN_AFFILIATE_ID,
        'format': 'json',
        'largeClassCode': 'japan',
        'middleClassCode': prefecture_code,
        'smallClassCode': area_code,
        'hits': limit,
        'responseType': 'large',
        'formatVersion': '2'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        hotels = []
        for item in data.get('hotels', []):
            h = item[0].get('hotelBasicInfo', {})
            hotels.append({
                'hotel_no': h.get('hotelNo'),
                'hotel_name': h.get('hotelName'),
                'hotel_special': h.get('hotelSpecial', ''),
                'review_average': h.get('reviewAverage'),
                'review_count': h.get('reviewCount'),
                'hotel_image_url': h.get('hotelImageUrl'),
                'room_image_url': h.get('roomImageUrl'),
                'address1': h.get('address1'),
                'address2': h.get('address2'),
                'access': h.get('access'),
                'hotel_information_url': h.get('hotelInformationUrl')
            })
        return hotels
    except Exception as e:
        print(f"楽天API エラー: {e}")
        return []


def fetch_reviews_from_web(hotel_no: str, max_reviews: int = 5) -> List[Dict]:
    """楽天トラベルWebページからレビューを取得"""
    url = f"https://travel.rakuten.co.jp/HOTEL/{hotel_no}/review.html"

    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # JSONデータを探す
        import re
        pattern = r'<script[^>]*type="application/json"[^>]*>([^<]+)</script>'
        matches = re.findall(pattern, response.text)

        for match in matches:
            try:
                data = json.loads(match)
                if 'reviewList' in str(data):
                    # レビューデータを探す
                    def find_reviews(obj, reviews=[]):
                        if isinstance(obj, dict):
                            if 'reviewList' in obj:
                                contents = obj['reviewList'].get('data', {}).get('contents', [])
                                for c in contents:
                                    if c.get('overAllEvaluation', 0) >= 4:
                                        reviews.append({
                                            'text': c.get('comment', '')[:300],
                                            'date': c.get('postDateTime', '')[:7],
                                            'score': c.get('overAllEvaluation')
                                        })
                                        if len(reviews) >= max_reviews:
                                            return reviews
                            for v in obj.values():
                                find_reviews(v, reviews)
                        elif isinstance(obj, list):
                            for item in obj:
                                find_reviews(item, reviews)
                        return reviews

                    reviews = find_reviews(data, [])
                    if reviews:
                        return reviews
            except:
                continue

        return []
    except Exception as e:
        print(f"レビュー取得エラー ({hotel_no}): {e}")
        return []


def generate_article_content(
    page_data: Dict,
    theme_data: Dict,
    hotels: List[Dict],
    gemini_api_key: str
) -> str:
    """Gemini REST APIで記事を生成"""

    # ホテル情報をJSON形式で準備
    hotels_json = json.dumps([{
        'name': h['hotel_name'],
        'special': h['hotel_special'][:200] if h['hotel_special'] else '',
        'review_average': h['review_average'],
        'review_count': h['review_count'],
        'access': h['access']
    } for h in hotels[:10]], ensure_ascii=False, indent=2)

    # プロンプト
    prompt = f'''
あなたは天才的なトラベルマーケターであり、卓越したコピーライターです。

【記事の基本情報】
- 温泉地名: {page_data.get('region_name', '')}
- テーマ: {theme_data.get('theme_title', '')}
- ターゲット: 50代夫婦

【タイトルフォーマット】
# 【{page_data.get('region_name', '')}】キャッチーなフレーズ｜50代夫婦におすすめの露天風呂付き客室

【候補ホテル】
{hotels_json}

【記事構成】
1. タイトル（# 見出し1）
2. 導入文（## 見出し2）- なぜこの温泉地がターゲットに響くか
3. この温泉地の魅力（箇条書き）
4. 各ホテルの紹介（5〜10軒、各ホテル2000文字以上）
   - ## ホテル名
   - #### キャッチコピー
   - おすすめポイント（箇条書き）
   - サービス・おもてなし
   - ふたりで紡ぐ、宿の記憶（物語形式、夫婦の会話を含む）
   - こんな方におすすめ
5. まとめ

【出力形式】
Markdown形式で出力してください。
プレースホルダー:
- [HOTEL_IMAGE:ホテル名] - ホテル画像
- [CTA_BUTTON:ホテル名] - 予約ボタン

【重要】
- 選定したホテル全てについて詳細な記事を書くこと
- 「ふたりで紡ぐ、宿の記憶」は情緒的で詩的な表現を使うこと
- 会話文（「」）を効果的に使うこと
'''

    print("Gemini REST APIで記事生成中...")

    # Gemini REST API呼び出し
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 65536
        }
    }

    response = requests.post(url, json=payload, timeout=300)

    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        print(response.text)
        return ""

    data = response.json()

    # レスポンスからテキストを抽出
    try:
        return data['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        print(f"レスポンス解析エラー: {e}")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
        return ""


def process_article(content: str, hotels: List[Dict]) -> str:
    """記事の後処理（プレースホルダー置換）"""

    for hotel in hotels:
        name = hotel['hotel_name']

        # 画像プレースホルダー置換
        if hotel.get('hotel_image_url'):
            img_tag = f'![{name}]({hotel["hotel_image_url"]})\n*出典：楽天トラベル*'
            content = content.replace(f'[HOTEL_IMAGE:{name}]', img_tag)

        # CTAボタン置換
        affiliate_url = f"https://hb.afl.rakuten.co.jp/hgc/{RAKUTEN_AFFILIATE_ID}/?pc=https://travel.rakuten.co.jp/HOTEL/{hotel['hotel_no']}/"
        cta_html = f'\n<a href="{affiliate_url}" target="_blank" class="cta-button">【楽天トラベル】{name}の空室を見る ➜</a>\n'
        content = content.replace(f'[CTA_BUTTON:{name}]', cta_html)

    return content


def save_to_tidb(page_id: str, content: str, title: str) -> bool:
    """TiDB Data APIで記事を保存"""
    # 注: page_by_slugエンドポイントはGETのみなので、
    # 保存用のエンドポイントを作成する必要があります
    # 今は生成結果をファイルに保存します

    output_file = f'/home/user/premium-travel-nextjs/generated/page_{page_id}_v4.md'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 保存: {output_file}")
    return True


def main():
    """メイン処理"""
    import sys

    # Gemini APIキー
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY が設定されていません")
        sys.exit(1)

    print("=" * 60)
    print("V4 記事生成（Data API版）")
    print("=" * 60)

    # 3ページをランダム取得
    print("\n📊 ページデータ取得中...")
    pages = fetch_tidb('random_pages', {'limit_count': '3'})

    if not pages:
        print("❌ ページデータの取得に失敗しました")
        sys.exit(1)

    print(f"✅ {len(pages)}ページを取得")

    for page in pages:
        page_id = page['page_id']
        region_name = page['region_name']
        theme_title = page['theme_title']
        area_code = page['area_code']
        prefecture_code = page['prefecture_code']

        print(f"\n{'='*60}")
        print(f"📄 ページID: {page_id}")
        print(f"   地域: {region_name}")
        print(f"   テーマ: {theme_title}")
        print(f"{'='*60}")

        # ホテル取得
        print("\n🏨 ホテル情報取得中...")
        hotels = fetch_rakuten_hotels(area_code, prefecture_code, limit=15)
        print(f"✅ {len(hotels)}件のホテルを取得")

        if not hotels:
            print("⚠️ ホテルが見つかりません。スキップします。")
            continue

        # レビュー取得（最初の5軒のみ）
        print("\n💬 レビュー取得中...")
        for i, hotel in enumerate(hotels[:5]):
            reviews = fetch_reviews_from_web(str(hotel['hotel_no']), max_reviews=5)
            hotels[i]['reviews'] = reviews
            if reviews:
                print(f"   {hotel['hotel_name']}: {len(reviews)}件")

        # テーマデータ
        theme_data = {'theme_title': theme_title}

        # 記事生成
        print("\n✍️ 記事生成中...")
        content = generate_article_content(page, theme_data, hotels, gemini_api_key)

        # 後処理
        print("\n🔧 後処理中...")
        content = process_article(content, hotels)

        # 保存
        print("\n💾 保存中...")
        save_to_tidb(page_id, content, page.get('page_title', ''))

        print(f"\n✅ ページ {page_id} の生成完了")

    print("\n" + "=" * 60)
    print("🎉 全ページの生成が完了しました！")
    print("=" * 60)


if __name__ == '__main__':
    main()
