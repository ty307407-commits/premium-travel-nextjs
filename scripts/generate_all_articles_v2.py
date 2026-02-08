#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate articles for all pages using the confirmed analysis data from hotel_review_analysis_v2.
This script incorporates the pre-calculated analysis (radar chart, summary, persona match)
into the article generation process, ensuring high quality and consistency.
"""

import os
import sys
import json
import argparse
import time
import random
from typing import List, Dict, Optional

# Add search path for modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/v4")

# Mock or import dependencies
try:
    from modules.hotel_fetcher import HotelFetcher
    from modules.gemini_client import GeminiClient
    from modules.post_processor import PostProcessor
    from config.settings import HOTEL_SELECTION_CONFIG, AFFILIATE_CONFIG
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# --- Modified Prompt with Analysis Integration ---
MASTER_PROMPT_WITH_ANALYSIS = '''
あなたの役割（ペルソナ）

あなたは、天才的なトラベルマーケターであり、卓越したコピーライターです。あなたの唯一の使命は、私が指定した日本の温泉地をテーマに、特定のフォーマットとコンセプトに基づいた高品質なブログ記事を生成することです。

あなたが生成するブログ記事の基本情報

ターゲット読者: {persona_description}

記事のコアコンセプト: {content_concept}

テーマ: {theme_title}

トーン: {content_tone}

【ライティングスタイルと改行に関する最終・厳格ルール】

'説明'ではなく'描写'に徹する: 登場人物の心情を直接的に説明する過度な心理描写は避けてください。代わりに、具体的な情景、夫婦の会話、さりげない仕草を通じて、感情や気づきが読者に自然と伝わるように描写してください。

現在形を効果的に使う: 物語の基本は過去形で記述しますが、物語の最後の一文や情景描写では、意図的に現在形や現在進行形を使用し、臨場感と余韻を生み出してください。

改行ルールの厳格な使い分け:

A) 説明的な文章（'客室露天風呂の時間''食事''共用風呂'など）:
文章が長くなり読みにくくなるのを防ぐため、意味の区切りや話の転換点で、段落改行（ハードブレーク、2回改行）を積極的に使用し、一つの項目を2～3の短い段落に分けてください。

B) 物語的な文章（'ふたりで紡ぐ、宿の記憶'）:
このセクションでは、段落を分ける改行（ハードブレーク、2回改行）の使用を完全に禁止します。すべての改行は、例外なく『単一の改行（ソフトブレーク）』のみを使用してください。

【宿選定の指示 - 重要】

以下の候補宿リストから、テーマ「{theme_title}」とターゲット「{persona_description}」に最も適した宿を【必ず5〜10軒】選定し、【選定したすべての宿について詳細な記事を作成】してください。

候補宿リストには、AIによる事前の「詳細分析データ（analysis_summary, radar_chart, persona_match）」が含まれています。
この分析データを最大限に活用し、実際に宿泊したかのような解像度の高い描写を行ってください。

⚠️ 絶対に守るべきルール:
- 選定した宿すべてについて、「3. 宿の紹介」セクションで完全な記述を行うこと
- 1軒だけ記述して終了することは禁止
- 各宿について、必ず「## [HOTEL_LINK:宿名]」から「[CTA_BUTTON:宿名]」までの完全なセクションを記述すること
- 出力が長くなっても、必ず最後まで記述を完了すること
- 以下のプレースホルダーを必ず含めること:
  - [HOTEL_LINK:宿名]
  - [RADAR_CHART:宿名]  <-- 追加: レーダーチャート挿入用
  - [REVIEW_BLOCK:宿名]
  - [HOTEL_IMAGE:宿名]
  - [CTA_BUTTON:宿名]
  - [ACCESS_LINK:宿名]

候補宿リスト:
{candidate_hotels_json}

【記事の構成と要件】

1. タイトル
SEOとクリック率を最大化するタイトルを作成し、マークダウンの見出し1（#）で出力します。

【タイトルの必須ルール】
- 【温泉地名】を必ず冒頭に配置
- {persona_keyword}をタイトル前半に配置
- 「厳選○選」を末尾に配置（○には選定した宿の数を入れる）
- 「｜」で区切る

【禁止事項】
- 毎回同じ形式のタイトルを使わない（バリエーションを持たせる）
- 「厳選○選」をタイトル先頭に置かない（必ず末尾）
- {persona_keyword}をタイトル後半に置かない

2. 導入文
見出し: マークダウンの見出し2（##）として、「なぜ、〇〇（ターゲット）は△△温泉に惹きつけられるのか」のような、温泉地の特性や読者の心情に寄り添った見出しを作成。
内容:
- この温泉地ならではの魅力（歴史、文化、自然、食など）を情緒的に解説
- なぜターゲット読者の心に響くのかを説明
- 旅への期待感を最大限に高める文章を作成

### ■この温泉地の魅力・おすすめポイント
導入文の中に、以下の要素を含む「この地域ならではの魅力」を箇条書きまたは段落で記述：
- 温泉の泉質や効能の特徴
- 周辺の観光スポット・名所
- 地元の名物料理・特産品
- 季節ごとの楽しみ方（紅葉、雪景色、桜など）
- 文化的・歴史的な背景

[AREA_CTA]

3. 宿の紹介（選定した宿すべて）

⚠️ 重要: 各宿について【最低2000文字以上】の詳細な記述を行うこと。短い記述は禁止。

【各宿の記述項目】※この順番とフォーマットを厳守すること

宿見出し:
## [HOTEL_LINK:宿名]
#### ～キャッチコピー～

導入文（100〜150文字、1段落のみ）: 
(分析データの overall_summary を参考に、この宿の最大の魅力や特徴を簡潔に紹介)

[RADAR_CHART:宿名]

[REVIEW_BLOCK:宿名]

### ■おすすめポイント（宿名）
箇条書きで5つ記述。各行の先頭に「✅ 」を付けること。
(分析データの positive_keywords や summary を活用し、具体的な特徴を抽出すること)
例:
✅ 全室に専用露天風呂付きで、プライベートな時間を満喫できる
✅ お部屋で金目鯛を味わえる

[HOTEL_IMAGE:宿名]

### 客室
(分析データを元に、露天風呂付き客室の雰囲気や特徴を記述)

### 客室露天風呂の時間
読者が'今すぐこの湯船に浸かりたい'と心から渇望するような文章を作成。建築家のように露天風呂の物理的な魅力を描写し、詩人のように情緒的な時間を丁寧に紡ぐ。

### 共用風呂
【条件分岐】
A) 共用風呂がある場合: 大浴場や貸切風呂の設計思想などを情熱的に解説
B) 共用風呂がない場合: プライベート感を重視する宿の哲学としてポジティブに描写

### 食事
単なるメニュー紹介ではなく、料理長の哲学、地元食材へのこだわりなど'食の物語'を描写。

### こんな方におすすめ
箇条書きで3つ程度記述。各行の先頭に「✅ 」を付けること。(分析データの persona_match を参考に)
例:
✅ カップル・記念日: (persona_match.couple.reasonの内容)
✅ 静かな環境でゆっくり過ごしたい方

### アクセス情報
* 住所: (データから住所を記載)
* アクセス: (データからアクセス方法を記載)
* 送迎: (データから送迎情報を記載)
[ACCESS_LINK:宿名]

### ふたりで紡ぐ、宿の記憶
【最重要項目】その宿の最大の特徴をテーマに、{persona_keyword}の心温まる400字程度のショートストーリーを作成。
(分析データの「雰囲気」スコアやキーワードから着想を得る)

必ず守るルール:
- '説明'ではなく'描写'に徹する: 心情を直接説明せず、具体的な情景、夫婦の会話、さりげない仕草で感情を伝える
- 会話文（「」）を効果的に使い、リアルな夫婦のやり取りを描写する
- 物語の最後は現在形で臨場感と余韻を生み出す
- ソフトブレーク（単一改行）のみ使用。ハードブレーク（2回改行）は禁止

[CTA_BUTTON:宿名]

---

4. まとめ
見出し: ## まとめ｜さあ、ふたりの時間を紡ぐ旅へ
内容: 紹介した宿を箇条書きで要約し、読者の旅立ちを後押しする感動的なメッセージで締めくくる。

5. メタディスクリプション
---
【メタディスクリプション】
温泉地名、{persona_keyword}、露天風呂付き客室という要素を含む120文字程度の紹介文

6. SEOタグ
---
【SEOタグ】
温泉地名, 都道府県名, 露天風呂付き客室, {persona_keyword}, 夫婦旅, 選定した宿名すべて, 高級旅館, 温泉旅行, 記念日旅行

【重要な注意事項】
- プレースホルダー [HOTEL_LINK:宿名], [HOTEL_IMAGE:宿名], [REVIEW_BLOCK:宿名], [CTA_BUTTON:宿名], [ACCESS_LINK:宿名], [RADAR_CHART:宿名] は必ずそのまま出力すること
- 宿名は正確に、候補リストの表記と完全一致させること
- 分析データ(summary, keywords)の内容を文章に自然に組み込むこと
- userReviewの内容を参考にしつつ、そのまま引用せず、文章に自然に反映させること
'''


class ArticleGeneratorWithAnalysis:
    """記事生成クラス（分析データ活用版）"""

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

    def get_analysis_data(self, hotel_ids: List[int]) -> Dict:
        """TiDBから分析データを一括取得"""
        if not hotel_ids:
            return {}
        
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
                port=4000,
                user='4VWXcjUowH2PPCE.root',
                password='6KcooGBdpDcmeIGI',
                database='test',
                ssl_verify_cert=False,
                use_pure=True
            )
            cursor = conn.cursor(dictionary=True)
            
            format_strings = ','.join(['%s'] * len(hotel_ids))
            # hotel_review_analysis_v2 テーブルは hotel_id がキー
            query = f"SELECT hotel_id, analysis_json FROM hotel_review_analysis_v2 WHERE hotel_id IN ({format_strings})"
            cursor.execute(query, tuple(hotel_ids))
            
            results = {}
            for row in cursor.fetchall():
                try:
                    data = json.loads(row['analysis_json'])
                    # 分析データが配列の場合の対処 (check_analysis_results.pyの知見)
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    results[row['hotel_id']] = data
                except Exception as e:
                    # print(f"JSON Parse Error for hotel {row['hotel_id']}: {e}")
                    pass
            
            conn.close()
            return results
        except Exception as e:
            print(f"Analysis fetch error: {e}")
            return {}

    def fetch_all_page_ids(self) -> List[int]:
        """全ページIDを取得"""
        self.hotel_fetcher.connect()
        try:
            self.hotel_fetcher.cursor.execute("SELECT id FROM page_data ORDER BY id")
            return [row['id'] for row in self.hotel_fetcher.cursor.fetchall()]
        finally:
            self.hotel_fetcher.close()

    def build_prompt(self, onsen_area, theme_data, candidate_hotels, analysis_map, persona_data=None, area_highlights=None):
        """プロンプト構築"""
        if persona_data is None:
            # デフォルトペルソナ（テーマデータから推定できない場合のフォールバック）
            persona_data = {
                "description": "子育てを終え、経済的に比較的余裕のある50代の夫婦",
                "keyword": "50代夫婦",
                "concept": "ただ宿泊するだけではない、夫婦ふたりの時間を深く紡ぎ直すための旅"
            }

        hotels_for_prompt = []
        for h in candidate_hotels:
            hotel_id = h.get("hotel_no")
            analysis = analysis_map.get(hotel_id, {})
            
            # 分析データがあればそれを優先・追加
            hotels_for_prompt.append({
                "hotel_name": h.get("hotel_name"),
                "review_average": float(h.get("review_average") or 0.0),
                "review_count": int(h.get("review_count") or 0),
                "hotel_special": (h.get("hotel_special") or "")[:200], # 長すぎる場合は切り詰め
                "access": h.get("access") or "",
                "user_review": (h.get("user_review") or "")[:200], # 分析データ重視のため元レビューは減らす
                
                # --- 分析データ ---
                "analysis_summary": analysis.get("overall_summary", ""),
                "radar_chart": analysis.get("radar_chart_data", {}),
                "positive_keywords": analysis.get("positive_keywords", []),
                "persona_match": analysis.get("persona_match", {})
            })

        candidate_hotels_json = json.dumps(hotels_for_prompt, ensure_ascii=False, indent=2)

        prompt = MASTER_PROMPT_WITH_ANALYSIS.format(
            persona_description=persona_data.get("description", "50代夫婦"),
            persona_keyword=persona_data.get("keyword", "50代夫婦"),
            content_concept=persona_data.get("concept", "夫婦ふたりの時間を紡ぐ旅"),
            theme_title=theme_data.get("theme_title", f"{onsen_area}温泉旅行"),
            content_tone=theme_data.get("content_tone", "静かで上質"),
            candidate_hotels_json=candidate_hotels_json
        )
        
        if area_highlights:
             prompt += f"\n【この地域の参考情報（導入文に活用してください）】\n{area_highlights}\n"
             
        prompt += f"\n\n温泉地: {onsen_area}\n"
        
        return prompt

    def generate_for_page(self, page_id, dry_run=False):
        """1ページ分の生成実行"""
        print(f"\n{'='*60}")
        print(f"📄 Processing Page ID: {page_id}")
        print(f"{'='*60}")

        self.hotel_fetcher.connect()
        try:
            page_data = self.hotel_fetcher.get_page_data(page_id)
            if not page_data:
                print(f"Skipping page {page_id}: Not found")
                return None
                
            theme_data = self.hotel_fetcher.get_theme_data(page_data['theme_id'])
            
            # 設定値取得
            candidate_count = HOTEL_SELECTION_CONFIG.get("candidate_count", 20)
            
            candidates = self.hotel_fetcher.get_candidate_hotels(
                area_code=page_data['rakuten_area_code'],
                theme_id=page_data['theme_id'],
                limit=candidate_count
            )
            
            if not candidates or len(candidates) < HOTEL_SELECTION_CONFIG.get("absolute_min", 3):
                print(f"Skipping page {page_id}: User candidates count {len(candidates)} < min")
                return None

            print(f"  Area: {page_data['rakuten_area_name']}")
            print(f"  Theme: {theme_data['theme_title']}")
            print(f"  Candidates: {len(candidates)} hotels")

            # 分析データ取得
            hotel_ids = [h['hotel_no'] for h in candidates]
            analysis_map = self.get_analysis_data(hotel_ids)
            print(f"  Found analysis for {len(analysis_map)}/{len(hotel_ids)} hotels")
            
            # 地域情報
            area_highlights = self.hotel_fetcher.get_area_highlights(page_data['rakuten_area_code'])
            
            # ペルソナ構築（簡易版）
            persona_data = {
                "description": theme_data.get('target_audience') or "温泉好きの方",
                "keyword": "温泉旅行", # FIXME: テーマから抽出するロジックが必要だが、ここでは簡易化
                "concept": theme_data.get('content_tone') or "癒やしの旅"
            }
            # テーマ名から年代などを推測
            if "50代" in theme_data.get("theme_title", ""):
                persona_data["keyword"] = "50代夫婦"
            elif "カップル" in theme_data.get("theme_title", ""):
                 persona_data["keyword"] = "カップル"

            prompt = self.build_prompt(
                onsen_area=page_data.get('rakuten_area_name', '温泉地'),
                theme_data=theme_data,
                candidate_hotels=candidates,
                analysis_map=analysis_map,
                persona_data=persona_data,
                area_highlights=area_highlights
            )
            
            if dry_run:
                print("Dry Run: Prompt generated.")
                # print(prompt[:500])
                return {"prompt": prompt}

            # Gemini呼び出し
            print("  🤖 Calling Gemini API...")
            start_time = time.time()
            result = self.gemini_client.generate_article(prompt)
            duration = time.time() - start_time
            print(f"  ✅ Generated in {duration:.1f}s. Content length: {len(result.get('content', ''))}")
            
            # 生成結果の選定ホテルリストがない場合、Geminiが返さなかった可能性があるため、候補リスト全体を仮定
            # ただし、通常GeminiClientはselected_hotelsを抽出するロジックを持つはず
            
            # 保存処理
            if self.save_to_db(page_data, result):
                print(f"  ✅ Saved to DB successfully.")
            else:
                 print(f"  ❌ DB Save Failed.")
            
            return result

        except Exception as e:
            print(f"  ❌ Error processing page {page_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            self.hotel_fetcher.close()

    def save_to_db(self, page_data, result) -> bool:
        import mysql.connector
        try:
            conn = mysql.connector.connect(
                host='gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
                port=4000,
                user='4VWXcjUowH2PPCE.root',
                password='6KcooGBdpDcmeIGI',
                database='test',
                ssl_verify_cert=False,
                use_pure=True
            )
            cursor = conn.cursor()
            
            content = result.get('content', '')
            title = result.get('title', '無題')
            meta_desc = result.get('meta_description', '')
            selected_hotels = json.dumps(result.get('selected_hotels', []))
            word_count = len(content)

            # 既存チェックと保存
            # status='draft'で保存
            sql = """
                INSERT INTO articles (page_id, status, title, content, meta_description, selected_hotels, word_count)
                VALUES (%s, 'draft', %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    content = VALUES(content),
                    meta_description = VALUES(meta_description),
                    selected_hotels = VALUES(selected_hotels),
                    word_count = VALUES(word_count)
            """
            cursor.execute(sql, (
                page_data['id'],
                title,
                content,
                meta_desc,
                selected_hotels,
                word_count
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Save Error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None, help='Number of pages to process')
    parser.add_argument('--page-id', type=int, help='Specific page ID')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    generator = ArticleGeneratorWithAnalysis()
    
    if args.page_id:
        page_ids = [args.page_id]
    else:
        print("Fetching all page IDs...")
        page_ids = generator.fetch_all_page_ids()
        
    if args.limit:
        page_ids = page_ids[:args.limit]
        
    print(f"Starting generation for {len(page_ids)} pages...")
    
    success_count = 0
    for i, pid in enumerate(page_ids):
        print(f"\n[{i+1}/{len(page_ids)}]")
        result = generator.generate_for_page(pid, dry_run=args.dry_run)
        if result:
            success_count += 1
        
        # Rate limiting / polite pause
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Completed! Success: {success_count}/{len(page_ids)}")

if __name__ == "__main__":
    main()
