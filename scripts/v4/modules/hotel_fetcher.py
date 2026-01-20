#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 ホテル取得モジュール
データベースから候補ホテルを取得

※ DBスキーマは docs/database_schema.md を参照
"""

import os
import mysql.connector
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class HotelFetcher:
    """ホテルデータ取得クラス"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """データベース接続"""
        self.conn = mysql.connector.connect(
            host=os.getenv('TIDB_HOST'),
            port=int(os.getenv('TIDB_PORT', 4000)),
            user=os.getenv('TIDB_USER'),
            password=os.getenv('TIDB_PASSWORD'),
            database=os.getenv('TIDB_DATABASE'),
            ssl_ca=os.getenv('TIDB_SSL_CA'),
            ssl_verify_cert=True
        )
        self.cursor = self.conn.cursor(dictionary=True)

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
        候補ホテルを取得

        Args:
            area_code: 楽天エリアコード
            theme_id: テーマID（キーワードフィルタ用）
            limit: 取得件数
            min_review_count: 最低レビュー数
            min_review_average: 最低評価点

        Returns:
            ホテルリスト
        """
        # テーマキーワード取得（オプション）
        keywords = []
        if theme_id:
            self.cursor.execute(
                "SELECT hotel_search_keywords FROM themes WHERE id = %s",
                (theme_id,)
            )
            theme_row = self.cursor.fetchone()
            if theme_row and theme_row.get('hotel_search_keywords'):
                keywords = [k.strip() for k in theme_row['hotel_search_keywords'].split(',')]

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

        self.cursor.execute(query, tuple(params))
        hotels = self.cursor.fetchall()

        return hotels

    def get_page_data(self, page_id: int) -> Optional[Dict]:
        """ページデータを取得"""
        self.cursor.execute(
            """
            SELECT
                id, page_title, url_slug, theme_id,
                rakuten_area_code, rakuten_area_name,
                rakuten_prefecture, author_id,
                hero_image_url
            FROM page_data
            WHERE id = %s
            """,
            (page_id,)
        )
        return self.cursor.fetchone()

    def get_theme_data(self, theme_id: int) -> Optional[Dict]:
        """テーマデータを取得"""
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
        return self.cursor.fetchone()

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
        # 同じテーマの他ページを優先、次に同じ都道府県
        query = """
            SELECT
                id, page_title, url_slug, theme_id,
                rakuten_area_name, rakuten_prefecture,
                hero_image_url
            FROM page_data
            WHERE id != %s
            AND (theme_id = %s OR rakuten_prefecture = %s)
            ORDER BY
                CASE WHEN theme_id = %s THEN 0 ELSE 1 END,
                id
            LIMIT %s
        """
        self.cursor.execute(query, (page_id, theme_id, prefecture, theme_id, limit))
        return self.cursor.fetchall()

    def get_author_info(self, author_id: int) -> Optional[Dict]:
        """
        著者情報をデータベースから取得

        Args:
            author_id: 著者ID

        Returns:
            著者情報辞書
        """
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

    def get_page_blocks(self, page_id: int) -> List[Dict]:
        """
        ページブロック（地域情報など）を取得

        Args:
            page_id: ページID

        Returns:
            ページブロックリスト
        """
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
