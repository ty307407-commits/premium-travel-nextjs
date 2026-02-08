# 次期セッションへの重要引き継ぎ事項 (HANDOVER INSTRUCTION)

**⚠️ 重要: このドキュメントは「最新かつ絶対的な正解」です。これ以前の古いスクリプトや設計（v3以前）は無視し、以下の設計に基づいて開発を進めてください。**

---

## 1. プロジェクトの核心設計（3層構造 + AI分析）

本プロジェクトは、単なるデータベースサイトではなく、**独自のAI分析に基づいた高品質な旅行メディア**です。
SEOを最大化するため、以下の**ピラミッド型 3層構造**を厳守して実装してください。

### ✅ 確定しているサイト構造
| 階層 | 役割 | URL構造 | コンテンツ内容 |
|---|---|---|---|
| **TOP** | 総合トップ | `/` | 検索機能、BIG記事へのリンク、新着情報 |
| **BIG** | 全国/広域 | `/ranking/japan-best-onsen` | 全国ランキング、季節の特集 |
| **MID** | 都道府県/エリア | `/area/gunma/kusatsu` | 温泉地トップ。LOWカテゴリへのハブページ。 |
| **LOW** | テーマ/目的 | `/theme/kusatsu/couple` | **集計ページ**。「草津でカップルにおすすめ」等。DETAILのAIスコアを集計してランキング表示。 |
| **DETAIL** | **個別旅館（最重要）** | `/hotel/shksai_nikko` | **AI要約、レーダーチャート、ポジティブ要素。** 全ての基礎データ。 |
| **LEGAL** | 法的情報 | `/about`, `/company` | 実装済み（再生成禁止） |

---

## 2. 実装済みの資産（ASSETS）

**以下のファイル・テーブルは「完成品」として扱ってください。**

### 💎 データベース（TiDB）
1.  **`hotels`**: 基本情報（ホテル名、住所、楽天基本データ）。
    *   キー: `hotel_no`, `review_url`, `onsen_id`
2.  **`hotel_review_analysis_v2`**: **【最重要】Gemini 2.0 FlashによるAI分析結果。**
    *   カラム: `hotel_id`, `analysis_json`
    *   AI分析内容:
        *   `overall_summary`: 300文字の魅力的な要約
        *   `radar_chart_data`: 5項目スコア（雰囲気, 清潔感, 泉質, 食事, 接客）
        *   `positive_keywords`: 具体的な高評価ポイント
        *   `persona_match`: カップル/家族/一人旅の適合度スコア

### 🎨 フロントエンドコンポーネント（React/Next.js）
1.  **`components/RadarChart.tsx`**: レーダーチャート表示用コンポーネント。
2.  **`app/chart-test/page.tsx`**: 実装の参考になるデモページ。

---

## 3. 次のアクション（MISSION）

**あなたの任務は、上記の資産を統合し、`DETAIL` ページを完成させ、それを `LOW` -> `MID` へと積み上げることです。**

### ⭕️ やるべきこと（Step-by-Step）

1.  **STEP 1: DETAILページ生成 (最優先)**
    *   `scripts/generate_pages_v4.py` (仮) を作成。
    *   DBの `hotel_review_analysis_v2` (JSON) を読み込む。
    *   `hotel_special` (宿の特徴) と `overall_summary` (AI要約) を組み合わせる。
    *   **レーダーチャート** は `RadarChart` コンポーネントを使用。
    *   **このページこそが「独自性の源泉」です。手抜き厳禁。**

2.  **STEP 2: LOWページ生成 (集計)**
    *   DETAILページの `persona_match` スコアを集計する。
    *   例: 「草津温泉」エリアで「カップルスコア」が高い順にランキング化 → `/theme/kusatsu/couple` ページを生成。
    *   これにより、単なる検索結果ではない「意味のあるランキング」を作る。

3.  **STEP 3: MIDページ生成 (ハブ)**
    *   そのエリアのLOWページへのリンク集を作成。

### ❌ やってはいけないこと
*   古い `generate_page.py` や `v3` 系のスクリプトを使うこと。
*   AI分析データ (`hotel_review_analysis_v2`) を使わずにページを作ること。
*   3層構造を無視して、フラットなディレクトリ構成にすること。

---

## 4. 参照すべきファイルパス
*   設計図: `.agent/MASTER_IMPLEMENTATION_PLAN.md`
*   チャート実装: `components/RadarChart.tsx`
*   口コミ分析データ源: TiDB `test.hotel_review_analysis_v2`

---
**この指示書に従い、最高品質の旅行サイトを構築してください。**
