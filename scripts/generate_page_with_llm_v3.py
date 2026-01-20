#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEMINI 2.5 Flashを使用したページ生成スクリプト v3 (TiDB対応版)
Phase 5: ページ構成とロジック実装
"""

import os
import sys
import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup
import mysql.connector
from typing import Dict, List, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 楽天API認証情報
RAKUTEN_APP_ID = os.environ.get('RAKUTEN_APP_ID', '1029472204308393704')
RAKUTEN_AFFILIATE_ID = os.environ.get('RAKUTEN_AFFILIATE_ID', '12426598.beaffa49.12426599.e0b47e86')

# OpenAI APIクライアント（クラス内で初期化）
client = None


def apply_line_breaks(content: str, break_rule: str) -> str:
    """改行ルールを適用"""
    if content is None or not content:
        return ""
    
    # 会話文の改行処理（「」「」連続パターン）
    # 例: 「こんにちは」「元気？」 → 「こんにちは」<br>「元気？」
    content = apply_conversation_breaks(content)
    
    if break_rule == 'ソフトブレーク':
        # 全ての改行を<br>に変換（空行は無視）
        lines = content.split('\n')
        result = []
        for line in lines:
            line = line.strip()
            if line:
                result.append(line)
        return '<br>\n'.join(result)
    
    elif break_rule == 'ハードブレーク':
        # 空行で段落を分ける（段落内の改行は保持）
        paragraphs = []
        current_paragraph = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line:
                current_paragraph.append(line)
            elif current_paragraph:
                # 段落内の行は改行で繋ぐ（スペースではなく）
                paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = []
        
        if current_paragraph:
            paragraphs.append('\n'.join(current_paragraph))
        
        # 段落間は空行で分ける
        return '\n\n'.join(paragraphs)
    
    else:
        # デフォルトはハードブレーク
        return apply_line_breaks(content, 'ハードブレーク')


def format_dialogue_and_prose(content: str) -> str:
    """会話文と地の文を正しく整形する後処理関数
    
    ルール:
    1. 会話文（「で始まり」で終わる行）が連続する場合 → 1つの段落内で<br>で区切る
    2. 地の文が連続する場合 → 1つの段落内で<br>で区切る
    3. 会話文と地の文の切り替わり → 別の段落
    
    前処理:
    - 「...」「...」 のような連続会話を分割
    - 「...」と言った。 のようなパターンを分割
    
    会話文の判定:
    - 行が「で始まり、」で終わり、「」が1組だけ → 会話文
    - それ以外 → 地の文
    """
    if not content:
        return content
    
    import re
    
    # LLMが出力した余分な<br>を削除
    content = re.sub(r'<br\s*/?>', '\n', content)
    
    # === 前処理: 連続会話のみ分割（文中の引用は分割しない） ===
    # パターン: 「...」「...」 → 「...」\n「...」
    # 行頭の連続会話文のみ分割（」の直後に「が続く場合）
    content = re.sub(r'」「', '」\n「', content)
    
    # 行ごとに分割して処理
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not lines:
        return content
    
    # === 会話文判定関数 ===
    def is_pure_dialogue(line: str) -> bool:
        """純粋な会話文かどうかを判定
        
        条件:
        1. 行が「で始まる
        2. 行が」で終わる
        3. 「」が1組だけ（文中に別の「」がない）
        """
        if not line.startswith('「') or not line.endswith('」'):
            return False
        
        # 「と」の数をカウント
        open_count = line.count('「')
        close_count = line.count('」')
        
        # 「」が1組だけなら会話文
        return open_count == 1 and close_count == 1
    
    # === 段落を構築 ===
    paragraphs = []
    current_block = []  # 連続する同種の行を一時保存
    current_is_dialogue = None  # 現在のブロックが会話文かどうか
    
    for line in lines:
        is_dialogue = is_pure_dialogue(line)
        
        if current_is_dialogue is None:
            # 最初の行
            current_block.append(line)
            current_is_dialogue = is_dialogue
        elif is_dialogue == current_is_dialogue:
            # 同じ種類（会話文同士または地の文同士）の連続
            current_block.append(line)
        else:
            # 種類が切り替わった
            # たまっているブロックを出力（改行のみ、nl2brが<br>に変換）
            if current_block:
                paragraphs.append('\n'.join(current_block))
            # 新しいブロックを開始
            current_block = [line]
            current_is_dialogue = is_dialogue
    
    # 最後に残っているブロックを出力
    if current_block:
        paragraphs.append('\n'.join(current_block))
    
    # 段落間は空行で区切る（Markdownでは\n\nが段落区切り）
    return '\n\n'.join(paragraphs)


def apply_conversation_breaks(content: str) -> str:
    """会話文（「」）の連続パターンに改行を挿入（後方互換用）
    
    例:
    「こんにちは」「元気？」 → 「こんにちは」<br>「元気？」
    """
    if not content:
        return content
    
    import re
    
    # パターン: 」の直後に「が続く場合（間に空白があってもなくても）
    # 」「 → 」<br>「
    pattern = r'」\s*「'
    replacement = '」<br>\n「'
    
    result = re.sub(pattern, replacement, content)
    
    return result


def should_display_image(image_url, images_count):
    """画像を表示すべきかを判定（ルールベース）"""
    if not image_url:
        return False
    
    # ルール1: サムネイルは表示しない
    if 'thumbnail' in image_url.lower():
        return False
    
    # ルール2: 画像が2枚未満の場合は表示しない
    if images_count < 2:
        return False
    
    return True


def generate_google_maps_url(address, hotel_name):
    """Google MapsのURLを生成（埋め込み用）"""
    import urllib.parse
    
    # Google Mapsの埋め込みURLを生成（APIキー不要）
    encoded_address = urllib.parse.quote(f"{hotel_name} {address}")
    
    # Google Mapsの検索URL（クリックでGoogle Mapsが開く）
    maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
    
    return maps_url


def fetch_hotel_images(hotel_no: str, max_images: int = 5) -> List[str]:
    """楽天APIから宿の画像を取得"""
    url = 'https://app.rakuten.co.jp/services/api/Travel/HotelDetailSearch/20170426'
    params = {
        'applicationId': RAKUTEN_APP_ID,
        'hotelNo': str(hotel_no),
        'formatVersion': 2
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        hotels = data.get('hotels', [])
        if not hotels or not hotels[0]:
            return []
        
        # Correct structure: hotels[0][0]['hotelBasicInfo']
        hotel_basic_info = hotels[0][0].get('hotelBasicInfo', {})
        images = []
        
        # メイン画像
        hotel_image_url = hotel_basic_info.get('hotelImageUrl')
        if hotel_image_url:
            images.append(hotel_image_url)
        
        # 客室画像
        room_image_url = hotel_basic_info.get('roomImageUrl')
        if room_image_url and room_image_url not in images:
            images.append(room_image_url)
        
        # 地図画像
        map_image_url = hotel_basic_info.get('hotelMapImageUrl')
        if map_image_url and map_image_url not in images:
            images.append(map_image_url)
        
        return images[:max_images]
    
    except Exception as e:
        print(f"    ⚠️ 画像取得エラー: {e}")
        return []


class LLMPageGeneratorV3:
    """TiDBと連携したページ生成クラス"""
    
    def __init__(self):
        print("=" * 80)
        print("LLMページ生成システム v3 (TiDB版) 初期化")
        print("=" * 80)
        
        # DB接続
        self.conn = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST'),
            port=os.getenv('DATABASE_PORT'),
            user=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            database=os.getenv('DATABASE_NAME'),
            ssl_ca=os.getenv('DATABASE_SSL_CA'),
            ssl_verify_cert=True
        )
        self.cursor = self.conn.cursor(dictionary=True)
        print("✅ TiDB: 接続完了")
        
        # Vertex AIを優先して使用（service_account.jsonが必要）
        self.model = None
        self.openai_client = None
        self.llm_provider = None
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                'service_account.json'
            )
            vertexai.init(
                project='gen-lang-client-0978608719', 
                location='us-east4',
                credentials=credentials
            )
            self.model = GenerativeModel("gemini-2.5-flash")
            self.llm_provider = 'vertex'
            print("✅ Vertex AI (Gemini 2.5 Flash): 準備完了")
        except Exception as e:
            print(f"⚠️ Vertex AI初期化エラー: {e}")
            print("❌ service_account.jsonをスクリプトと同じディレクトリに配置してください。")
        
        # テンプレート読み込み
        self.content_templates = self._load_content_templates()
        print(f"✅ Content_Templates: {len(self.content_templates)}項目")
        print("=" * 80 + "\n")

    def _load_content_templates(self) -> List[Dict]:
        """DBからテンプレートを読み込み"""
        self.cursor.execute("SELECT * FROM content_templates")
        return self.cursor.fetchall()

    def _get_page_data(self, page_id: int) -> Optional[Dict]:
        """ページデータを取得"""
        self.cursor.execute("SELECT * FROM page_data WHERE id = %s", (page_id,))
        return self.cursor.fetchone()

    def _get_theme(self, theme_id: int) -> Optional[Dict]:
        """テーマ情報を取得"""
        self.cursor.execute("SELECT * FROM themes WHERE id = %s", (theme_id,))
        return self.cursor.fetchone()

    def _get_page_blocks(self, template_name: str = 'default') -> List[Dict]:
        """
        page_blocksテーブルからブロック構成を取得
        display_orderに従ってソートされたブロックリストを返す
        
        block_type:
        - INTRODUCTION: 導入文
        - AREA_HIGHLIGHTS: 周辺の魅力・見どころ
        - HOTEL_CONTENT: 宿コンテンツ（レビューセクション含む）
        - AUTHOR_INFO: 著者情報
        - RELATED_LINKS: 関連リンク
        """
        try:
            self.cursor.execute(
                "SELECT * FROM page_blocks WHERE template_name = %s ORDER BY display_order",
                (template_name,)
            )
            blocks = self.cursor.fetchall()
            if blocks:
                print(f"✅ page_blocks: {len(blocks)}ブロックを取得 (template: {template_name})")
                for block in blocks:
                    print(f"   - [{block['display_order']}] {block['block_type']}")
                return blocks
            else:
                print(f"⚠️ page_blocks: template '{template_name}' が見つかりません。デフォルト順序を使用します。")
                return self._get_default_page_blocks()
        except Exception as e:
            print(f"⚠️ page_blocks取得エラー: {e}。デフォルト順序を使用します。")
            return self._get_default_page_blocks()

    def _get_default_page_blocks(self) -> List[Dict]:
        """
        DB接続失敗時のデフォルトブロック構成
        MASTER_PLAN.mdの設計に従う
        """
        return [
            {'display_order': 1, 'block_type': 'INTRODUCTION', 'template_name': 'default', 'generation_prompt': None},
            {'display_order': 2, 'block_type': 'AREA_HIGHLIGHTS', 'template_name': 'default', 'generation_prompt': None},
            {'display_order': 3, 'block_type': 'HOTEL_CONTENT', 'template_name': 'default', 'generation_prompt': None},
            {'display_order': 4, 'block_type': 'RELATED_LINKS', 'template_name': 'default', 'generation_prompt': None},
            {'display_order': 5, 'block_type': 'AUTHOR_INFO', 'template_name': 'default', 'generation_prompt': None},
        ]

    def _fetch_reviews_from_web(self, hotel_id: int) -> List[Dict]:
        """
        楽天トラベルのレビューページからレビューを取得する（スクレイピング）
        Returns: List[Dict] with keys 'text' and 'date'
        """
        url = f"https://travel.rakuten.co.jp/HOTEL/{hotel_id}/review.html"
        print(f"  🔍 レビュー取得中: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # スクリプトタグからJSONを探す
            for element in soup.find_all('script'):
                content = element.string
                if content and "window.PRELOADED_STATE=" in content:
                    json_str = content.strip()
                    if json_str.startswith("window.PRELOADED_STATE="):
                        json_str = json_str[len("window.PRELOADED_STATE="):]
                        if json_str.endswith(";"):
                            json_str = json_str[:-1]
                        
                        try:
                            data = json.loads(json_str)
                            if 'reviewList' in data:
                                contents = data['reviewList'].get('data', {}).get('contents', [])
                                
                                good_reviews = []
                                for c in contents:
                                    text = c.get('comment', '')
                                    score = c.get('overallScore', 0)
                                    check_in_date = c.get('reservation', {}).get('checkInDate', '')
                                    
                                    # 評価4以上、かつ本文がある程度の長さ（20文字以上）
                                    if score >= 4 and text and len(text) > 20:
                                         # 改行を削除して1行にする
                                         text = text.replace('\n', ' ')
                                         
                                         # 日付をフォーマット（例: 2024-12-07 → 2024年12月）
                                         date_str = None
                                         if check_in_date:
                                             try:
                                                 from datetime import datetime
                                                 dt = datetime.strptime(check_in_date, '%Y-%m-%d')
                                                 date_str = f"{dt.year}年{dt.month}月"
                                             except:
                                                 date_str = None
                                         
                                         good_reviews.append({
                                             'text': text,
                                             'date': date_str
                                         })
                                         if len(good_reviews) >= 3:
                                             break
                                
                                if good_reviews:
                                    print(f"  ✅ {len(good_reviews)}件のレビューを取得しました")
                                    return good_reviews
                                    
                        except json.JSONDecodeError:
                            continue
            
            print("  ⚠️ レビューデータが見つかりませんでした")
            return []
            
        except Exception as e:
            print(f"  ⚠️ レビュー取得エラー: {e}")
            return []

    def _get_hotels_for_page(self, area_code: str, theme_id: int, limit: int = 10) -> List[Dict]:
        """
        エリアとテーマに基づいてホテルを選定
        1. rakuten_area_masterからエリア名を取得
        2. hotelsテーブルをエリア名で検索
        3. テーマのキーワードでフィルタリング
        4. 情報充実度でフィルタリング（hotel_special/レビュー数）
        5. 評価順にソート
        
        選定ロジック:
        - hotel_special >= 100文字 → 採用
        - hotel_special >= 50文字 AND レビュー >= 20件 → 採用
        - hotel_special < 50文字 AND レビュー >= 50件 → 採用
        - それ以外 → スキップ
        """
        # エリア名取得
        self.cursor.execute("SELECT area_name FROM rakuten_area_master WHERE area_code = %s", (area_code,))
        area_row = self.cursor.fetchone()
        if not area_row:
            print(f"⚠️ エリアコード {area_code} が見つかりません")
            return []
        
        area_name = area_row['area_name']
        
        # テーマキーワード取得
        self.cursor.execute("SELECT hotel_search_keywords FROM themes WHERE id = %s", (theme_id,))
        theme_row = self.cursor.fetchone()
        keywords = []
        if theme_row and theme_row['hotel_search_keywords']:
            keywords = [k.strip() for k in theme_row['hotel_search_keywords'].split(',')]
        
        # ホテル検索クエリ構築（情報充実度フィルタリング追加）
        query = """
            SELECT * FROM hotels 
            WHERE (address1 LIKE %s OR address2 LIKE %s)
            AND (
                LENGTH(hotel_special) >= 100
                OR (LENGTH(hotel_special) >= 50 AND review_count >= 20)
                OR (LENGTH(hotel_special) < 50 AND review_count >= 50)
            )
        """
        params = [f"%{area_name}%", f"%{area_name}%"]
        
        if keywords:
            keyword_conditions = []
            for k in keywords:
                keyword_conditions.append("(hotel_name LIKE %s OR hotel_special LIKE %s)")
                params.extend([f"%{k}%", f"%{k}%"])
            
            if keyword_conditions:
                query += " AND (" + " OR ".join(keyword_conditions) + ")"
        
        # 十分な数を取得するために多めに取得（limitの3倍）
        query += " ORDER BY review_average DESC LIMIT %s"
        params.append(limit * 3)
        
        self.cursor.execute(query, tuple(params))
        hotels = self.cursor.fetchall()
        
        # 必要数だけ返す
        return hotels[:limit]

    def _get_related_links(self, current_page: Dict, limit: int = 5) -> List[Dict]:
        """関連リンクを生成"""
        links = []
        
        # 1. 同じ県の別エリア
        self.cursor.execute("""
            SELECT id, page_title, url_slug FROM page_data 
            WHERE rakuten_prefecture = %s 
            AND id != %s 
            ORDER BY RAND() LIMIT %s
        """, (current_page['rakuten_prefecture'], current_page['id'], 3))
        links.extend(self.cursor.fetchall())
        
        # 2. 同じテーマの別エリア
        self.cursor.execute("""
            SELECT id, page_title, url_slug FROM page_data 
            WHERE theme_id = %s 
            AND id != %s 
            ORDER BY RAND() LIMIT %s
        """, (current_page['theme_id'], current_page['id'], 2))
        links.extend(self.cursor.fetchall())
        
        return links

    def _get_author_info(self, author_id: int) -> Optional[Dict]:
        """著者情報を取得"""
        if not author_id:
            return None
        self.cursor.execute("SELECT * FROM authors WHERE id = %s", (author_id,))
        return self.cursor.fetchone()

    def _generate_page_introduction(self, page: Dict, theme: Dict, hotels: List[Dict]) -> str:
        """記事の導入文を生成"""
        hotel_names = "、".join([h['hotel_name'] for h in hotels[:3]])
        
        prompt = f"""
あなたはプロのトラベルライターです。
読者が「ここに行きたい」と感じる導入文を、**描写だけ**で作成してください。

# 記事情報
- タイトル: {page['page_title']}
- テーマ: {theme.get('theme_title')}
- エリア: {page.get('rakuten_area_name')}
- 紹介する宿の例: {hotel_names} など

# 絶対禁止ワード
以下の表現は一切使用しないでください：
- 「〜してくれます」「〜ようです」「〜感覚」「〜思い」
- 「まるで〜のよう」「〜を感じさせ」「〜に誘う」「〜誘います」
- 「心が〜」「魂が〜」といった抽象的な心理描写
- 「深い安らぎ」「至福」「極上」などの結論
- 「解き放たれる」「満たされる」「癒される」

# 必須要素（3つ以上使う）
1. **視覚**: 色、光、形、動き、景色
2. **聴覚**: 音、声、静寂
3. **触覚**: 温度、質感、重さ、湿度
4. **嗅覚**: 香り、空気の匂い

# 書き方の鉄則
- 「〜な気持ち」と言わず、読者がそう感じる情景を描く
- 抽象名詞（安らぎ、感動、至福）ではなく、具体的な動詞と名詞
- 夫婦の短い会話を入れても良い（1往復まで）

# 出力
300文字程度。見出しは含めず、本文のみを出力してください。
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.8
                }
            )
            content = response.text
            if content:
                content = content.strip()
            else:
                content = ""
            return content
        except Exception as e:
            print(f"    ⚠️ 導入文生成エラー: {e}")
            return f"{page.get('rakuten_area_name')}は、心安らぐ温泉地です。"

    def _generate_meta_description(self, page_data: Dict, theme: Dict) -> str:
        """SEO最適化されたmeta descriptionを生成（70-120文字）"""
        page_title = page_data.get('page_title', '')
        area_name = page_data.get('rakuten_area_name', '')
        theme_title = theme.get('theme_title', '')
        
        prompt = f"""
        以下の情報を元に、SEO最適化されたmeta descriptionを生成してください。

        ページタイトル: {page_title}
        温泉地: {area_name}
        テーマ: {theme_title}

        ルール:
        - 全体で70〜120文字（日本語）厳守
        - 最初の70文字に主要キーワードと魅力を凝縮（スマホ対応）
        - 温泉地名、テーマを前半に配置
        - 具体的なベネフィットを含める
        - 「。」で終わる完結した文章
        - 余計な説明や前置きは不要、meta descriptionのテキストのみを出力
        """
        
        try:
            print(f"  📝 meta_description 生成中...")
            response = self.model.generate_content(prompt)
            if response and response.text:
                meta_desc = response.text.strip()
                # 改行や余計な空白を削除
                meta_desc = ' '.join(meta_desc.split())
                # 120文字を超える場合は切り詰め
                if len(meta_desc) > 120:
                    meta_desc = meta_desc[:117] + '...'
                print(f"  ✅ meta_description 生成完了 ({len(meta_desc)}文字)")
                return meta_desc
            else:
                return f"{area_name}の温泉宿をご紹介。{theme_title}にぴったりの宿が見つかります。"
        except Exception as e:
            print(f"  ⚠️ meta_description生成エラー: {e}")
            return f"{area_name}の温泉宿をご紹介。{theme_title}にぴったりの宿が見つかります。"
    
    def _save_meta_description(self, page_id: int, meta_description: str):
        """生成したmeta_descriptionをTiDBに保存"""
        try:
            self.cursor.execute(
                "UPDATE page_data SET meta_description = %s WHERE page_id = %s",
                (meta_description, page_id)
            )
            self.conn.commit()
            print(f"  ✅ meta_description をTiDBに保存しました")
        except Exception as e:
            print(f"  ⚠️ meta_description保存エラー: {e}")

    def _generate_area_highlights(self, area_name: str, theme: Dict) -> str:
        """エリアの観光スポットセクションを生成（AREA_HIGHLIGHTS）"""
        
        # DBからプロンプトを取得
        self.cursor.execute(
            "SELECT generation_prompt FROM page_blocks WHERE block_type = 'AREA_HIGHLIGHTS'"
        )
        row = self.cursor.fetchone()
        
        if row and row.get('generation_prompt'):
            # DBのプロンプトを使用（変数を置換）
            prompt_template = row['generation_prompt']
            prompt = prompt_template.replace('{area_name}', area_name)
            prompt = prompt.replace('{theme_title}', theme.get('theme_title', ''))
        else:
            # フォールバックプロンプト
            prompt = f"""
あなたは50代夫婦向けの温泉旅行ライターです。
{area_name}周辺のおすすめ観光スポットを4つ紹介してください。

# 要件
- 50代夫婦が楽しめる場所を選ぶ
- 各スポットは名前と短い説明（50文字程度）
- 季節の見どころや特徴を含める
- 具体的な描写を心がける

# 出力形式
以下の形式で出力（HTMLタグを含む）:

<div class="area-highlights">
<h3>🌿 {area_name}周辺のおすすめ観光スポット</h3>
<div class="highlight-grid">
<div class="highlight-item">
<span class="highlight-label">観光</span>
<strong>スポット名</strong>
<p>説明文</p>
</div>
<!-- 4つのスポットを同様の形式で -->
</div>
</div>
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.7
                }
            )
            content = response.text
            if content:
                content = content.strip()
                # Markdownのコードブロックを削除
                if content.startswith('```html'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
            return content
        except Exception as e:
            print(f"    ⚠️ 観光スポット生成エラー: {e}")
            return ""

    def _generate_hotel_content(self, hotel, theme, selected_items, page):
        """ホテルのコンテンツを生成"""
        print(f"Generating content for hotel: {hotel['hotel_name']}")
        
        # 必須項目の定義（順序重要）
        # DBのテンプレートIDを使用
        # ※宿見出し(1)は_generate_all_hotel_contentで生成済みのため除外
        # 4:導入文（タイトル非表示）, 2:おすすめポイント
        base_top = [4, 2]
        
        # 6:ふたりで紡ぐ、宿の記憶, 90:こんな50代夫婦におすすめ, 45:客室イメージ, 5:アクセス情報, 46:アクセスマップ, 3:感動体験ボタン, 7:感情的クロージングリンク
        base_bottom = [6, 90, 45, 5, 46, 3, 7]
        
        # タイトルを非表示にするテンプレートID
        # ※宿見出し(1)は_generate_all_hotel_contentで生成済みのため除外
        NO_TITLE_IDS = [4, 3, 7, 46]  # 46: アクセスマップはタイトルなしで埋め込み

        # テンプレートごとのカスタムタイトル（DBのtemplate_idを使用）
        CUSTOM_TITLES = {
            2: "この宿の魅力",
            12: "プライベート温泉で過ごす至福の時間",
            28: "心に残るおもてなし",
            6: "二人だけの特別な思い出",
            90: "こんな50代夫婦におすすめ",
            45: "お部屋の雰囲気",
            5: "アクセス・交通案内",
            46: "地図で確認",
        }
        
        # selected_items (カンマ区切り文字列) をパースしてIDに変換
        selected_template_ids = []
        if selected_items and isinstance(selected_items, str):
            items = [x.strip() for x in selected_items.split(',') if x.strip()]
            for item in items:
                if item.isdigit():
                    selected_template_ids.append(int(item))
                else:
                    # 名前で検索
                    found = next((t['id'] for t in self.content_templates if t['template_name'] == item), None)
                    if found:
                        selected_template_ids.append(found)
                    else:
                        print(f"  DEBUG: Template name '{item}' not found")
        
        # 重複排除しつつ結合
        # base_top + selected + base_bottom
        # ただし、baseに含まれるものがselectedにもある場合はselectedの方を無視（順序優先）
        
        target_template_ids = list(base_top)
        
        for tid in selected_template_ids:
            if tid not in base_top and tid not in base_bottom:
                target_template_ids.append(tid)
                
        target_template_ids.extend(base_bottom)

        print(f"  DEBUG: target_template_ids: {target_template_ids}")

        # 画像情報の取得
        images = fetch_hotel_images(hotel['hotel_no']) 
        print(f"  DEBUG: Fetched images: {len(images)} items")
        
        # レビュー情報の取得（スクレイピング）
        reviews = self._fetch_reviews_from_web(hotel['hotel_no'])
        # プロンプト用のテキスト形式に変換
        reviews_text = "\n".join([f"・{r['text']}" for r in reviews]) if reviews else ""
        
        content_parts = [] # Initialize content_parts list
        
        for template_id in target_template_ids:
            template = next((t for t in self.content_templates if t.get('template_id') == template_id or t.get('id') == template_id), None)
            
            if not template:
                print(f"  DEBUG: Template ID {template_id} not found in content_templates")
                continue
                
            print(f"  📝 {hotel['hotel_name']} - {template['template_name']} 生成中...")
            
            # 画像テンプレートの処理
            if template_id in [86, 87, 88]:
                # ... (image handling code remains same, omitted for brevity in replace_file_content if not changing)
                # Wait, I need to include the image handling code if I'm replacing the block.
                # Since I'm replacing a large block, I should be careful.
                # Actually, I can just insert the review fetching before the loop, and the prompt modification inside the loop.
                # Let's do it in two steps or be very precise.
                pass

            # ... (Image handling logic) ...
            # DBのテンプレートID: 44=施設外観, 45=客室イメージ, 46=アクセスマップ
            image_url = None
            if template_id in [44, 45, 46]:
                if template_id == 44 and images:
                    image_url = images[0]
                elif template_id == 45 and len(images) > 1:
                    image_url = images[1]
                elif template_id == 46:
                    address = f"{hotel.get('address1', '')}{hotel.get('address2', '')}".strip()
                    if address:
                        map_url = generate_google_maps_url(address, hotel['hotel_name'])
                        if map_url:
                            image_url = map_url
                
                if template_id == 45 and image_url and ('map' in image_url.lower() or 'access' in image_url.lower()):
                    if len(images) > 2:
                        image_url = images[2]
                    else:
                        image_url = None
                
                if template_id == 46:
                    # アクセスマップ: Google Maps埋め込みiframeとして出力
                    address = f"{hotel.get('address1', '')}{hotel.get('address2', '')}".strip()
                    hotel_name = hotel.get('hotel_name', '宿')
                    if address:
                        # Google Maps Embed API（APIキー不要の埋め込み形式）
                        import urllib.parse
                        encoded_query = urllib.parse.quote(f"{hotel_name} {address}")
                        embed_url = f"https://maps.google.com/maps?q={encoded_query}&output=embed&hl=ja"
                        content_parts.append(f'''\n<div class="map-section">
<h4>📍 {hotel_name}の地図</h4>
<div class="map-container">
<iframe src="{embed_url}" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div>
</div>\n''')
                    else:
                        print(f"  ⚠️ 住所情報がないため地図を表示できません")
                elif image_url:
                    credit = "出典：楽天トラベル"
                    credit_html = f"<p class='image-credit'>{credit}</p>"
                    # 画像のみ表示（タイトルなし）- SEO用のalt属性には宿名を使用
                    hotel_name = hotel.get('hotel_name', '客室')
                    if template_id == 45:
                        # 客室イメージ: タイトルなしで画像のみ
                        content_parts.append(f"\n![{hotel_name}の客室]({image_url})\n{credit_html}\n")
                    elif template_id == 44:
                        # 施設外観: タイトルなしで画像のみ
                        content_parts.append(f"\n![{hotel_name}の外観]({image_url})\n{credit_html}\n")
                    else:
                        content_parts.append(f"\n![{template['template_name']}]({image_url})\n{credit_html}\n")
                else:
                    print(f"  ⚠️ 画像が見つかりません: {template['template_name']}")
                continue

            # 通常のテキスト生成
            prompt = template['generation_prompt']
            if not prompt:
                continue
            
            # レビュー情報をプロンプトに追加（該当するテンプレートのみ）
            if reviews_text and template['template_name'] in ['導入文', '宿見出し', 'おすすめポイント', '料理・食事', '客室露天風呂', 'サービス・おもてなし', 'ふたりで紡ぐ、宿の記憶', 'こんな50代夫婦におすすめ']:
                prompt += f"\n\n# 参考情報（実際の口コミ）\n以下の実際の口コミを参考に、具体的な描写や感動を盛り込んでください（ただし、口コミをそのまま引用するのではなく、エッセンスを取り入れてください）：\n{reviews_text}"

            # プロンプトの変数を置換
            # Map template variables to actual data fields
            affiliate_id = RAKUTEN_AFFILIATE_ID  # 定数から取得（確実にアフィリエイトIDを使用）
            hotel_no = hotel.get('hotel_no') or hotel.get('hotelNo')
            if hotel_no:
                hotel_url = f"https://travel.rakuten.co.jp/HOTEL/{hotel_no}/{hotel_no}.html"
            else:
                hotel_url = hotel.get('hotel_information_url', '') or hotel.get('plan_list_url', '')
            
            if template['template_name'] in ['感動体験ボタン', 'アクセス情報']:
                print(f"  DEBUG: [{template['template_name']}] hotelUrl='{hotel_url}', access='{hotel.get('access', '')}'")

            if affiliate_id and hotel_url:
                import urllib.parse
                encoded_url = urllib.parse.quote(hotel_url)
                affiliate_url = f"https://hb.afl.rakuten.co.jp/hgc/{affiliate_id}/?pc={encoded_url}"
            else:
                affiliate_url = hotel_url

            # プロンプト変数のマッピング（包括的かつ安全に）
            prompt_vars = {
                # 基本情報
                'hotel_name': hotel.get('hotel_name', ''),
                'hotelName': hotel.get('hotel_name', ''),
                'hotel_special': hotel.get('hotel_special', ''),
                'hotelSpecial': hotel.get('hotel_special', ''),
                'area': page.get('rakuten_area_name', ''),
                'region_name': page.get('rakuten_area_name', ''),
                'target_audience': theme.get('target_audience', '50代夫婦'),
                'onsen_area': page.get('rakuten_area_name', ''),
                'reviews': reviews_text, # Add reviews to vars just in case

                
                # レビュー・評価
                'user_review': hotel.get('user_review', ''),
                'userReview': hotel.get('user_review', ''),
                'reviewAverage': hotel.get('review_average', '-'),
                'review_average': hotel.get('review_average', '-'),
                'reviewCount': hotel.get('review_count', '-'),
                'review_count': hotel.get('review_count', '-'),
                'roomAverage': hotel.get('room_average', '-'),
                'bathAverage': hotel.get('bath_average', '-'),
                'mealAverage': hotel.get('meal_average', '-'),
                'serviceAverage': hotel.get('service_average', '-'),
                'locationAverage': hotel.get('location_average', '-'),
                
                # テーマ関連
                'theme_title': theme.get('theme_title', ''),
                'content_tone': theme.get('content_tone', '丁寧で親しみやすい'),
                'persona': theme.get('persona', '旅行好き'),
                'preferred_hotel_types': theme.get('preferred_hotel_types', ''),
                'main_features': theme.get('target_keywords', ''),
                'author_specialty_theme': theme.get('theme_title', ''), # 仮
                
                # その他（データがない場合は空文字）
                'activity_programs': '',
                'nearby_attractions': '',
                'onsen_count': '',
                'onsen_quality_list': '',
                'access': hotel.get('access', ''),
                'address': f"{hotel.get('address1', '')}{hotel.get('address2', '')}".strip(),
                'address_with_postal': (f"〒{hotel.get('postal_code', '')} {hotel.get('address1', '')}{hotel.get('address2', '')}" if hotel.get('postal_code') else f"{hotel.get('address1', '')}{hotel.get('address2', '')}").strip(),
                'address1': hotel.get('address1', ''),
                'address2': hotel.get('address2', ''),
                'postal_code': hotel.get('postal_code', ''),
                'hotelUrl': hotel_url,
                'affiliateUrl': affiliate_url,
                'affiliate_url': affiliate_url,
            }

            try:
                # プロンプト内の変数を抽出
                required_keys = re.findall(r'\{([a-zA-Z0-9_]+)\}', prompt)
                safe_vars = prompt_vars.copy()
                
                # 足りないキーは空文字で埋める
                for key in required_keys:
                    if key not in safe_vars:
                        # print(f"    ⚠️ Missing key: {key}, using empty string")
                        safe_vars[key] = ""
                
                formatted_prompt = prompt.format(**safe_vars)
                
            except Exception as e:
                print(f"    ⚠️ プロンプト変数置換エラー: {e}. Using raw prompt.")
                formatted_prompt = prompt
            # 感動体験ボタン（CTA）用の特別プロンプト処理
            if template['template_name'] == '感動体験ボタン':
                formatted_prompt = f"""
あなたはプロのWebマーケター兼コピーライターです。
以下の宿の情報を元に、読者が「泊まってみたい！」と強く感じ、予約ページへ進みたくなるような「感動体験ボタン（CTA）」のコンテンツを作成してください。

# 宿情報
評価: {prompt_vars['review_average']}

# 作成要件
1. **マイクロコピー（キャッチコピー）**: 宿の魅力を凝縮し、読者の感情に訴えかける15〜25文字程度の言葉。「〜しませんか？」「〜な体験を。」など、問いかけや誘いの形式が良い。
2. **ボタン文言**: クリックしたくなる具体的なアクション。「{prompt_vars['hotel_name']}の空室を見る ➜」のような形式。矢印（➜）を含めること。
3. **リンクURL**: {affiliate_url}

# 出力フォーマット
マイクロコピー: [ここにマイクロコピー]
ボタン文言: [ここにボタン文言]
リンクURL: {affiliate_url}

余計な説明は省き、上記フォーマットのみを出力してください。
"""
            # アクセス情報用の特別プロンプト処理
            elif template['template_name'] == 'アクセス情報':
                formatted_prompt = f"""
以下の宿のアクセス情報を、シンプルで分かりやすく案内してください。

# 宿名
{prompt_vars['hotel_name']}

# 住所
{prompt_vars['address_with_postal']}

# アクセス情報
{prompt_vars['access']}

# 出力フォーマット（必ずこの形式で出力してください）
**住所**: [住所をここに記載]

**アクセス方法**:
- [電車でのアクセス]
- [車でのアクセス]

**送迎**: [送迎情報、なければ「なし」]

# 出力要件
- マークダウンの見出し（#, ##, ###）は絶対に使用しないこと
- 太字（**）とリスト（-）のみ使用
- 簡潔で分かりやすい表現
- 上記のフォーマットを厳守すること
"""
            # 客室露天風呂(54)用の特別プロンプト処理（構造強制）
            elif template['template_name'] == '客室露天風呂':
                formatted_prompt = f"""
あなたはプロのトラベルライターです。
以下の宿の「客室露天風呂」での滞在シーンを、臨場感たっぷりに描いてください。

# 宿情報
- 宿名: {prompt_vars['hotel_name']}
- 特徴: {prompt_vars['hotel_special']}
- ターゲット: {prompt_vars['target_audience']}
- 温泉の質: {prompt_vars['onsen_quality_list']}

# 必須構成（以下の順序で記述すること）
1. **会話文1**: 入浴直後の感動や第一声（例：「わぁ、素敵ね」「ああ、いい湯だ」）
2. **地の文1**: 露天風呂の情景、広さ、景色、お湯の質感、香りを五感に訴えるように描写（200文字程度）
3. **会話文2**: リラックスした夫婦の会話、幸せな気分の共有
4. **地の文2**: 心理描写と結び（心身が満たされる感覚、思い出に残るという確信）

# 執筆ルール
- **会話文と地の文は必ず改行で区切ること**
- 会話文は「」で囲むこと
- 地の文は「です・ます」調で統一すること
- ターゲット層（{prompt_vars['target_audience']}）に響く、落ち着いた上質なトーンで書くこと
- **本文中で「50代」や「熟年」といった年齢を特定する言葉は絶対に使わないこと**（あくまでその世代に響く内容であれば良い）
# 執筆要件
1. **「Show, Don't Tell（語るな、見せろ）」を徹底すること**。
    - 「豪華な」「洗練された」といった抽象的な形容詞で説明するのではなく、具体的な描写（素材、光、音、香りなど）を通じて、読者にその情景を感じさせてください。
    - 悪い例：「洗練されたモダンな空間で、美味しい料理を味わえます。」
    - 良い例：「磨き上げられた黒柿のテーブルに、旬の鮎が踊るように盛り付けられている。箸を伸ばせば、炭火の香ばしさがふわりと鼻腔をくすぐった。」
2. ターゲット層（{prompt_vars['target_audience']}）の心に響く、情緒的なトーンで書くこと。
3. 決して「〜が魅力です」や「〜をお楽しみください」といった説明口調にしないこと。あくまで物語の始まりのように。
4. **禁止事項**:
    - **「50代」「40代」「60代」「熟年」などの年齢を特定する言葉は絶対に使用しないこと。**
    - 「結婚5周年」という言葉で書き出さないこと（自然な流れで触れるのは可）。
5. 決して「導入文」のような書き出しにせず、いきなりシーンから始めること。

# 出力例
「わぁ、なんて開放的なの！」「本当だ、風が気持ちいいな」

目の前に広がるのは、鮮やかな緑と澄み渡る青空。二人で足を伸ばしてもまだ余裕のある檜の湯船には、源泉かけ流しの湯がたっぷりと湛えられています。肌に触れた瞬間、とろりとした感触が全身を包み込み、日頃の疲れがすーっと溶け出していくよう。湯気とともに立ち上る木の香りが、深い安らぎへと誘います。
"""
            elif template['template_name'] == '宿見出し':
                 formatted_prompt = template['generation_prompt'].format(**prompt_vars)

            elif template['template_name'] == 'おすすめポイント':
                 formatted_prompt = f"""
あなたはプロの編集者です。
この宿の魅力を、**箇条書き4点**で紹介してください。

# 絶対禁止
- 「〜できます」「〜してくれます」「〜を感じられます」
- 「極上」「至福」「上質」などの抽象形容詞
- 「心が〜」「魂が〜」といった心理描写
- 「〜をもたらします」「〜を彩ります」

# 書き方
- 各項目は1-2文（各50文字以内）
- **何が、どうなっているのか**を具体的に描く
- 読者がそれを読んで「それなら魅力的だ」と思える具体性

# 宿情報
- 宿名: {prompt_vars['hotel_name']}
- 特徴: {prompt_vars['hotel_special']}
- テーマ: {prompt_vars['theme_title']}

# 参考情報（実際の口コミ）
{reviews_text}

# 悪い例
- 極上の温泉で心身を癒すことができます
- 上質なおもてなしが滞在を彩ります

# 良い例
- 全室に温泉露天風呂。誰にも邪魔されず、朝も夜も好きな時間に箱根の名湯を独り占め。
- 到着時、スタッフが荷物を持ち、笑顔で「お待ちしておりました」と声をかけてくれる。

# 出力フォーマット
[リード文（1文、30文字以内）]
- [おすすめポイント1]
- [おすすめポイント2]
- [おすすめポイント3]
- [おすすめポイント4]
"""
            # 客室露天風呂(54)用の特別プロンプト処理（構造強制）
            elif template['template_name'] == '客室露天風呂':
                 formatted_prompt = template['generation_prompt'].format(**prompt_vars)
                 pass

            # 心に残るおもてなし(70)用の特別プロンプト処理
            elif template['template_name'] == '心に残るおもてなし':
                formatted_prompt = f"""
あなたはプロのトラベルライターです。
この宿のスタッフが**実際に何をするのか**を、具体的な行動だけで描いてください。

# 絶対禁止
- 「心尽くしのおもてなし」「上質なホスピタリティ」などの抽象表現
- 「お客様を大切に」「最上級の体験へ」といった結論
- 「してくれます」「してくださいます」の連発
- 「きめ細やか」「丁寧」などの説明
- 「滞在を彩ります」「〜をもたらします」

# 必須要素
1. **到着時の具体的な対応**（誰が、どこで、何をするのか）
2. **滞在中の細やかな配慮**（具体例を2つ以上）
3. **スタッフのセリフ**（1-2箇所、実際に言いそうな自然な言葉）

# 書き方の鉄則
- 「きめ細やか」と言わず、実際の行動を描く
- 夫婦がどう感じたかは書かない（読者に推測させる）

# 宿情報
- 宿名: {prompt_vars['hotel_name']}

# 参考情報（実際の口コミ）
{reviews_text}

# 悪い例
> スタッフが心を込めておもてなしします。きめ細やかな配慮で滞在を彩ります。

# 良い例
> 車を降りると、スタッフが駆け寄り「お待ちしておりました」と笑顔で迎えてくれた。荷物を受け取ると、「少しお疲れですか？お部屋で温かいお茶をご用意しますね」と声をかけ、先に立って案内してくれる。
> 
> 夕食時、ペースに合わせて次の料理が運ばれてくる。一品ごとに「この鮎は今朝、近くの川で獲れたものです」と説明があり、食材への愛着が伝わってきた。

# 出力
300文字程度。見出しは不要、本文のみ。
"""
            # 二人だけの特別な思い出(50)用の特別プロンプト処理
            elif template['template_name'] == '二人だけの特別な思い出':
                formatted_prompt = f"""
あなたはプロの小説家です。
以下の宿での滞在を通じて、夫婦の絆が深まる感動的なショートストーリーを作成してください。

# 宿情報
- 宿名: {prompt_vars['hotel_name']}
- 特徴: {prompt_vars['hotel_special']}
- ターゲット: {prompt_vars['target_audience']}

# ストーリー構成
1. **導入**: 宿に到着した時の高揚感、または部屋に入った瞬間の感動。
2. **展開**: 夫婦での会話。過去（新婚当時など）を振り返り、現在の幸せを噛み締めるシーン。
3. **結び**: この宿での滞在が、これからの二人にとって大切な思い出になるという確信。

# 執筆ルール
- **会話文と地の文を織り交ぜること**（会話文多めが望ましい）。
- 会話文は「」で囲むこと。
- **本文中で「50代」や「熟年」といった年齢を特定する言葉は絶対に使わないこと**。
- ターゲット層（{prompt_vars['target_audience']}）が共感できる、落ち着いた大人の恋愛小説のようなトーンで。
- 決して「導入文」のような書き出しにせず、いきなりシーンから始めること。

# 出力例
チェックインを済ませ、部屋に入ると、窓一面に広がる紅葉が二人を出迎えてくれた。

「わぁ、すごい。まるで絵画みたいね」
「本当だ。君に見せたかったんだ、この景色を」

夫の言葉に、妻は少し照れくさそうに微笑む。結婚してから30年。子育ても落ち着き、ようやく二人きりで旅行に来られた。

「ねえ、覚えてる？新婚旅行も温泉だったわよね」
「ああ。あの時は緊張して、あまりゆっくり話せなかったな」

露天風呂に浸かりながら、昔話に花を咲かせる。湯の温もりが、長い年月を共に歩んできた二人の心を優しく包み込んでいく。

「また来ようね。今度は桜の季節に」
「うん、約束だ」

この宿で過ごした時間は、二人のアルバムに新たな1ページとして刻まれた。
"""
            else:

                try:
                    formatted_prompt = template['generation_prompt'].format(**prompt_vars)
                except KeyError as ke:
                    print(f"    ⚠️ プロンプト変数置換エラー: {ke}. Using raw prompt.")
                    formatted_prompt = prompt
            
            # Retry logic for API rate limits
            max_retries = 3
            for retry in range(max_retries):
                try:
                    if not self.model:
                        raise Exception("Vertex AI model not initialized")

                    response = self.model.generate_content(
                        formatted_prompt,
                        generation_config={
                            "max_output_tokens": 8192,  # Increased to max for thinking mode
                            "temperature": 0.7,
                        }
                    )
                    
                    if response.text:
                        content = response.text.strip()
                        
                        # 全体共通: 「。」と「」」が連続する場合の修正（強制置換）
                        content = content.replace('」。', '」')
                        content = content.replace('。」', '」') # 句点＋閉じ括弧も修正
                        content = re.sub(r'」\s*。', '」', content) # 改行やスペース後の句点も削除
                        content = re.sub(r'」\n+。', '」\n', content)
                        
                        # 会話文の改行処理（強化版）
                        # 1. 閉じ括弧の後に開き括弧が続く場合は改行を入れる
                        content = re.sub(r'」\s*「', '」\n\n「', content)
                        # 2. 閉じ括弧の後に地の文が続く場合は改行を入れる
                        content = re.sub(r'」([^\n「])', '」\n\n\\1', content)
                        # 3. 地の文の後に開き括弧が続く場合は改行を入れる
                        content = re.sub(r'([。！？])\s*「', '\\1\n\n「', content)
                        # 4. 連続する改行を2つに統一
                        content = re.sub(r'\n{3,}', '\n\n', content)

                        # タイトルの有無を判定
                        # CRITICAL FIX: Use 'template_id' because constants (3, 4, 7, etc.) match 'template_id', not 'id' (PK)
                        raw_id = template.get('template_id')
                        try:
                            template_id_val = int(raw_id)
                        except (ValueError, TypeError):
                            # print(f"    ⚠️ Invalid template ID: {raw_id}")
                            template_id_val = -1

                        # DEBUG: Log to file
                        with open("debug_log.txt", "a") as f:
                            f.write(f"Processing Template ID (PK): {template_id_val}\n")
                            if template_id_val in [48, 49, 47, 50, 54, 70]:
                                f.write(f"  Target Template Found: {template_id_val}\n")
                                f.write(f"  Content Start: {content[:50]!r}\n")

                        # ヘルパー関数: 強制改行（約200-250文字ごと）
                        def apply_forced_line_breaks(text):
                            forced_break_content = ""
                            current_chunk = ""
                            for char in text:
                                current_chunk += char
                                # 句点、感嘆符、疑問符、閉じ括弧のタイミングで改行
                                if len(current_chunk) > 200 and char in ['。', '！', '？', '!', '?', '」']:
                                    forced_break_content += current_chunk + "<br>\n"
                                    current_chunk = ""
                            forced_break_content += current_chunk
                            return forced_break_content

                        # 導入文(4)の書き出し修正（禁止ワード削除）と強制改行
                        if template_id_val == 4:
                            # 「結婚5周年」などで始まる場合、そのフレーズを削除
                            prohibited_patterns = [
                                r'^\s*結婚5周年[、！!。]',
                                r'^\s*結婚5周年記念[、！!。]',
                                r'^\s*5周年記念[、！!。]',
                                r'^\s*結婚5周年という輝かしい節目[、！!。]',
                                r'^\s*結婚5周年', # 最も汎用的なパターン
                            ]
                            for pattern in prohibited_patterns:
                                content = re.sub(pattern, '', content).strip()
                            
                            # タイトル削除
                            content = re.sub(r'^#+\s*導入文\s*$', '', content, flags=re.MULTILINE)
                            content = re.sub(r'^\*\*導入文\*\*\s*$', '', content, flags=re.MULTILINE)
                            content = content.replace('### 導入文', '')

                            # 強制改行ルール（！、？の後）
                            content = content.replace('！', '！\n\n').replace('？', '？\n\n')
                            content = re.sub(r'\n{3,}', '\n\n', content) # 余分な改行削除

                            # プログラムによる強制改行
                            content = apply_forced_line_breaks(content)

                        # サービス・おもてなし(28)の強制改行
                        if template_id_val in [28]:
                            content = apply_forced_line_breaks(content)

                        # 客室露天風呂(12)とふたりで紡ぐ、宿の記憶(6)の特別フォーマット
                        # 後処理関数で会話文と地の文を正しく整形
                        if template_id_val in [12, 6]:
                            # まず強制改行を適用（地の文が長くなりすぎないように）
                            content = apply_forced_line_breaks(content)
                            # 後処理関数で会話文と地の文を整形
                            content = format_dialogue_and_prose(content)

                        # アクセス情報(5)の分割とスタイル修正
                        if template_id_val == 5:
                            # まず箇条書き記号を統一
                            content = content.replace('- ', '■ ').replace('* ', '■ ')
                            content = re.sub(r'^\s*-\s+', '■ ', content, flags=re.MULTILINE)
                            
                            # 内容を解析して分割
                            lines = content.split('\n')
                            public_transport = []
                            car_access = []
                            
                            for line in lines:
                                line = line.strip()
                                if not line: continue
                                # キーワード判定
                                if any(k in line for k in ['車', 'IC', 'インター', '駐車場', 'マイカー']):
                                    car_access.append(line)
                                else:
                                    # デフォルトは公共交通機関扱い（住所などは除く）
                                    if not line.startswith('**住所'):
                                        public_transport.append(line)

                            new_content = ""
                            if public_transport:
                                new_content += "**公共交通機関でのアクセス**:\n" + "\n".join(public_transport) + "\n\n"
                            if car_access:
                                new_content += "**お車でのアクセス**:\n" + "\n".join(car_access)
                            
                            if new_content:
                                content = new_content.strip()

                        # 感動体験ボタン(3)の処理: HTMLボタン形式に変換
                        if template_id_val == 3:
                            # タイトル削除
                            content = re.sub(r'^#+\s*感動体験ボタン\s*$', '', content, flags=re.MULTILINE)
                            content = re.sub(r'^\*\*感動体験ボタン\*\*\s*$', '', content, flags=re.MULTILINE)
                            content = content.replace('### 感動体験ボタン', '')
                            
                            # LLMの出力からマイクロコピーとボタン文言を抽出してHTMLボタンに変換
                            lines = [l.strip() for l in content.strip().split('\n') if l.strip()]
                            micro_copy = ''
                            button_text = 'この宿の空室を見る ➜'
                            for line in lines:
                                if 'マイクロコピー' in line:
                                    micro_copy = line.split(':', 1)[-1].strip() if ':' in line else line.replace('マイクロコピー', '').strip()
                                elif 'ボタン文言' in line:
                                    button_text = line.split(':', 1)[-1].strip() if ':' in line else button_text
                            
                            # HTMLボタンを生成
                            content = f'''<div class="cta-section">
<p class="micro-copy">{micro_copy}</p>
<a href="{affiliate_url}" target="_blank" class="cta-button">{button_text}</a>
</div>'''

                        # 感情的クロージングリンク(7)の処理
                        if template_id_val == 7:
                            # LLMが生成した感情的な一文をボタンに変換
                            # 「」や余計な改行を削除
                            closing_text = content.strip()
                            closing_text = closing_text.replace('「', '').replace('」', '')
                            closing_text = closing_text.replace('\n', ' ').strip()
                            # ボタンHTMLを生成
                            content = f'<div class="emotional-closing"><a href="{affiliate_url}" target="_blank" class="closing-button">{closing_text}</a></div>'

                        # ターゲット(90)の動的置換（年代削除・汎用タイトル化）
                        if template_id_val in [90, 30001]:
                            target_audience = prompt_vars.get('target_audience', '50代夫婦')
                            
                            # ターゲット種別判定
                            if '夫婦' in target_audience:
                                title_suffix = "ご夫婦"
                            elif '家族' in target_audience:
                                title_suffix = "ご家族"
                            elif 'グループ' in target_audience:
                                title_suffix = "グループ旅行"
                            else:
                                title_suffix = "方" # 汎用
                            
                            # カスタムタイトル更新（年代を削除）
                            CUSTOM_TITLES[90] = f"こんな{title_suffix}におすすめ"
                            CUSTOM_TITLES[30001] = f"こんな{title_suffix}におすすめ"
                            
                            # コンテンツ内の「50代」等の具体的な年代記述を削除または汎用化
                            content = re.sub(r'\d+代', '', content) # 年代を削除
                            content = content.replace('夫婦', title_suffix) # ターゲットに合わせて置換

                            # タイトル削除（Markdown, 太字, 鍵括弧など）
                            content = re.sub(r'^#+\s*こんな.*おすすめ\s*$', '', content, flags=re.MULTILINE)
                            content = re.sub(r'^\*\*こんな.*おすすめ\*\*\s*$', '', content, flags=re.MULTILINE)
                            content = re.sub(r'^\s*[「【].*おすすめ.*[」】]\s*$', '', content, flags=re.MULTILINE)

                        if template_id_val in NO_TITLE_IDS:
                            if template_id_val in [2, 90, 46, 3, 7]:  # 3:感動体験ボタン, 7:感情的クロージングリンクはHTML出力なのでそのまま
                                processed_content = content
                            elif template_id_val == 4:
                                # 導入文は強制的にハードブレーク（プログラムで入れた<br>を活かすため）
                                processed_content = apply_line_breaks(content, 'ハードブレーク')
                            else:
                                processed_content = apply_line_breaks(content, template.get('break_rule', 'ハードブレーク'))
                            content_parts.append(f"\n{processed_content}\n")
                        else:
                            title = CUSTOM_TITLES.get(template_id_val, template['template_name'])
                            # 箇条書き(2, 90)はapply_line_breaksをバイパス
                            if template_id_val in [2, 90]:
                                processed_content = content
                            elif template_id_val in [12, 6]:
                                # 客室露天風呂(12)とふたりで紡ぐ(6)は既に整形済みなのでそのまま
                                processed_content = content
                            elif template_id_val == 28:
                                # サービス(28)は強制改行適用済みなのでハードブレークで整形
                                processed_content = apply_line_breaks(content, 'ハードブレーク')
                            else:
                                processed_content = apply_line_breaks(content, template.get('break_rule', 'ハードブレーク'))
                            content_parts.append(f"### {title}\n\n{processed_content}")

                        # おすすめポイント(2)の直後に中間リンクを挿入（マイクロボタン化 + target="_blank"）
                        if template_id_val == 2:
                            link_text = "この宿の空室・料金を見る ➜"
                            # class="middle-link micro-button" に変更し、target="_blank"を追加
                            content_parts.append(f'\n<div class="middle-link micro-button"><a href="{affiliate_url}" target="_blank">{link_text}</a></div>\n')
                            
                            # レビューセクションを追加（2-3件）
                            if reviews:
                                review_html = '\n<div class="review-section">\n<h3>宿泊者が語る、この宿の魅力</h3>\n\n'
                                for i, review_data in enumerate(reviews[:3]):  # 最大3件
                                    # reviewsが文字列のリストかオブジェクトのリストかチェック
                                    if isinstance(review_data, str):
                                        review_text = review_data
                                        review_date = None
                                    else:
                                        review_text = review_data.get('text', '')
                                        review_date = review_data.get('date', None)
                                    
                                    review_html += f'<div class="review-item">\n\n> 「{review_text}」\n\n'
                                    if review_date:
                                        review_html += f'<div class="review-citation">— {review_date}ご宿泊</div>\n\n</div>\n\n'
                                    else:
                                        review_html += f'<div class="review-citation">— ご宿泊のお客様より</div>\n\n</div>\n\n'
                                review_html += '</div>\n'
                                content_parts.append(review_html)

                    else:
                        print(f"    ⚠️ 生成コンテンツが空でした ({template['template_name']})")
                        # フォールバック
                        content_parts.append(f"### {template['template_name']}\n\n（{template['template_name']}の内容 - 生成失敗）")
                    
                    break  # Success
                    
                except Exception as e:
                    error_str = str(e)
                    # Retry on Rate Limit (429) or Server Errors (500, 503)
                    if ('429' in error_str or '500' in error_str or '503' in error_str) and retry < max_retries - 1:
                        wait_time = 2 ** retry
                        print(f"  ⚠️ APIエラー ({error_str})。{wait_time}秒後にリトライ... ({retry + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"  ⚠️ 生成エラー ({template['template_name']}): {e}")
                        # エラー時も極力コンテンツを埋める（空欄よりはマシ）
                        if template['template_name'] == 'ふたりで紡ぐ、宿の記憶':
                             content_parts.append(f"### {template['template_name']}\n\n（現在、感動的なストーリーを準備中です。もう少々お待ちください。）")
                        else:
                             content_parts.append(f"### {template['template_name']}\n\n（{template['template_name']}の内容 - エラー）")
                        break
                
        return "\n\n".join(content_parts)

    def _sanitize_content(self, content: str) -> str:
        """
        生成されたコンテンツから不適切な表現（年齢特定など）を除去・置換する
        """
        forbidden_phrases = {
            "50代": "大人",
            "40代": "大人",
            "60代": "シニア",
            "70代": "シニア",
            "熟年": "大人",
            "シニア": "大人",
            "高齢者": "年配の方",
            "情報なし": "",
            "記載なし": "",
            "車でのアクセス: なし": "",
            "車でのアクセス情報は直接の記載がありません": ""
        }
        
        sanitized = content
        for phrase, replacement in forbidden_phrases.items():
            sanitized = sanitized.replace(phrase, replacement)
            
        # Remove empty lines caused by removal
        sanitized = re.sub(r'\n\s*\n', '\n\n', sanitized)
        
        # Remove lines that are just bullets with empty content
        sanitized = re.sub(r'^\s*[-*]\s*$', '', sanitized, flags=re.MULTILINE)
        
        # ========== 車のアクセス情報：ネガティブ表現の完全削除 ==========
        # ユーザーフィードバックに基づく3つの最悪パターンとその類似表現
        
        # パターン1-3: ユーザーが指摘した具体例
        sanitized = re.sub(r'■\s*\*\*車でのアクセス\*\*[:：]?\s*なし', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*車でのアクセス[:：]?\s*なし', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*車でのアクセス情報は記載がありません', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*車でのアクセスに関する具体的な情報はございません', '', sanitized, flags=re.MULTILINE)
        
        # パターン4-10: 類似表現の網羅的削除
        sanitized = re.sub(r'■\s*車でのアクセス[:：]?\s*（情報はありません）', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*車でのアクセス[:：]?\s*情報はありません', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*車でのアクセス[:：]?\s*記載がありません', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*車でのアクセス[:：]?\s*$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*お車でのアクセス[:：]?\s*なし', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*お車でのアクセス[:：]?\s*（情報はありません）', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*お車でのアクセス[:：]?\s*情報はありません', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'■\s*お車でのアクセス[:：]?\s*$', '', sanitized, flags=re.MULTILINE)
        
        # **車でのアクセス**: 形式も削除
        sanitized = re.sub(r'\*\*車でのアクセス\*\*[:：]?\s*なし', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*車でのアクセス\*\*[:：]?\s*（情報はありません）', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*車でのアクセス\*\*[:：]?\s*情報はありません', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*車でのアクセス\*\*[:：]?\s*記載がありません', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*お車でのアクセス\*\*[:：]?\s*なし', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*お車でのアクセス\*\*[:：]?\s*（情報はありません）', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*お車でのアクセス\*\*[:：]?\s*$', '', sanitized, flags=re.MULTILINE)
        
        # セクションヘッダー直後に内容がない場合の削除
        sanitized = re.sub(r'\*\*お車でのアクセス\*\*[:：]?\s*\n\s*■', '■', sanitized, flags=re.MULTILINE)
        
        # 既存のパターン（電車、送迎）
        sanitized = re.sub(r'■\s*電車でのアクセス[:：]?\s*$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'^\s*■\s*なし\s*$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'\*\*送迎\*\*[:：]\s*なし\s*$', '', sanitized, flags=re.MULTILINE)
        
        # Remove entire Access Info block if it becomes empty or only contains "None"
        if "アクセス・交通案内" in sanitized:
             # Remove lines that became empty (just newlines)
             sanitized = re.sub(r'\n\s*\n', '\n\n', sanitized)
             # If the section is now just the header and maybe "公共交通機関でのアクセス:" but no content
             # This is hard to perfect with regex, but let's try to clean up "orphan headers"
             sanitized = re.sub(r'\*\*公共交通機関でのアクセス\*\*:\s*\n\s*\n', '', sanitized, flags=re.MULTILINE)
             sanitized = re.sub(r'\*\*お車でのアクセス\*\*:\s*\n\s*\n', '', sanitized, flags=re.MULTILINE)
             sanitized = re.sub(r'\*\*アクセス方法\*\*:\s*\n\s*\n', '', sanitized, flags=re.MULTILINE)

        # ========== 不完全なURLの修正 ==========
        # LLMが生成した不完全なURLを修正
        # 例: //sleep-quality-onsen/hakone-onsen/ → https://premium-travel-japan.com/sleep-quality-onsen/hakone-onsen/
        base_domain = 'https://premium-travel-japan.com'
        
        # パターン1: href="// で始まるURL
        sanitized = re.sub(r'href="//', f'href="{base_domain}/', sanitized)
        
        # パターン2: ](// で始まるMarkdownリンク
        sanitized = re.sub(r'\]\(//', f']({base_domain}/', sanitized)
        
        # パターン3: 行頭の // で始まるURL（リンクテキスト内）
        sanitized = re.sub(r'\(//([a-zA-Z0-9-]+)', f'({base_domain}/\\1', sanitized)
        
        # ========== プレースホルダー置換処理 ==========
        # 「〇〇」などのプレースホルダーを具体的な名前に置換
        import random
        
        # 愛犬の名前リスト
        dog_names = ['アオ', 'ラテ', 'タロウ', 'ポチ', 'モモ', 'ハナ', 'ココ', 'マロン', 'チョコ', 'ソラ']
        
        # プレースホルダーパターンと置換処理
        placeholder_patterns = [
            (r'〇〇（愛犬の名前）', lambda: random.choice(dog_names)),
            (r'○○（愛犬の名前）', lambda: random.choice(dog_names)),
            (r'〇〇\s*（愛犬）', lambda: random.choice(dog_names)),
            (r'○○\s*（愛犬）', lambda: random.choice(dog_names)),
            (r'「〇〇」', lambda: random.choice(dog_names)),
            (r'「○○」', lambda: random.choice(dog_names)),
            (r'〇〇ちゃん', lambda: random.choice(dog_names) + 'ちゃん'),
            (r'○○ちゃん', lambda: random.choice(dog_names) + 'ちゃん'),
            (r'〇〇くん', lambda: random.choice(dog_names) + 'くん'),
            (r'○○くん', lambda: random.choice(dog_names) + 'くん'),
        ]
        
        for pattern, replacement_func in placeholder_patterns:
            if re.search(pattern, sanitized):
                replacement = replacement_func()
                sanitized = re.sub(pattern, replacement, sanitized)
                print(f"  ⚠️ プレースホルダー置換: {pattern} → {replacement}")
        
        # 残った単独の〇〇や○○も置換（文脈に応じて）
        # ペット関連の文脈で出現する場合
        if re.search(r'[犬猫ペットわんこ].*〇〇|〇〇.*[犬猫ペットわんこ]', sanitized):
            sanitized = re.sub(r'〇〇', random.choice(dog_names), sanitized)
            sanitized = re.sub(r'○○', random.choice(dog_names), sanitized)
        
        # ========== 句点削除: 。」→ 」 ==========
        sanitized = sanitized.replace('。」', '」')
        sanitized = sanitized.replace('。」', '」')  # 全角も対応
        
        # ========== 会話文の改行処理 ==========
        # 「」で囲まれた会話文の前後に改行を追加
        # パターン: 文章「会話」文章 → 文章\n「会話」\n文章
        sanitized = re.sub(r'([^\n])「', r'\1\n「', sanitized)
        sanitized = re.sub(r'」([^\n])', r'」\n\1', sanitized)
        
        # 連続する改行を整理（3つ以上の改行は2つに）
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
        
        return sanitized

    def generate_page(self, page_id: int, hotel_limit: int = None) -> str:
        """
        ページ生成メイン処理
        
        page_blocksテーブルのdisplay_orderに従って動的にブロックを生成する。
        これにより、DBでページ構造を管理でき、コード変更なしに構成変更が可能。
        """
        print(f"\n{'=' * 80}")
        print(f"ページ生成開始: page_id={page_id}")
        print(f"{'=' * 80}\n")
        
        # データ取得
        page_data = self._get_page_data(page_id)
        if not page_data:
            print(f"❌ page_id={page_id}が見つかりません")
            return ""
            
        theme = self._get_theme(page_data['theme_id'])
        hotels = self._get_hotels_for_page(page_data['rakuten_area_code'], page_data['theme_id'])
        
        # ホテル数制限を適用
        if hotel_limit and hotel_limit > 0:
            hotels = hotels[:hotel_limit]
            print(f"📌 ホテル数を{hotel_limit}件に制限")
        
        author = self._get_author_info(page_data['author_id'])
        related_links = self._get_related_links(page_data)
        
        print(f"✅ ページ: {page_data['page_title']}")
        print(f"✅ テーマ: {theme['theme_title'] if theme else 'Unknown'}")
        print(f"✅ エリア: {page_data['rakuten_area_name']}")
        print(f"✅ 選定ホテル: {len(hotels)}軒")
        
        # === page_blocksテーブルからブロック構成を取得 ===
        template_name = page_data.get('page_template', 'default')
        page_blocks = self._get_page_blocks(template_name)
        
        # Markdown構築
        # 記事ヘッダー
        markdown_content = f"# {page_data['page_title']}\n\n"
        
        # プロモーション表記（小さく控えめに、記事末尾のプロフィールへの誘導）
        markdown_content += "<p class='ad-disclaimer'><small>PR | 記事末尾にライタープロフィールあり</small></p>\n\n"
        
        # === page_blocksのdisplay_orderに従ってブロックを生成 ===
        for block in page_blocks:
            block_type = block.get('block_type')
            print(f"\n📝 ブロック生成: [{block.get('display_order')}] {block_type}")
            
            if block_type == 'INTRODUCTION':
                # 導入文生成
                print(f"Generating introduction for page {page_data['id']}...")
                intro_text = self._generate_page_introduction(page_data, theme, hotels)
                markdown_content += f"{intro_text}\n\n"
                
                # meta_description生成とTiDBへの保存
                meta_description = self._generate_meta_description(page_data, theme)
                self._save_meta_description(page_id, meta_description)
                
            elif block_type == 'AREA_HIGHLIGHTS':
                # エリアの観光スポットセクションを生成
                area_name = page_data.get('rakuten_area_name', '')
                if area_name:
                    print(f"Generating area highlights for {area_name}...")
                    area_highlights = self._generate_area_highlights(area_name, theme)
                    if area_highlights:
                        markdown_content += area_highlights + "\n\n"
                        
            elif block_type == 'HOTEL_CONTENT':
                # ホテルごとのコンテンツ生成（レビューセクション含む）
                markdown_content += self._generate_all_hotel_content(hotels, theme, page_data)
                
            elif block_type == 'RELATED_LINKS':
                # 関連リンク
                if page_data.get('related_links'):
                    markdown_content += "## 関連リンク\n"
                    markdown_content += f"{page_data['related_links']}\n\n"
                    
            elif block_type == 'AUTHOR_INFO':
                # 著者プロフィール（記事末尾に配置 - 信頼性と透明性の確保）
                author = self._get_author_info(page_data.get('author_id'))
                if author:
                    markdown_content += self._generate_author_section(author)
            else:
                print(f"⚠️ 未知のブロックタイプ: {block_type}")
            
        # 最終確認: アフィリエイトIDのプレースホルダーを実際のIDに置換（二重チェック）
        markdown_content = markdown_content.replace('YOUR_AFFILIATE_ID', RAKUTEN_AFFILIATE_ID)
        
        print(f"\n✅ ページ生成完了: {len(markdown_content)}文字")
        return markdown_content

    def _generate_all_hotel_content(self, hotels: List[Dict], theme: Dict, page_data: Dict) -> str:
        """
        全ホテルのコンテンツを生成（HOTEL_CONTENTブロック）
        レビューセクションも含む
        """
        markdown_content = ""
        hotel_number = 0
        
        for i, hotel in enumerate(hotels, 1):
            print(f"Checking hotel {i}/{len(hotels)}: {hotel['hotel_name']}")
            
            hotel_special = hotel.get('hotel_special', '') or ''
            review_count = hotel.get('review_count', 0) or 0
            print(f"  ℹ️ hotel_special: {len(hotel_special)}文字, レビュー数: {review_count}件")
            
            hotel_number += 1
            print(f"Generating content for hotel {hotel_number}: {hotel['hotel_name']}")
            
            # サブタイトル（キャッチコピー）生成
            # ※レビュー取得は_generate_hotel_content内で1回のみ行う（重複防止）
            subtitle_prompt = f"""
            あなたはコピーライティングのプロです。
            以下の宿の特徴を捕らえた、魅力的で短いキャッチコピー（サブタイトル）を作成してください。
            
            # 宿情報
            宿名: {hotel['hotel_name']}
            特徴: {hotel.get('hotel_special', '')}
            ユーザー評価: {hotel.get('user_review', '')}
            
            # 要件
            - 20文字以内。
            - 宿の最大の魅力を凝縮すること。
            - 情緒的で美しい日本語を使うこと。
            - 引用符や「サブタイトル：」などの接頭辞は不要。
            """
            
            try:
                subtitle_response = self.model.generate_content(
                    subtitle_prompt,
                    generation_config={"temperature": 0.7, "max_output_tokens": 2048}
                )
                subtitle = subtitle_response.text.strip()
            except Exception as e:
                print(f"Error generating subtitle: {e}")
                subtitle = "極上の癒しと非日常の空間"

            # アフィリエイトリンク生成
            affiliate_id = RAKUTEN_AFFILIATE_ID
            hotel_no = hotel.get('hotel_no') or hotel.get('hotelNo')
            if hotel_no:
                h_url = f"https://travel.rakuten.co.jp/HOTEL/{hotel_no}/{hotel_no}.html"
            else:
                h_url = hotel.get('hotel_information_url', '')
            
            if affiliate_id and h_url:
                import urllib.parse
                encoded_url = urllib.parse.quote(h_url)
                header_affiliate_url = f"https://hb.afl.rakuten.co.jp/hgc/{affiliate_id}/?pc={encoded_url}"
            else:
                header_affiliate_url = h_url

            # ホテル見出しとサブタイトル
            markdown_content += f"## [{hotel_number}. {hotel['hotel_name']}]({header_affiliate_url})\n"
            markdown_content += f"#### {subtitle}\n\n"
            
            # 画像取得
            images = fetch_hotel_images(hotel['hotel_no'])
            if str(hotel['hotel_no']) == '153275' and images:
                if len(images) > 1:
                    images[0] = images[1]
                else:
                    images = []

            if images and should_display_image(images[0], len(images)):
                markdown_content += f"![{hotel['hotel_name']}の外観]({images[0]})\n"
                markdown_content += "<p class='image-credit'>出典：楽天トラベル</p>\n\n"
            
            # 評価情報
            markdown_content += f"<div class='review-score'>（評価: {hotel.get('review_average', '-')} / レビュー数: {hotel.get('review_count', '-')}件）</div>\n\n"

            # コンテンツ生成（レビューセクション含む）
            selected_items = theme.get('selected_items') if theme else None
            hotel_content = self._generate_hotel_content(hotel, theme or {}, selected_items, page_data)
            
            # Sanitize content
            hotel_content = self._sanitize_content(hotel_content)
            
            markdown_content += f"{hotel_content}\n\n"
            markdown_content += "---\n\n"
            
        return markdown_content

    def _generate_author_section(self, author: Dict) -> str:
        """
        著者プロフィールセクションを生成（AUTHOR_INFOブロック）
        """
        content = '''\n---\n\n<div class="author-profile">
<div class="author-box">
'''
        if author.get('author_image_url'):
            content += f"<img src=\"{author['author_image_url']}\" alt=\"{author['author_name']}\" class='author-avatar' />\n"
        content += "<div class='author-bio'>\n"
        content += "<h4>この記事を書いた人</h4>\n"
        content += f"<p class='author-name'><strong>{author['author_name']}</strong>（{author['author_title']}）</p>\n"
        if author.get('author_bio'):
            content += f"<p>{author['author_bio']}</p>\n"
        content += "</div>\n"
        content += "</div>\n"
        content += "<p class='disclosure'><small>※ 本記事はアフィリエイト広告を含みます。宿泊予約により当サイトに報酬が支払われる場合がありますが、記事内容は純粋な評価に基づいています。</small></p>\n"
        content += "</div>\n"
        return content

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LLMページ生成システム v3')
    parser.add_argument('--page-id', type=int, default=1, help='生成するページID')
    parser.add_argument('--hotel-limit', type=int, default=None, help='ホテル数の上限')
    parser.add_argument('--output', type=str, default=None, help='出力ファイルパス')
    
    args = parser.parse_args()
    
    page_id = args.page_id
    hotel_limit = args.hotel_limit
    output_path = args.output
    
    if hotel_limit:
        print(f"ホテル数を{hotel_limit}件に制限します")
    
    # インスタンス作成とページ生成
    generator = LLMPageGeneratorV3()
    markdown = generator.generate_page(page_id, hotel_limit=hotel_limit)
    
    if markdown:
        if not output_path:
            output_path = f'page_{page_id}_v3_tidb.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n✅ 生成完了: {output_path}")

if __name__ == '__main__':
    main()

