#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 記事生成メインスクリプト

単一のLLM呼び出しで記事全体を生成し、
Pythonで後処理（アフィリエイトリンク、画像、レビュー）を行う
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

# モジュールパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.hotel_fetcher import HotelFetcher, fetch_candidates_for_page
from modules.gemini_client import GeminiClient
from modules.post_processor import PostProcessor, process_article
from prompts.master_prompt import build_prompt
from config.settings import HOTEL_SELECTION_CONFIG, AFFILIATE_CONFIG

load_dotenv()


class ArticleGeneratorV4:
    """V4 記事生成クラス"""

    def __init__(self, affiliate_id: str = None):
        """
        Args:
            affiliate_id: 楽天アフィリエイトID（オプション）
        """
        # 優先順位: 引数 > 環境変数 > settings.py
        default_affiliate_id = AFFILIATE_CONFIG.get('rakuten', {}).get('affiliate_id', '')
        self.affiliate_config = {
            "affiliate_id": affiliate_id or os.getenv('RAKUTEN_AFFILIATE_ID', '') or default_affiliate_id
        }
        self.gemini_client = GeminiClient()
        self.hotel_fetcher = HotelFetcher()

    def generate_for_page(
        self,
        page_id: int,
        candidate_count: int = None,
        persona_override: dict = None,
        dry_run: bool = False
    ) -> Dict:
        """
        ページIDから記事を生成

        Args:
            page_id: ページID
            candidate_count: 候補ホテル数（デフォルト: 設定値）
            persona_override: ペルソナ上書き（テスト用）
            dry_run: True の場合、プロンプトのみ出力

        Returns:
            {
                "page_id": ページID,
                "title": タイトル,
                "content": 処理後の記事本文,
                "meta_description": メタディスクリプション,
                "seo_tags": SEOタグリスト,
                "selected_hotels": 選定されたホテル名リスト,
                "raw_output": LLM生の出力
            }
        """
        if candidate_count is None:
            candidate_count = HOTEL_SELECTION_CONFIG["candidate_count"]

        print(f"\n{'='*60}")
        print(f"📄 ページID: {page_id} の記事生成を開始")
        print(f"{'='*60}")

        # Step 1: データ取得
        print("\n📊 Step 1: データ取得中...")
        self.hotel_fetcher.connect()

        try:
            page_data = self.hotel_fetcher.get_page_data(page_id)
            if not page_data:
                raise ValueError(f"ページID {page_id} が見つかりません")

            theme_data = self.hotel_fetcher.get_theme_data(page_data['theme_id'])
            if not theme_data:
                raise ValueError(f"テーマID {page_data['theme_id']} が見つかりません")

            candidate_hotels = self.hotel_fetcher.get_candidate_hotels(
                area_code=page_data['rakuten_area_code'],
                theme_id=page_data['theme_id'],
                limit=candidate_count,
                min_review_count=HOTEL_SELECTION_CONFIG["min_review_count"],
                min_review_average=HOTEL_SELECTION_CONFIG["min_review_average"]
            )

            print(f"  ✅ ページ: {page_data['page_title']}")
            print(f"  ✅ テーマ: {theme_data['theme_title']}")
            print(f"  ✅ 候補ホテル: {len(candidate_hotels)} 件")

            if len(candidate_hotels) < HOTEL_SELECTION_CONFIG["absolute_min"]:
                print(f"  ⚠️ 候補ホテルが最低数({HOTEL_SELECTION_CONFIG['absolute_min']})未満です")
                return None

            # 地域情報（onsen_areas）を取得
            area_highlights = self.hotel_fetcher.get_area_highlights(page_data['rakuten_area_code'])
            if area_highlights:
                print(f"  ✅ 地域情報: {len(area_highlights)} 文字")
            else:
                print("  ⚠️ 地域情報が見つかりません（onsen_areas）")
                area_highlights = ""

        finally:
            self.hotel_fetcher.close()

        # Step 2: ペルソナ構築
        print("\n🎭 Step 2: ペルソナ構築中...")
        persona_data = persona_override or self._build_persona_from_theme(theme_data)
        print(f"  ✅ ターゲット: {persona_data.get('description', 'N/A')}")

        # Step 3: プロンプト構築
        print("\n📝 Step 3: プロンプト構築中...")
        onsen_area = page_data.get('rakuten_area_name', '温泉地')
        prompt = build_prompt(
            onsen_area=onsen_area,
            theme_data=theme_data,
            candidate_hotels=candidate_hotels,
            persona_data=persona_data,
            area_highlights=area_highlights
        )
        print(f"  ✅ プロンプト長: {len(prompt)} 文字")

        if dry_run:
            print("\n🔍 [DRY RUN] プロンプトのみ出力:")
            print("-" * 40)
            print(prompt[:2000] + "..." if len(prompt) > 2000 else prompt)
            return {"prompt": prompt, "page_data": page_data}

        # Step 4: LLM生成
        print("\n🤖 Step 4: Gemini API呼び出し中...")
        generation_result = self.gemini_client.generate_article(prompt)
        print(f"  ✅ 生成完了: {len(generation_result['content'])} 文字")
        print(f"  ✅ 選定ホテル: {len(generation_result['selected_hotels'])} 件")

        for idx, hotel_name in enumerate(generation_result['selected_hotels'], 1):
            print(f"      {idx}. {hotel_name}")

        # Step 5: ホテルデータ・著者情報・関連ページ取得
        print("\n🏨 Step 5: 選定ホテル・著者・関連ページのデータ取得中...")
        self.hotel_fetcher.connect()
        try:
            # 選定ホテルのデータ取得
            hotels_data = self.hotel_fetcher.get_hotels_by_names(
                generation_result['selected_hotels']
            )
            print(f"  ✅ {len(hotels_data)} 件のホテルデータを取得")

            # 著者情報取得
            author_id = page_data.get('author_id')
            author_info = None
            if author_id:
                author_info = self.hotel_fetcher.get_author_info(author_id)
                if author_info:
                    print(f"  ✅ 著者情報取得: {author_info.get('author_name', 'N/A')}")
                else:
                    print(f"  ⚠️ 著者ID {author_id} の情報が見つかりません")
            else:
                print("  ⚠️ 著者IDが設定されていません")

            # 関連ページ取得
            related_pages = self.hotel_fetcher.get_related_pages(
                page_id=page_id,
                theme_id=page_data['theme_id'],
                prefecture=page_data.get('rakuten_prefecture', ''),
                limit=5
            )
            print(f"  ✅ 関連ページ: {len(related_pages)} 件")
        finally:
            self.hotel_fetcher.close()

        # Step 6: 後処理
        print("\n🔧 Step 6: 後処理中...")
        processor = PostProcessor(
            page_id=page_id,
            hotels_data=hotels_data,
            affiliate_config=self.affiliate_config,
            author_info=author_info,
            related_pages=related_pages,
            hero_image_url=page_data.get('hero_image_url'),
            area_name=onsen_area
        )
        processed_content = processor.process(generation_result['content'])
        print(f"  ✅ 後処理完了: {len(processed_content)} 文字")

        # タイトル抽出
        title = self._extract_title(processed_content)

        result = {
            "page_id": page_id,
            "page_title": page_data['page_title'],
            "url_slug": page_data.get('url_slug', ''),
            "title": title,
            "content": processed_content,
            "meta_description": generation_result['meta_description'],
            "seo_tags": generation_result['seo_tags'],
            "selected_hotels": generation_result['selected_hotels'],
            "author": {
                "id": author_info.get('author_id') if author_info else None,
                "name": author_info.get('author_name') if author_info else None,
                "title": author_info.get('author_title') if author_info else None
            },
            "related_pages_count": len(related_pages),
            "raw_output": generation_result['raw_output'],
            "generated_at": datetime.now().isoformat()
        }

        print(f"\n✨ 記事生成完了!")
        print(f"  タイトル: {title[:50]}..." if len(title) > 50 else f"  タイトル: {title}")
        if author_info:
            print(f"  著者: {author_info.get('author_name', 'N/A')}")
        print(f"  関連ページ: {len(related_pages)} 件")

        return result

    def _build_persona_from_theme(self, theme_data: dict) -> dict:
        """テーマからペルソナを構築"""
        persona_text = theme_data.get('target_audience', '') or ''
        theme_title = theme_data.get('theme_title', '')
        target_keywords = theme_data.get('target_keywords', '') or ''

        # ターゲットとして使用可能なキーワード（優先順）
        audience_keywords = [
            '50代夫婦', '40代夫婦', '60代夫婦', '70代夫婦', 'シニア夫婦',
            'カップル', '夫婦', '女子旅', '一人旅', '家族'
        ]

        persona_keyword = None

        # target_keywords がカンマ区切りの場合、適切なキーワードを抽出
        if target_keywords:
            keywords_list = [k.strip() for k in target_keywords.split(',')]
            # 優先キーワードを探す
            for kw in audience_keywords:
                if kw in keywords_list:
                    persona_keyword = kw
                    break
            # 見つからなければ最後のキーワードを使用
            if not persona_keyword and keywords_list:
                persona_keyword = keywords_list[-1]

        # フォールバック: テーマタイトルから抽出
        if not persona_keyword:
            persona_keyword = "方"  # デフォルトは汎用的な「方」
            if "50代" in theme_title or "50代" in persona_text:
                persona_keyword = "50代夫婦"
            elif "40代" in theme_title or "40代" in persona_text:
                persona_keyword = "40代夫婦"
            elif "60代" in theme_title or "60代" in persona_text:
                persona_keyword = "60代夫婦"
            elif "70代" in theme_title or "70代" in persona_text:
                persona_keyword = "70代夫婦"
            elif "シニア" in theme_title or "シニア" in persona_text:
                persona_keyword = "シニア夫婦"
            elif "夫婦" in theme_title or "夫婦" in persona_text:
                persona_keyword = "夫婦"
            elif "カップル" in theme_title or "カップル" in persona_text:
                persona_keyword = "カップル"

        return {
            "description": persona_text or f"{persona_keyword}向けの上質な温泉旅行",
            "keyword": persona_keyword,
            "concept": theme_data.get('content_tone', 'ふたりの時間を紡ぐ旅')
        }

    def _extract_title(self, content: str) -> str:
        """Markdownからタイトルを抽出"""
        import re
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""


def _generate_html_output(result: Dict) -> str:
    """
    記事データから完全なHTMLドキュメントを生成
    コンテンツはそのまま出力（変換による干渉を防ぐ）
    """
    title = result.get('title', '記事')
    content = result.get('content', '')
    meta_description = result.get('meta_description', '')

    # コンテンツをそのまま使用（変換なし）
    html_body = content

    html_template = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_description}">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
        }}
        h1 {{
            font-size: 1.8em;
            color: #1a1a1a;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        h2 {{
            font-size: 1.4em;
            color: #333;
            margin-top: 40px;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        h3 {{
            font-size: 1.2em;
            color: #444;
            margin-top: 30px;
        }}
        p {{
            margin: 1em 0;
        }}
        ul {{
            padding-left: 25px;
        }}
        li {{
            margin: 8px 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 40px 0;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        blockquote {{
            margin: 15px 0;
            padding: 15px 20px;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            font-style: italic;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            padding: 16px 32px;
            border-radius: 30px;
            text-decoration: none !important;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(102,126,234,0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102,126,234,0.5);
        }}
        .cta-container {{
            text-align: center;
            margin: 30px 0;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>'''

    return html_template


def _save_to_database(result: Dict, page_id: int) -> bool:
    """
    記事をTiDB Data APIで保存

    Returns:
        保存成功: True, 失敗: False
    """
    import base64
    import requests

    # TiDB Data API設定
    TIDB_API_BASE = "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint"
    TIDB_AUTH = base64.b64encode(b'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286').decode()

    content = result.get('content', '')
    url = f"{TIDB_API_BASE}/save_page_content"
    payload = {"page_id": int(page_id), "content": content}

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Basic {TIDB_AUTH}",
                "Content-Type": "application/json"
            },
            timeout=60
        )

        if response.status_code == 200:
            print(f"✅ TiDB Data APIに保存: page_id={page_id}")
            return True
        else:
            print(f"❌ Data API保存エラー: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ データベース保存エラー: {e}")
        return False


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='V4 記事生成スクリプト')
    parser.add_argument('--page-id', type=int, required=True, help='生成対象のページID')
    parser.add_argument('--candidate-count', type=int, default=20, help='候補ホテル数')
    parser.add_argument('--dry-run', action='store_true', help='プロンプトのみ出力')
    parser.add_argument('--output', type=str, help='出力ファイルパス')
    parser.add_argument('--output-dir', type=str, default='./output', help='出力ディレクトリ')
    parser.add_argument('--save-db', action='store_true', default=True, help='TiDBに保存（デフォルト: 有効）')
    parser.add_argument('--no-save-db', action='store_true', help='TiDBに保存しない')

    args = parser.parse_args()

    # 生成実行
    generator = ArticleGeneratorV4()
    result = generator.generate_for_page(
        page_id=args.page_id,
        candidate_count=args.candidate_count,
        dry_run=args.dry_run
    )

    if result is None:
        print("\n❌ 記事生成に失敗しました")
        sys.exit(1)

    # 出力
    if args.output:
        output_path = args.output
    else:
        os.makedirs(args.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            args.output_dir,
            f"article_{args.page_id}_{timestamp}.json"
        )

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n📁 出力ファイル: {output_path}")

    # Markdown形式でも出力
    md_path = output_path.replace('.json', '.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(result.get('content', ''))

    print(f"📁 Markdownファイル: {md_path}")

    # HTML形式で出力（ブラウザで直接表示可能）
    html_path = output_path.replace('.json', '.html')
    html_content = _generate_html_output(result)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"📁 HTMLファイル: {html_path}")
    print(f"\n💡 HTMLファイルをブラウザで開くと記事を確認できます")

    # TiDBに保存（デフォルトで有効、--no-save-dbで無効化）
    if args.save_db and not args.no_save_db:
        print("\n📤 TiDBに保存中...")
        if _save_to_database(result, args.page_id):
            preview_url = f"https://premium-travel-japan.com/preview?id={args.page_id}"
            print(f"\n{'='*60}")
            print(f"🔗 プレビューURL: {preview_url}")
            print(f"{'='*60}")
            print("   ↑ クリックで記事を確認できます")


if __name__ == '__main__':
    main()
