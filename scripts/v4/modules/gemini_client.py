#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 Gemini APIクライアント (Google AI Studio API版)

APIキー認証で長い出力に対応
"""

import os
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Google AI Studio Gemini クライアント"""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Args:
            model_name: 使用するモデル名
        """
        import google.generativeai as genai

        # APIキー認証
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY または GEMINI_API_KEY が必要です")

        genai.configure(api_key=api_key)

        # モデル設定
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 65536,  # Google AI Studio の上限
            }
        )
        print(f"✅ Google AI Studio ({model_name}): 準備完了")

    def generate(self, prompt: str) -> str:
        """
        コンテンツを生成

        Args:
            prompt: プロンプト

        Returns:
            生成されたテキスト
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini API エラー: {e}")
            raise

    def generate_article(self, prompt: str) -> dict:
        """
        記事を生成し、メタ情報を抽出

        Args:
            prompt: プロンプト

        Returns:
            {
                "content": 記事本文,
                "meta_description": メタディスクリプション,
                "seo_tags": SEOタグリスト,
                "selected_hotels": 選定されたホテル名リスト,
                "raw_output": 生の出力
            }
        """
        raw_output = self.generate(prompt)

        # メタディスクリプション抽出
        meta_description = ""
        if "【メタディスクリプション】" in raw_output:
            parts = raw_output.split("【メタディスクリプション】")
            if len(parts) > 1:
                meta_part = parts[1].split("---")[0].strip()
                meta_description = meta_part.strip()

        # SEOタグ抽出
        seo_tags = []
        if "【SEOタグ】" in raw_output:
            parts = raw_output.split("【SEOタグ】")
            if len(parts) > 1:
                tags_part = parts[1].strip()
                seo_tags = [t.strip() for t in tags_part.split(",")]

        # 選定されたホテル名を抽出
        selected_hotels = []
        hotel_pattern = r'\[HOTEL_LINK:(.+?)\]'
        matches = re.findall(hotel_pattern, raw_output)
        selected_hotels = list(dict.fromkeys(matches))  # 重複除去、順序保持

        # 記事本文（メタ情報を除去）
        content = raw_output
        if "【メタディスクリプション】" in content:
            # 「【メタディスクリプション】」の直前で分割
            content = content.split("【メタディスクリプション】")[0]
            # 末尾の「---」を削除（あれば）
            content = content.rstrip()
            if content.endswith("---"):
                content = content[:-3].rstrip()

        return {
            "content": content,
            "meta_description": meta_description,
            "seo_tags": seo_tags,
            "selected_hotels": selected_hotels,
            "raw_output": raw_output
        }


def generate_article_with_gemini(prompt: str) -> dict:
    """
    Geminiで記事を生成するヘルパー関数

    Args:
        prompt: プロンプト

    Returns:
        生成結果
    """
    client = GeminiClient()
    return client.generate_article(prompt)
