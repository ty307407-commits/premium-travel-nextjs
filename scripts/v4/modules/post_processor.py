#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 後処理モジュール
プレースホルダーを実際のリンク・画像・レビューに置換
"""

import re
import os
from typing import Dict, List, Optional

class PostProcessor:
    """LLM出力の後処理を行うクラス"""

    def __init__(
        self,
        page_id: int,
        hotels_data: Dict[str, dict],
        affiliate_config: dict = None,
        author_info: dict = None,
        related_pages: List[dict] = None,
        site_base_url: str = "https://premium-onsen.com",
        hero_image_url: str = None,
        area_name: str = ""
    ):
        """
        Args:
            page_id: ページID（ヒーロー画像用）
            hotels_data: ホテル名をキーとしたホテルデータ辞書
            affiliate_config: アフィリエイト設定
            author_info: 著者情報
            related_pages: 関連ページリスト
            site_base_url: サイトのベースURL
            hero_image_url: ヒーロー画像URL（page_dataから取得）
            area_name: 温泉地名（CTAボタン用）
        """
        self.page_id = page_id
        self.hotels_data = hotels_data
        self.affiliate_config = affiliate_config or {}
        self.author_info = author_info
        self.related_pages = related_pages or []
        self.site_base_url = site_base_url
        self.hero_image_url = hero_image_url
        self.area_name = area_name

        # Cloudinary設定（ヒーロー画像用）
        self.cloudinary_base = "https://res.cloudinary.com/doj2i11km/image/upload/v1767127493/onsen/page_data"
        # Cloudflare R2設定（著者画像用）
        self.r2_base = "https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev"

    def _remove_llm_preamble(self, content: str) -> str:
        """
        LLMの前置き文を削除

        「はい、承知いたしました」などの前置きを削除し、
        「# タイトル」から始まるようにする
        """
        # 「# 」で始まる最初の見出しを探す
        lines = content.split('\n')
        start_index = 0

        for i, line in enumerate(lines):
            # Markdownの見出し1（# タイトル）を探す
            if line.strip().startswith('# ') and not line.strip().startswith('## '):
                start_index = i
                break

        # 見出しが見つかった場合、それより前を削除
        if start_index > 0:
            content = '\n'.join(lines[start_index:])

        return content

    def _remove_section_numbers(self, content: str) -> str:
        """
        不要なセクション番号を削除

        「3. 宿の紹介」などのセクション番号行を削除
        """
        lines = content.split('\n')
        filtered_lines = []

        for line in lines:
            stripped = line.strip()
            # 「数字. 〇〇」形式で、特定のキーワードを含む行をスキップ
            if stripped and len(stripped) > 2:
                if stripped[0].isdigit() and '. ' in stripped[:4]:
                    if any(keyword in stripped for keyword in ['宿の紹介', 'タイトル', '導入文', 'まとめ', 'メタディスクリプション', 'SEOタグ']):
                        continue
            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _format_dialogue_sections(self, content: str) -> str:
        """
        特定セクション（サービス、ふたりで紡ぐ、宿の記憶）の会話部分に改行を追加
        また、✅の箇条書きにも改行を追加（これは全体に適用）

        会話文（「」）の前後に適切な改行を入れ、読みやすくする
        すべての改行は<br>1つのみ
        """
        # まず全体で「。」→「」に変換（句点+閉じかっこ → 閉じかっこのみ）
        content = content.replace('。」', '」')

        # ✅の前に改行を追加（これは全体に適用）
        content = re.sub(r'(\S)\s*✅', r'\1<br>\n✅', content)

        # 会話処理は特定セクションのみに適用（物語形式のセクション）
        dialogue_sections = ['ふたりで紡ぐ', '宿の記憶']

        # セクションごとに分割して処理
        lines = content.split('\n')
        result_lines = []
        in_dialogue_section = False
        current_section_content = []

        for line in lines:
            stripped = line.strip()

            # 新しいセクション（##または###）の検出
            if stripped.startswith('## ') or stripped.startswith('### '):
                # 前のセクションを処理して追加
                if current_section_content:
                    section_text = '\n'.join(current_section_content)
                    if in_dialogue_section:
                        section_text = self._apply_dialogue_breaks(section_text)
                    result_lines.append(section_text)
                    current_section_content = []

                # このセクションが会話処理対象か判定
                in_dialogue_section = any(s in stripped for s in dialogue_sections)
                result_lines.append(line)
            else:
                current_section_content.append(line)

        # 最後のセクションを処理
        if current_section_content:
            section_text = '\n'.join(current_section_content)
            if in_dialogue_section:
                section_text = self._apply_dialogue_breaks(section_text)
            result_lines.append(section_text)

        return '\n'.join(result_lines)

    def _apply_dialogue_breaks(self, text: str) -> str:
        """会話セクション内のテキストに改行を適用"""
        # 「の前に<br>タグ（文中の場合）
        text = re.sub(r'([。、」])(\s*)「', r'\1<br>\n「', text)
        text = re.sub(r'([^\n「<])(\s*)「', r'\1<br>\n「', text)
        # 」の後に<br>タグ（次が地の文の場合）
        text = re.sub(r'」(\s*)([^」\n\s「<])', r'」<br>\n\2', text)
        # 重複する<br>タグをすべて1つに統一
        text = re.sub(r'(<br>\s*)+', '<br>\n', text)
        return text

    def _add_summary_hotel_links(self, content: str) -> str:
        """
        まとめセクション内の宿名にアフィリエイトリンクを追加し、各宿の後に改行
        """
        # まとめセクションを探す
        if '## まとめ' not in content:
            return content

        lines = content.split('\n')
        result_lines = []
        in_summary = False

        for line in lines:
            stripped = line.strip()

            # まとめセクション開始
            if '## まとめ' in stripped:
                in_summary = True
                result_lines.append(line)
                continue

            # 次のセクションでまとめ終了、または区切り線
            if in_summary and (stripped.startswith('## ') and '## まとめ' not in stripped):
                in_summary = False

            if stripped == '---':
                in_summary = False
                result_lines.append(line)
                continue

            # まとめセクション外はそのまま
            if not in_summary:
                result_lines.append(line)
                continue

            # まとめセクション内で宿名を検索してリンク化
            modified_line = line
            has_hotel = False
            for hotel_name, hotel_data in self.hotels_data.items():
                if hotel_name in modified_line:
                    has_hotel = True
                    affiliate_url = self._build_affiliate_url(hotel_data)
                    if affiliate_url:
                        # 「宿名」の形式をリンクに置換
                        modified_line = modified_line.replace(
                            f'「{hotel_name}」',
                            f'「<a href="{affiliate_url}" target="_blank" rel="noopener" style="color:#667eea;">{hotel_name}</a>」'
                        )
                        # 宿名のみの場合もリンク化（「」なし）
                        if hotel_name in modified_line and f'>{hotel_name}</a>' not in modified_line:
                            modified_line = modified_line.replace(
                                hotel_name,
                                f'<a href="{affiliate_url}" target="_blank" rel="noopener" style="color:#667eea;">{hotel_name}</a>'
                            )
                        # 宿名: 説明 の形式の場合、:の後に<br>を入れる
                        if ':' in modified_line or '：' in modified_line:
                            modified_line = modified_line.replace(': ', ':<br>\n')
                            modified_line = modified_line.replace('：', '：<br>\n')

            result_lines.append(modified_line)
            # 宿を含む行の後に空行を追加して見やすくする
            if has_hotel and stripped:
                result_lines.append('')

        return '\n'.join(result_lines)

    def process(self, content: str) -> str:
        """
        全てのプレースホルダーを処理

        Args:
            content: LLM出力のMarkdown

        Returns:
            処理後のMarkdown
        """
        # 0. LLMの前置き文を削除
        content = self._remove_llm_preamble(content)

        # 0.5. 不要なセクション番号を削除
        content = self._remove_section_numbers(content)

        # 0.6. 物語セクションの会話改行処理
        content = self._format_dialogue_sections(content)

        # 1. ヒーロー画像 + 広告表記 + 執筆者バイライン
        content = self._replace_hero_image(content)

        # 2. ホテルリンク（見出し）
        content = self._replace_hotel_links(content)

        # 3. ホテル画像
        content = self._replace_hotel_images(content)

        # 4. CTAボタン
        content = self._replace_cta_buttons(content)

        # 4.5. エリア検索CTAボタン（導入文後）
        content = self._replace_area_cta(content, self.area_name)

        # 5. アクセスリンク
        content = self._replace_access_links(content)

        # 6. レビューブロック（オプション）
        content = self._replace_review_blocks(content)

        # 7. まとめセクションの宿名にアフィリエイトリンクを追加
        content = self._add_summary_hotel_links(content)

        # 8. 関連ページセクションを追加
        content = self._add_related_pages_section(content)

        # 9. 著者情報セクションを追加（記事末尾）
        content = self._add_author_section(content)

        # 10. タイトルに宿数を追加
        content = self._update_title_with_hotel_count(content)

        return content

    def _update_title_with_hotel_count(self, content: str) -> str:
        """タイトルに宿数を追加（SEO対策）"""
        hotel_count = len(self.hotels_data)
        if hotel_count == 0:
            return content

        # タイトル行を探す（# で始まる行）
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# ') and not line.startswith('## '):
                title = line[2:].strip()
                # すでに「○選」が含まれている場合はスキップ
                if '選' in title:
                    break
                # タイトル末尾に宿数を追加
                new_title = f"# {title}【厳選{hotel_count}宿】"
                lines[i] = new_title
                break

        return '\n'.join(lines)

    def _build_header_elements(self) -> str:
        """広告表記と執筆者バイラインを構築"""
        elements = []

        # 広告表記（PR表記）- 控えめだが見える表示（1行HTMLで生成）
        ad_disclosure = '<p class="ad-disclosure" style="font-size:0.75em; color:#888; text-align:right; margin:5px 0 15px 0;"><span style="background:#f5f5f5; padding:2px 8px; border-radius:3px;">PR・広告を含みます</span></p>'
        elements.append(ad_disclosure)

        # 執筆者バイライン（上部の簡易版）（1行HTMLで生成）
        if self.author_info:
            author_name = self.author_info.get('author_name', '')
            author_title = self.author_info.get('author_title', '')
            author_id = self.author_info.get('author_id', 1)
            r2_author_id = 30120 + author_id
            author_image = f"{self.r2_base}/authors/{r2_author_id}.webp"

            byline = (
                f'<div class="author-byline" style="display:flex; align-items:center; gap:10px; margin:15px 0 25px 0; padding:10px 15px; background:#fafafa; border-radius:8px; border-left:3px solid #667eea;">'
                f'<img src="{author_image}" alt="{author_name}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;">'
                f'<div>'
                f'<span style="font-size:0.9em; color:#333; font-weight:500;">{author_title}・{author_name}</span>'
                f'<span style="font-size:0.8em; color:#666;"> が執筆</span>'
                f'</div>'
                f'</div>'
            )
            elements.append(byline)

        return '\n\n'.join(elements)

    def _replace_hero_image(self, content: str) -> str:
        """ヒーロー画像をタイトル直下に挿入（広告表記・バイライン含む）"""
        # page_dataから取得したhero_image_urlを優先使用
        if self.hero_image_url:
            hero_url = self.hero_image_url
        else:
            # フォールバック: R2から取得（page_プレフィックスなし）
            hero_url = f"{self.r2_base}/page_data/{self.page_id}.webp"

        # ヘッダー要素（広告表記 + バイライン）を構築
        header_elements = self._build_header_elements()

        # 1行のHTMLで生成（Markdownパーサーとの干渉を防ぐ）
        hero_html = (
            '\n\n'
            f'<figure class="hero-image-container" style="width:100%; margin:20px 0;">'
            f'<img src="{hero_url}" alt="記事ヒーロー画像" class="hero-image" style="width:100%; max-width:1200px; height:auto; object-fit:cover; border-radius:12px; display:block; margin:0 auto;">'
            f'</figure>'
            '\n\n'
            f'{header_elements}'
            '\n\n'
        )

        # [HERO_IMAGE]プレースホルダーがあれば置換
        if "[HERO_IMAGE]" in content:
            content = content.replace("[HERO_IMAGE]", hero_html)
        else:
            # プレースホルダーがない場合、H1タイトル直後に挿入
            lines = content.split('\n')
            new_lines = []
            h1_found = False
            for line in lines:
                new_lines.append(line)
                # H1タイトル（# で始まり ## ではない）の直後に挿入
                if not h1_found and line.strip().startswith('# ') and not line.strip().startswith('## '):
                    new_lines.append(hero_html)
                    h1_found = True
            content = '\n'.join(new_lines)

        return content

    def _replace_hotel_links(self, content: str) -> str:
        """ホテル名リンクを置換"""
        pattern = r'\[HOTEL_LINK:(.+?)\]'

        def replacer(match):
            hotel_name = match.group(1)
            hotel = self.hotels_data.get(hotel_name, {})
            affiliate_url = self._build_affiliate_url(hotel)

            if affiliate_url:
                return f'<a href="{affiliate_url}" target="_blank" rel="noopener" class="hotel-name-link">{hotel_name}</a>'
            else:
                return hotel_name

        return re.sub(pattern, replacer, content)

    def _replace_hotel_images(self, content: str) -> str:
        """ホテル画像を置換"""
        pattern = r'\[HOTEL_IMAGE:(.+?)\]'

        def replacer(match):
            hotel_name = match.group(1)
            hotel = self.hotels_data.get(hotel_name, {})
            image_url = hotel.get('hotel_image_url', '')

            if image_url:
                # 1行のHTMLで生成（Markdownパーサーとの干渉を防ぐ）
                return (
                    '\n\n'
                    f'<figure class="hotel-image" style="width:100%; max-width:800px; margin:20px auto;">'
                    f'<img src="{image_url}" alt="{hotel_name}の外観" style="width:100%; height:400px; object-fit:cover; border-radius:12px; display:block;">'
                    f'<figcaption style="text-align:center; margin-top:8px;"><small>画像提供: 楽天トラベル</small></figcaption>'
                    f'</figure>'
                    '\n\n'
                )
            else:
                return ''

        return re.sub(pattern, replacer, content)

    def _replace_cta_buttons(self, content: str) -> str:
        """CTAボタンを置換（ユーザーメリット訴求）"""
        pattern = r'\[CTA_BUTTON:(.+?)\]'

        def replacer(match):
            hotel_name = match.group(1)
            hotel = self.hotels_data.get(hotel_name, {})
            affiliate_url = self._build_affiliate_url(hotel)

            if affiliate_url:
                # 1行のHTMLで生成（Markdownパーサーとの干渉を防ぐ）
                return (
                    '\n\n'
                    f'<div class="cta-container" style="text-align:center; margin:30px 0;">'
                    f'<a href="{affiliate_url}" target="_blank" rel="noopener" class="cta-button" style="display:inline-block; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:16px 32px; border-radius:30px; text-decoration:none; font-weight:bold; font-size:1.1em; box-shadow:0 4px 15px rgba(102,126,234,0.4);">'
                    f'【楽天トラベル】空室・最安値をチェック ➜'
                    f'</a>'
                    f'</div>'
                    '\n\n'
                )
            else:
                return f'<p><strong>{hotel_name}の詳細はこちら</strong></p>'

        return re.sub(pattern, replacer, content)

    def _replace_access_links(self, content: str) -> str:
        """アクセス情報リンクを置換"""
        pattern = r'\[ACCESS_LINK:(.+?)\]'

        def replacer(match):
            hotel_name = match.group(1)
            hotel = self.hotels_data.get(hotel_name, {})
            affiliate_url = self._build_affiliate_url(hotel)

            if affiliate_url:
                return f'<a href="{affiliate_url}" target="_blank" rel="noopener" class="access-link">📍 {hotel_name}の詳細・予約はこちら</a>'
            else:
                return ''

        return re.sub(pattern, replacer, content)

    def _replace_area_cta(self, content: str, area_name: str = "") -> str:
        """導入文後のエリア検索CTAボタンを置換"""
        if '[AREA_CTA]' not in content:
            return content

        # エリア名が取得できない場合は汎用的なテキスト
        if not area_name:
            area_name = "この温泉地"

        # 楽天トラベルのエリア検索URL（露天風呂付き客室で絞り込み）
        affiliate_id = self.affiliate_config.get('affiliate_id', '')
        if affiliate_id:
            base_url = f"https://hb.afl.rakuten.co.jp/hgc/{affiliate_id}/"
        else:
            base_url = "https://travel.rakuten.co.jp/"

        cta_html = (
            '\n\n'
            '<div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%); padding:20px; border-radius:12px; margin:30px 0; text-align:center; border:1px solid #d0d8f0;">'
            f'<p style="margin:0 0 15px 0; font-size:0.95em; color:#555;">すでに{area_name}への旅行を決めている方へ</p>'
            f'<a href="{base_url}" target="_blank" rel="noopener" style="display:inline-block; background:linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); color:white; padding:14px 28px; border-radius:25px; text-decoration:none; font-weight:bold; font-size:1em; box-shadow:0 4px 12px rgba(238,90,90,0.3);">'
            f'楽天トラベルで{area_name}の露天風呂付き客室を探す →'
            '</a>'
            '</div>'
            '\n\n'
        )

        return content.replace('[AREA_CTA]', cta_html)

    def _replace_review_blocks(self, content: str) -> str:
        """レビューブロックを置換（視覚的に分離されたデザイン）"""
        pattern = r'\[REVIEW_BLOCK:(.+?)\]'

        def replacer(match):
            hotel_name = match.group(1)
            hotel = self.hotels_data.get(hotel_name, {})

            review_average = hotel.get('review_average', 0)
            review_count = hotel.get('review_count', 0)
            user_review = hotel.get('user_review', '')
            hotel_no = hotel.get('hotel_no', '')

            if review_average and review_count:
                stars = '★' * int(review_average) + '☆' * (5 - int(review_average))

                # blockquote部分を先に作成
                blockquote_html = ''
                if user_review and len(user_review) > 20:
                    # HTMLタグを除去してからテキストを切り取る（閉じタグ欠落防止）
                    clean_review = re.sub(r'<[^>]+>', '', user_review)
                    # 日時や投稿情報も除去
                    clean_review = re.sub(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}投稿.*$', '', clean_review)
                    # URL（https://...）を除去
                    clean_review = re.sub(r'https?://[^\s]+', '', clean_review)
                    # 「クチコミの詳細はこちらから」などの案内文を除去
                    clean_review = re.sub(r'(クチコミ|口コミ|レビュー)の詳細は(こちら|コチラ)から?', '', clean_review)
                    clean_review = clean_review.strip()
                    if len(clean_review) > 20:
                        excerpt = clean_review[:150] + '...' if len(clean_review) > 150 else clean_review
                        blockquote_html = f'<blockquote style="background:#fff; border-left:4px solid #f5a623; padding:15px 18px; margin:0 0 15px 0; border-radius:0 8px 8px 0; font-style:italic; color:#555; line-height:1.7;">「{excerpt}」</blockquote>'

                # レビュー全文へのアフィリエイトリンクを作成
                review_link_html = ''
                if hotel_no:
                    affiliate_id = self.affiliate_config.get('affiliate_id', '')
                    if affiliate_id:
                        review_url = f"https://hb.afl.rakuten.co.jp/hgc/{affiliate_id}/?pc=https%3A%2F%2Ftravel.rakuten.co.jp%2FHOTEL%2F{hotel_no}%2Freview.html"
                    else:
                        review_url = f"https://travel.rakuten.co.jp/HOTEL/{hotel_no}/review.html"
                    review_link_html = f'<div style="text-align:right; margin-top:10px;"><a href="{review_url}" target="_blank" rel="noopener" style="color:#667eea; font-size:0.9em; text-decoration:none;">📖 この宿のレビュー全文はこちら →</a></div>'

                # 完結したHTMLを1行で生成（Markdownパーサーとの干渉を防ぐ）
                # モバイル対応: パディングを最小限に
                review_html = (
                    '\n\n'
                    '<div class="review-block" style="background:linear-gradient(135deg, #fff9e6 0%, #fff5d6 100%); padding:15px 10px; border-radius:10px; margin:20px 0; border:1px solid #f0e6c8;">'
                    '<div style="display:flex; align-items:center; gap:8px; margin-bottom:10px; padding-bottom:10px; border-bottom:1px dashed #e8d9a8;">'
                    '<span style="font-size:1.2em;">💬</span>'
                    '<span style="font-weight:bold; color:#8b7355; font-size:0.9em;">宿泊者が語る、この宿の魅力</span>'
                    '</div>'
                    '<div style="display:flex; align-items:center; gap:6px;">'
                    f'<span style="color:#f5a623; font-size:1em; letter-spacing:1px;">{stars}</span>'
                    f'<span style="font-weight:bold; color:#333; font-size:1em;">{review_average}</span>'
                    '</div>'
                    f'<div style="color:#666; font-size:0.85em; margin-bottom:12px;">（{review_count}件のレビュー）</div>'
                    f'{blockquote_html}'
                    f'{review_link_html}'
                    '</div>'
                    '\n\n'
                )
                return review_html
            else:
                return ''

        return re.sub(pattern, replacer, content)

    def _add_related_pages_section(self, content: str) -> str:
        """関連ページセクションを追加"""
        if not self.related_pages:
            return content

        # 関連記事カードを1行HTMLで生成
        cards_html = ''
        for page in self.related_pages[:5]:  # 最大5件
            page_url = f"{self.site_base_url}/{page.get('url_slug', '')}"
            page_title = page.get('page_title', '関連記事')
            area_name = page.get('rakuten_area_name', '')
            hero_url = page.get('hero_image_url', '')

            # ヒーロー画像がない場合はR2から取得（page_プレフィックスなし）
            if not hero_url:
                hero_url = f"{self.r2_base}/page_data/{page.get('page_id', 0)}.webp"

            # 各カードを1行HTMLで生成
            cards_html += (
                f'<a href="{page_url}" class="related-page-card" style="display:block; text-decoration:none; color:inherit; border:1px solid #e0e0e0; border-radius:12px; overflow:hidden; transition:transform 0.2s, box-shadow 0.2s;">'
                f'<img src="{hero_url}" alt="{page_title}" style="width:100%; height:160px; object-fit:cover;">'
                f'<div style="padding:12px;">'
                f'<p style="font-size:0.85em; color:#666; margin:0 0 5px 0;">{area_name}</p>'
                f'<h4 style="margin:0; font-size:1em; line-height:1.4;">{page_title}</h4>'
                f'</div>'
                f'</a>'
            )

        # 関連記事セクション全体を構築
        related_html = (
            '\n\n---\n\n'
            '## 関連記事\n\n'
            '<div class="related-pages" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:20px; margin:30px 0;">'
            f'{cards_html}'
            '</div>'
            '\n\n'
        )

        # まとめセクションの後に挿入
        if "## まとめ" in content:
            # メタディスクリプションの前に挿入
            if "【メタディスクリプション】" in content:
                parts = content.split("---\n【メタディスクリプション】")
                content = parts[0] + related_html + "---\n【メタディスクリプション】" + parts[1] if len(parts) > 1 else content + related_html
            else:
                content += related_html
        else:
            content += related_html

        return content

    def _add_author_section(self, content: str) -> str:
        """著者情報セクションを追加"""
        if not self.author_info:
            return content

        author_name = self.author_info.get('author_name', '')
        author_title = self.author_info.get('author_title', '')
        author_bio = self.author_info.get('author_bio', '')
        author_id = self.author_info.get('author_id', 30121)

        # Cloudflare R2から著者画像を取得（author_id + 30120）
        r2_author_id = 30120 + author_id
        author_image = f"{self.r2_base}/authors/{r2_author_id}.webp"

        # 1行HTMLで生成（Markdownパーサーとの干渉を防ぐ）
        # レイアウト: 1行目=写真+名前・肩書き、2行目=プロフィール文（幅100%）
        author_html = (
            '\n\n---\n\n'
            '## この記事を書いた人\n\n'
            f'<div class="author-box">'
            f'<div class="author-header">'
            f'<img src="{author_image}" alt="{author_name}" class="author-image">'
            f'<div class="author-info">'
            f'<h4 class="author-name">{author_name}</h4>'
            f'<p class="author-title">{author_title}</p>'
            f'</div>'
            f'</div>'
            f'<p class="author-bio">{author_bio}</p>'
            f'</div>'
            '\n\n'
        )

        # メタディスクリプションの前に挿入
        if "【メタディスクリプション】" in content:
            parts = content.split("---\n【メタディスクリプション】")
            content = parts[0] + author_html + "---\n【メタディスクリプション】" + parts[1] if len(parts) > 1 else content + author_html
        else:
            content += author_html

        return content

    def _build_affiliate_url(self, hotel: dict) -> str:
        """アフィリエイトURLを構築"""
        hotel_no = hotel.get('hotel_no', '')
        if not hotel_no:
            return ''

        # 楽天トラベルのアフィリエイトURL構築
        # 注: 実際のアフィリエイトID設定が必要
        affiliate_id = self.affiliate_config.get('affiliate_id', '')

        if affiliate_id:
            # 正式なアフィリエイトURL
            return f"https://hb.afl.rakuten.co.jp/hgc/{affiliate_id}/?pc=https%3A%2F%2Ftravel.rakuten.co.jp%2FHOTEL%2F{hotel_no}%2F"
        else:
            # アフィリエイトID未設定時は直リンク
            return f"https://travel.rakuten.co.jp/HOTEL/{hotel_no}/"


def process_article(
    content: str,
    page_id: int,
    hotels_data: Dict[str, dict],
    affiliate_config: dict = None,
    author_info: dict = None,
    related_pages: List[dict] = None,
    site_base_url: str = "https://premium-onsen.com",
    hero_image_url: str = None
) -> str:
    """
    記事の後処理を実行するヘルパー関数

    Args:
        content: LLM出力
        page_id: ページID
        hotels_data: ホテルデータ
        affiliate_config: アフィリエイト設定
        author_info: 著者情報
        related_pages: 関連ページリスト
        site_base_url: サイトのベースURL
        hero_image_url: ヒーロー画像URL

    Returns:
        処理後の記事
    """
    processor = PostProcessor(
        page_id=page_id,
        hotels_data=hotels_data,
        affiliate_config=affiliate_config,
        author_info=author_info,
        related_pages=related_pages,
        site_base_url=site_base_url,
        hero_image_url=hero_image_url
    )
    return processor.process(content)
