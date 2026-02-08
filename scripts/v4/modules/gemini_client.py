#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 Gemini APIクライアント (Google Gen AI SDK版)
Updated for Gemini 2.0 Flash and google-genai SDK
"""

import os
import re
from typing import Optional
from google import genai
from google.genai import types

class GeminiClient:
    """Google Gen AI SDK Gemini クライアント"""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Args:
            model_name: 使用するモデル名
        """
        # APIキーを直接指定（環境変数読み込みエラー回避のため）
        self.api_key = "AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        
        print(f"✅ Google Gen AI SDK ({model_name}): 準備完了")

    def generate(self, prompt: str) -> str:
        """
        コンテンツを生成
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=65536
                )
            )
            return response.text
        except Exception as e:
            print(f"❌ Gemini API エラー: {e}")
            raise

    def generate_article(self, prompt: str) -> dict:
        """
        記事を生成し、メタ情報を抽出
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
            content = content.split("【メタディスクリプション】")[0]
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
    client = GeminiClient()
    return client.generate_article(prompt)
