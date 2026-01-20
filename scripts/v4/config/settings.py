#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 生成システム設定
"""

# 画像設定
IMAGE_CONFIG = {
    "cloudflare_r2": {
        "base_url": "https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev",
        "hero_path": "page_data",
        "format": "webp"
    }
}

# アフィリエイト設定
AFFILIATE_CONFIG = {
    "rakuten": {
        "base_url": "https://hb.afl.rakuten.co.jp/hgc/",
        "affiliate_id": "12426598.beaffa49.12426599.e0b47e86",
        "tracking_id": ""
    }
}

# 宿選定設定
HOTEL_SELECTION_CONFIG = {
    "target_count": 10,      # 目標宿数
    "min_count": 5,          # 通常最小
    "absolute_min": 1,       # 絶対最小（ニッチな温泉地用）
    "candidate_count": 20,   # LLMに渡す候補数
    "min_review_count": 10,  # 最低レビュー数
    "min_review_average": 3.5  # 最低評価点
}

# プレースホルダー定義
PLACEHOLDERS = {
    "hero_image": "[HERO_IMAGE]",
    "hotel_link": "[HOTEL_LINK:{hotel_name}]",
    "hotel_image": "[HOTEL_IMAGE:{hotel_name}]",
    "cta_button": "[CTA_BUTTON:{hotel_name}]",
    "access_link": "[ACCESS_LINK:{hotel_name}]",
    "review_block": "[REVIEW_BLOCK:{hotel_name}]"
}

# CTA設定
CTA_CONFIG = {
    "button_class": "cta-button",
    "button_suffix": "の空室を見る ➜",
    "access_prefix": "📍 ",
    "access_suffix": "の詳細・予約はこちら"
}

# LLM設定
LLM_CONFIG = {
    "model": "gemini-1.5-pro",
    "temperature": 0.7,
    "max_tokens": 30000
}
