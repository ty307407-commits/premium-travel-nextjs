#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 ホテル取得モジュール
データベースから候補ホテルを取得（Data API使用）

※ DBスキーマは docs/database_schema.md を参照
"""

import os
import base64
import requests
import mysql.connector
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# TiDB Data API設定
TIDB_API_BASE = "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint"
TIDB_API_PUBLIC_KEY = "S2R9M3V0"
TIDB_API_PRIVATE_KEY = "8cc2d2cd-7567-422a-a9d1-8a96b5643286"


class HotelFetcher:
    """ホテルデータ取得クラス（Data API + MySQL ハイブリッド）"""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self._api_auth = base64.b64encode(
            f"{TIDB_API_PUBLIC_KEY}:{TIDB_API_PRIVATE_KEY}".encode()
        ).decode()

    def _api_request(self, endpoint: str, method: str = "GET", params: dict = None) -> Optional[dict]:
        """Data API リクエスト"""
        url = f"{TIDB_API_BASE}/{endpoint}"
        headers = {
            "Authorization": f"Basic {self._api_auth}",
            "Content-Type": "application/json"
        }
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Data API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Data API request failed: {e}")
            return None

    def connect(self):
        """データベース接続（MySQL）"""
        ssl_ca = os.getenv('TIDB_SSL_CA')

        # SSL証明書が存在しない場合はSSL無効で接続試行
        connect_params = {
            'host': os.getenv('TIDB_HOST'),
            'port': int(os.getenv('TIDB_PORT', 4000)),
            'user': os.getenv('TIDB_USER'),
            'password': os.getenv('TIDB_PASSWORD'),
            'database': os.getenv('TIDB_DATABASE'),
        }

        if ssl_ca and os.path.exists(ssl_ca):
            connect_params['ssl_ca'] = ssl_ca
            connect_params['ssl_verify_cert'] = True
        else:
            # TiDB CloudはSSL必須なので、ssl_disabledは使えない
            # 代わりにシステムのCA証明書を使用
            connect_params['ssl_verify_cert'] = False
            connect_params['ssl_disabled'] = False

        try:
            self.conn = mysql.connector.connect(**connect_params)
            self.cursor = self.conn.cursor(dictionary=True)
        except Exception as e:
            print(f"MySQL connection failed: {e}")
            print("Falling back to Data API only mode")
            self.conn = None
            self.cursor = None

    def close(self):
        """接続を閉じる"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_candidate_hotels(
        self,
        area_code: str,
        theme_id: int = None,
        limit: int = 20,
        min_review_count: int = 10,
        min_review_average: float = 3.5
    ) -> List[Dict]:
        """
        候補ホテルを取得（Data API優先）

        Args:
            area_code: 楽天エリアコード
            theme_id: テーマID（キーワードフィルタ用）
            limit: 取得件数
            min_review_count: 最低レビュー数
            min_review_average: 最低評価点

        Returns:
            ホテルリスト
        """
        # Data APIでホテルを取得
        result = self._api_request("get_hotels_by_area", params={
            "area_code": area_code,
            "min_review_count": min_review_count,
            "min_review_average": min_review_average,
            "limit": limit
        })

        if result and result.get("data") and result["data"].get("rows"):
            return result["data"]["rows"]

        # MySQLフォールバック
        if not self.cursor:
            print("Warning: Neither Data API nor MySQL available for hotels")
            return []

        # テーマキーワード取得（オプション）
        keywords = []
        if theme_id:
            try:
                self.cursor.execute(
                    "SELECT hotel_search_keywords FROM themes WHERE id = %s",
                    (theme_id,)
                )
                theme_row = self.cursor.fetchone()
                if theme_row and theme_row.get('hotel_search_keywords'):
                    keywords = [k.strip() for k in theme_row['hotel_search_keywords'].split(',')]
            except Exception as e:
                print(f"Theme keywords fetch failed: {e}")

        # ホテル検索クエリ（実際のDBカラム名を使用）
        query = """
            SELECT
                hotel_no,
                hotel_name,
                hotel_special,
                user_review,
                review_average,
                review_count,
                hotel_image_url,
                room_image_url,
                address1,
                address2,
                access,
                postal_code,
                tel
            FROM hotels
            WHERE rakuten_area_code = %s
            AND review_count >= %s
            AND review_average >= %s
            AND hotel_special IS NOT NULL
            AND LENGTH(hotel_special) >= 50
        """
        params = [area_code, min_review_count, min_review_average]

        # キーワードフィルタ（オプション）
        if keywords:
            keyword_conditions = []
            for k in keywords:
                keyword_conditions.append("(hotel_name LIKE %s OR hotel_special LIKE %s)")
                params.extend([f"%{k}%", f"%{k}%"])
            query += " AND (" + " OR ".join(keyword_conditions) + ")"

        # 信頼度スコアでソート（評価 × レビュー数の重み）
        query += """
            ORDER BY
                (review_average * (1 + LOG10(GREATEST(review_count, 1)) / 3)) DESC
            LIMIT %s
        """
        params.append(limit)

        try:
            self.cursor.execute(query, tuple(params))
            hotels = self.cursor.fetchall()
            return hotels
        except Exception as e:
            print(f"Hotel fetch failed: {e}")
            return []

    def get_page_data(self, page_id: int) -> Optional[Dict]:
        """ページデータを取得（Data API使用）"""
        # Data APIでページデータを取得
        result = self._api_request("get_page_by_id", params={"page_id": page_id})

        if result and result.get("data") and result["data"].get("rows"):
            row = result["data"]["rows"][0]
            # Data APIの戻り値をマッピング
            return {
                "id": row.get("page_id"),
                "page_title": row.get("page_title", row.get("onsen_name", "")),
                "url_slug": row.get("url_slug", ""),
                "theme_id": row.get("theme_id", 1),
                "rakuten_area_code": row.get("rakuten_area_code", ""),
                "rakuten_area_name": row.get("onsen_name", ""),
                "rakuten_prefecture": row.get("prefecture", ""),
                "author_id": row.get("author_id", 1),
                "hero_image_url": row.get("hero_image_url", "")
            }

        # フォールバック: MySQLを試行
        if self.cursor:
            try:
                # 実際のテーブル名は pages
                self.cursor.execute(
                    """
                    SELECT
                        page_id as id, onsen_name as page_title, url_slug, theme_id,
                        rakuten_area_code, onsen_name as rakuten_area_name,
                        prefecture as rakuten_prefecture, 1 as author_id,
                        '' as hero_image_url
                    FROM pages
                    WHERE page_id = %s
                    """,
                    (page_id,)
                )
                return self.cursor.fetchone()
            except Exception as e:
                print(f"MySQL fallback failed: {e}")

        return None

    def get_theme_data(self, theme_id: int) -> Optional[Dict]:
        """テーマデータを取得"""
        # MySQLが利用可能な場合
        if self.cursor:
            try:
                self.cursor.execute(
                    """
                    SELECT
                        id, theme_title, theme_slug, target_audience,
                        content_tone, preferred_hotel_types,
                        hotel_search_keywords, target_keywords
                    FROM themes
                    WHERE id = %s
                    """,
                    (theme_id,)
                )
                result = self.cursor.fetchone()
                if result:
                    return result
            except Exception as e:
                print(f"Theme fetch failed: {e}")

        # Data API only モードまたはエラー時: デフォルトテーマを返す
        return {
            "id": theme_id,
            "theme_title": "露天風呂付き客室で過ごす贅沢な時間",
            "theme_slug": "rotenburo-kyakushitsu",
            "target_audience": "子育てを終え、経済的に比較的余裕のある50代の夫婦",
            "content_tone": "静かで上質、夫婦の時間を大切にする",
            "preferred_hotel_types": "高級旅館,温泉宿",
            "hotel_search_keywords": "露天風呂付き客室,貸切風呂,プライベート",
            "target_keywords": "50代夫婦,露天風呂付き客室,温泉旅行,高級旅館"
        }

    def get_hotels_by_names(self, hotel_names: List[str]) -> Dict[str, Dict]:
        """
        ホテル名リストからホテルデータを取得

        Args:
            hotel_names: ホテル名のリスト

        Returns:
            ホテル名をキーとした辞書
        """
        if not hotel_names:
            return {}

        # Data APIでホテルを取得（複数名対応）
        hotels_dict = {}
        for name in hotel_names:
            result = self._api_request("get_hotel_by_name", params={"hotel_name": name})
            if result and result.get("data") and result["data"].get("rows"):
                row = result["data"]["rows"][0]
                hotels_dict[row.get("hotel_name", name)] = row

        if hotels_dict:
            return hotels_dict

        # MySQLフォールバック
        if not self.cursor:
            print("Warning: Neither Data API nor MySQL available for hotel lookup")
            return {}

        try:
            placeholders = ', '.join(['%s'] * len(hotel_names))
            query = f"""
                SELECT
                    hotel_no,
                    hotel_name,
                    hotel_special,
                    user_review,
                    review_average,
                    review_count,
                    hotel_image_url,
                    room_image_url,
                    address1,
                    address2,
                    access,
                    tel
                FROM hotels
                WHERE hotel_name IN ({placeholders})
            """

            self.cursor.execute(query, tuple(hotel_names))
            hotels = self.cursor.fetchall()

            return {h['hotel_name']: h for h in hotels}
        except Exception as e:
            print(f"Hotels by name fetch failed: {e}")
            return {}


    def get_related_pages(self, page_id: int, theme_id: int, prefecture: str, limit: int = 5) -> List[Dict]:
        """
        関連ページを取得（同じテーマまたは同じ地域）

        Args:
            page_id: 現在のページID（除外用）
            theme_id: テーマID
            prefecture: 都道府県
            limit: 取得数

        Returns:
            関連ページリスト
        """
        # Data APIで関連ページを取得
        result = self._api_request("get_related_pages", params={
            "page_id": page_id,
            "prefecture": prefecture,
            "limit": limit
        })

        if result and result.get("data") and result["data"].get("rows"):
            return result["data"]["rows"]

        # MySQLフォールバック
        if not self.cursor:
            return []  # 関連ページは必須ではない

        try:
            # 同じテーマの他ページを優先、次に同じ都道府県
            query = """
                SELECT
                    page_id as id, onsen_name as page_title, url_slug, theme_id,
                    onsen_name as rakuten_area_name, prefecture as rakuten_prefecture,
                    '' as hero_image_url
                FROM pages
                WHERE page_id != %s
                AND prefecture = %s
                LIMIT %s
            """
            self.cursor.execute(query, (page_id, prefecture, limit))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Related pages fetch failed: {e}")
            return []

    def get_author_info(self, author_id: int) -> Optional[Dict]:
        """
        著者情報をデータベースから取得

        Args:
            author_id: 著者ID

        Returns:
            著者情報辞書
        """
        # Data APIで著者情報を取得
        result = self._api_request("get_author", params={"author_id": author_id})

        if result and result.get("data") and result["data"].get("rows"):
            return result["data"]["rows"][0]

        # MySQLフォールバック
        if not self.cursor:
            # デフォルト著者情報を返す
            return {
                "author_id": 1,
                "author_name": "温泉ライター",
                "author_name_kana": "オンセンライター",
                "author_image_url": "",
                "author_title": "温泉旅行ライター",
                "author_bio": "全国の温泉地を巡り、上質な宿をご紹介しています。",
                "specialty_region": "全国",
                "specialty_theme": "露天風呂付き客室",
                "twitter_url": "",
                "instagram_url": "",
                "author_type": "editor"
            }

        try:
            self.cursor.execute(
                """
                SELECT
                    author_id,
                    author_name,
                    author_name_kana,
                    author_image_url,
                    author_title,
                    author_bio,
                    specialty_region,
                    specialty_theme,
                    twitter_url,
                    instagram_url,
                    author_type
                FROM authors
                WHERE author_id = %s
                """,
                (author_id,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Author fetch failed: {e}")
            return None

    def get_page_blocks(self, page_id: int) -> List[Dict]:
        """
        ページブロック（地域情報など）を取得

        Args:
            page_id: ページID

        Returns:
            ページブロックリスト
        """
        # Data APIで取得を試みる
        result = self._api_request("get_page_blocks", params={"page_id": page_id})
        if result and result.get("data") and result["data"].get("rows"):
            return result["data"]["rows"]

        # MySQLフォールバック
        if not self.cursor:
            return []

        try:
            # page_blocksテーブルが存在するか確認
            self.cursor.execute("SHOW TABLES LIKE 'page_blocks'")
            if not self.cursor.fetchone():
                return []

            # カラム情報を取得
            self.cursor.execute("SHOW COLUMNS FROM page_blocks")
            columns = {row['Field']: row for row in self.cursor.fetchall()}

            # クエリを動的に構築
            select_cols = []
            if 'id' in columns:
                select_cols.append('id')
            if 'page_id' in columns:
                select_cols.append('page_id')
            if 'block_type' in columns:
                select_cols.append('block_type')
            if 'block_order' in columns:
                select_cols.append('block_order')
            if 'title' in columns:
                select_cols.append('title')
            if 'content' in columns:
                select_cols.append('content')
            if 'metadata' in columns:
                select_cols.append('metadata')

            if not select_cols:
                return []

            # page_id カラムがあるか確認
            if 'page_id' in columns:
                query = f"SELECT {', '.join(select_cols)} FROM page_blocks WHERE page_id = %s"
                if 'block_order' in columns:
                    query += " ORDER BY block_order"
                self.cursor.execute(query, (page_id,))
            else:
                # page_id カラムがない場合は全件取得を試みる
                return []

            return self.cursor.fetchall()
        except Exception as e:
            # エラー時は空を返して処理を継続
            return []

    def get_area_highlights(self, rakuten_area_code: str) -> Optional[str]:
        """
        地域のおすすめポイント（ハイライト）をonsen_areasテーブルから取得

        Args:
            rakuten_area_code: 楽天エリアコード

        Returns:
            地域のハイライト情報（テキスト）
        """
        # Data APIで取得を試みる
        result = self._api_request("get_area_highlights", params={"area_code": rakuten_area_code})
        if result and result.get("data") and result["data"].get("rows"):
            row = result["data"]["rows"][0]
            area_content = []

            if row.get('spring_quality_note'):
                area_content.append("### 温泉・泉質の特徴")
                area_content.append(row['spring_quality_note'])

            if row.get('scenic_features'):
                area_content.append("### 景観・自然の魅力")
                area_content.append(row['scenic_features'])

            if row.get('nearby_attractions'):
                area_content.append("### 周辺の観光スポット・名所")
                area_content.append(row['nearby_attractions'])

            return '\n\n'.join(area_content) if area_content else None

        # MySQLフォールバック
        if not self.cursor:
            return None

        try:
            # onsen_areasテーブルから地域情報を取得
            self.cursor.execute(
                """
                SELECT
                    scenic_features,
                    nearby_attractions,
                    spring_quality_note
                FROM onsen_areas
                WHERE rakuten_area_code = %s
                LIMIT 1
                """,
                (rakuten_area_code,)
            )
            row = self.cursor.fetchone()

            if not row:
                return None

            area_content = []

            # 泉質の特徴
            if row.get('spring_quality_note'):
                area_content.append("### 温泉・泉質の特徴")
                area_content.append(row['spring_quality_note'])

            # 景観・自然の魅力
            if row.get('scenic_features'):
                area_content.append("### 景観・自然の魅力")
                area_content.append(row['scenic_features'])

            # 周辺の観光スポット
            if row.get('nearby_attractions'):
                area_content.append("### 周辺の観光スポット・名所")
                area_content.append(row['nearby_attractions'])

            return '\n\n'.join(area_content) if area_content else None

        except Exception as e:
            # エラー時は空を返して処理を継続
            print(f"Warning: Failed to get area highlights: {e}")
            return None


def fetch_candidates_for_page(page_id: int, candidate_count: int = 20) -> tuple:
    """
    ページIDから候補ホテルを取得するヘルパー関数

    Args:
        page_id: ページID
        candidate_count: 候補数

    Returns:
        (page_data, theme_data, candidate_hotels)
    """
    fetcher = HotelFetcher()
    fetcher.connect()

    try:
        # ページデータ取得
        page_data = fetcher.get_page_data(page_id)
        if not page_data:
            raise ValueError(f"Page ID {page_id} not found")

        # テーマデータ取得
        theme_data = fetcher.get_theme_data(page_data['theme_id'])

        # 候補ホテル取得
        candidate_hotels = fetcher.get_candidate_hotels(
            area_code=page_data['rakuten_area_code'],
            theme_id=page_data['theme_id'],
            limit=candidate_count
        )

        return page_data, theme_data, candidate_hotels

    finally:
        fetcher.close()
