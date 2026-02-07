# BH01グループ × V4プロンプト統合設計書

**最終更新**: 2026年2月7日  
**目的**: 既存V4の高品質プロンプトを新しい4層構造に統合

---

## 🎯 統合の基本方針

### **既存V4プロンプトの強み**
1. ✅ **ペルソナベース**: ターゲット読者を明確化（50代夫婦など）
2. ✅ **テーマ駆動**: 「昇進記念」「結婚記念日」など明確なテーマ
3. ✅ **高品質な文章**: 「説明ではなく描写」「情緒的な表現」
4. ✅ **ストーリーテリング**: 「ふたりで紡ぐ、宿の記憶」
5. ✅ **構造化された出力**: プレースホルダーで後処理が容易

### **新4層構造の要件**
1. ✅ **データドリブン**: 楽天レビュー項目を活用
2. ✅ **ランキング形式**: TOP20などの順位付け
3. ✅ **階層的**: BIG → MID → LOW → DETAIL
4. ✅ **検索意図対応**: ロングテールSEO

---

## 📊 4層構造とV4プロンプトの対応表

| レベル | URL例 | 生成方法 | V4要素の活用 |
|---|---|---|---|
| **BIG** | `/onsen-ranking/` | **新プロンプト**（ランキング専用） | テーマ・ペルソナの概念を応用 |
| **MID** | `/onsen-ranking/bath-rating/` | **新プロンプト**（評価項目別） | 同上 |
| **LOW** | `/onsen-ranking/bath-rating/kanto/` | **新プロンプト**（地域絞込） | 同上 |
| **DETAIL** | `/onsen-ranking/detail/hakone/` | **V4プロンプト改良版** | ✅ ほぼそのまま活用 |
| **既存LOW** | `/promotion-onsen-trip/izu-onsen/` | **V4プロンプト（既存）** | ✅ そのまま継続 |

---

## 🔧 各レベルの詳細設計

### **Level 1-3: BIG/MID/LOW（ランキングページ）**

#### プロンプト構造（新規）
```python
RANKING_PROMPT_TEMPLATE = '''
あなたの役割（ペルソナ）

あなたは、温泉旅行の専門家であり、データアナリストです。
あなたの使命は、楽天トラベルの12,000軒以上の温泉旅館データと
実際の宿泊者レビューを分析し、客観的で信頼性の高いランキング記事を作成することです。

記事の基本情報

タイトル: {page_title}
対象地域: {target_region}  # 全国 or 関東 or 関西 etc.
評価項目: {rating_category}  # お風呂 or 料理 or サービス etc.
ターゲット読者: {persona_description}  # V4から継承

【記事の構成】

## {page_title}

### 導入文（300-400文字）
- このランキングの特徴（データドリブンであること）
- なぜこの評価項目が重要か
- ターゲット読者への共感

### ランキングの基準
- データソース: 楽天トラベルの実際の宿泊者レビュー
- 評価項目: お風呂評価（5点満点）
- 集計方法: 温泉地ごとの平均値
- 信頼性: レビュー数10件以上、旅館数3軒以上

### ランキング TOP20

【各温泉地の記述項目】
#### N位: 〇〇温泉（都道府県）
**{rating_category}評価: 4.X / 5.0**

[温泉地の画像]

##### おすすめポイント
- 泉質の特徴（具体的に）
- {rating_category}の魅力（データに基づいて）
- ターゲット読者に響く理由

##### 泉質・効能
- 温泉の種類
- 主な効能

##### 代表的な旅館
- 〇〇旅館（{rating_category}評価: 4.X）
- △△ホテル（{rating_category}評価: 4.X）

👉 [詳細ページへ](/onsen-ranking/detail/{area_code}/)
👉 [関連ページ](/onsen-ranking/...)

---

### {rating_category}の選び方ガイド（800-1000文字）
※ V4の「描写」スタイルを適用

### FAQ（5-7問）

### 関連ページリンク
- 他の評価項目別ランキング
- 地域別ランキング
- テーマ別ページ

---

【メタディスクリプション】
{meta_description}

【SEOタグ】
{seo_tags}
'''
```

#### V4要素の活用ポイント
1. **ペルソナ概念**: ターゲット読者を明確化
2. **描写スタイル**: 「選び方ガイド」で情緒的な文章
3. **構造化**: マークダウン見出しで明確に
4. **SEO最適化**: タイトル・メタディスクリプション

---

### **Level 4: DETAIL（個別温泉地の宿一覧）**

#### プロンプト構造（V4改良版）
```python
DETAIL_PAGE_PROMPT = '''
あなたの役割（ペルソナ）

※ V4プロンプトとほぼ同じ

記事の基本情報

温泉地名: {onsen_area}
ターゲット読者: {persona_description}  # 可変（全年代対応）
記事のコンセプト: この温泉地の全ての宿を網羅的に紹介

【V4との違い】
- テーマ固定ではなく、温泉地固定
- 5-10軒ではなく、**その温泉地の全ての宿**を紹介
- ペルソナは「温泉地を探している全ての人」に拡大

【記事の構成】

## {onsen_area}のおすすめ温泉旅館・ホテル【全XX軒】

### 導入文
※ V4と同じスタイル: その温泉地の魅力を情緒的に

### この温泉地の魅力・おすすめポイント
※ V4と同じ

### 評価項目別ランキング（新規セクション）

#### お風呂評価が高い宿 TOP5
#### 料理評価が高い宿 TOP5
#### サービス評価が高い宿 TOP5

### 宿の紹介（全XX軒）

※ V4と完全に同じ構造:
- ## [HOTEL_LINK:宿名]
- #### ～キャッチコピー～
- おすすめポイント
- 客室露天風呂の時間
- ふたりで紡ぐ、宿の記憶
- [CTA_BUTTON:宿名]

【V4からの改良点】
1. 評価項目別ミニランキングを追加
2. 1軒しかない場合は「唯一の名宿」として格調高く紹介
3. ペルソナは柔軟に（全年代対応）
'''
```

---

## 🔄 コンテンツ生成フロー

### **Phase 1: ランキングページ生成（BIG/MID/LOW）**

```python
# scripts/generate_ranking_page.py

from modules.ranking_calculator import RankingCalculator
from modules.gemini_client import GeminiClient

def generate_ranking_page(page_level, rating_category, region=None):
    """
    ランキングページを生成
    
    Args:
        page_level: 'BIG', 'MID', 'LOW'
        rating_category: 'bath', 'meal', 'service', etc.
        region: 'kanto', 'kansai', etc. (LOWレベルのみ)
    """
    # 1. ランキングデータ計算
    calculator = RankingCalculator()
    ranking_data = calculator.calculate_ranking(
        category=rating_category,
        region=region
    )
    
    # 2. プロンプト構築（V4スタイルを応用）
    prompt = build_ranking_prompt(
        page_level=page_level,
        rating_category=rating_category,
        region=region,
        ranking_data=ranking_data,
        persona_data={
            "description": "温泉旅行を計画している全ての方",
            "keyword": "温泉好き"
        }
    )
    
    # 3. Geminiで生成
    gemini = GeminiClient()
    content = gemini.generate(prompt)
    
    # 4. 後処理（V4と同じ）
    processed_content = post_process(content)
    
    # 5. DB保存
    save_to_page_data(processed_content)
```

### **Phase 2: 詳細ページ生成（DETAIL）**

```python
# scripts/generate_detail_page.py

def generate_detail_page(onsen_area_code):
    """
    個別温泉地の詳細ページ生成（V4プロンプト改良版）
    """
    # 1. その温泉地の全宿を取得
    hotels = get_all_hotels_by_area(onsen_area_code)
    
    # 2. 評価項目別にソート
    bath_top5 = sorted(hotels, key=lambda h: h['bath_average'], reverse=True)[:5]
    meal_top5 = sorted(hotels, key=lambda h: h['meal_average'], reverse=True)[:5]
    
    # 3. V4プロンプトを改良して使用
    prompt = build_detail_prompt_v4_modified(
        onsen_area=onsen_area,
        all_hotels=hotels,
        bath_top5=bath_top5,
        meal_top5=meal_top5,
        persona_data={
            "description": "この温泉地に興味を持っている全ての方",
            "keyword": "温泉旅行者"
        }
    )
    
    # 4. Geminiで生成（V4と同じ）
    gemini = GeminiClient()
    content = gemini.generate(prompt)
    
    # 5. 後処理（V4と同じ）
    processed_content = post_process_v4(content)
    
    # 6. DB保存
    save_to_page_data(processed_content)
```

---

## 📂 ファイル構成

```
scripts/
├── v4/                          # 既存V4（そのまま維持）
│   ├── generate_article_v4.py
│   ├── prompts/
│   │   └── master_prompt.py
│   └── modules/
│
├── ranking/                     # 新規：ランキング生成
│   ├── generate_ranking_page.py
│   ├── ranking_calculator.py   # ランキング計算ロジック
│   ├── prompts/
│   │   ├── ranking_prompt.py   # ランキング用プロンプト
│   │   └── detail_prompt_v4_modified.py  # V4改良版
│   └── modules/
│       ├── gemini_client.py    # V4から共有
│       └── post_processor.py   # V4から共有
│
└── common/                      # 共通モジュール
    ├── gemini_client.py         # Gemini API クライアント
    ├── tidb_client.py           # TiDB 接続
    └── post_processor.py        # マークダウン後処理
```

---

## 🎨 V4要素の活用マトリクス

| V4の要素 | BIG/MID/LOW | DETAIL | 既存LOW |
|---|---|---|---|
| ペルソナ | ✅ 概念を応用 | ✅ 柔軟に適用 | ✅ そのまま |
| テーマ | ➖ 不使用 | ➖ 温泉地固定 | ✅ そのまま |
| 描写スタイル | ✅ ガイドで使用 | ✅ 全体で使用 | ✅ そのまま |
| ストーリー | ➖ 不使用 | ✅ 使用 | ✅ そのまま |
| プレースホルダー | ✅ 一部使用 | ✅ 同じ | ✅ そのまま |
| SEO最適化 | ✅ 強化 | ✅ 同じ | ✅ そのまま |
| 候補ホテル選定 | ➖ ランキング | ✅ 全宿 | ✅ 5-10軒 |

---

## 🚀 段階的実装プラン

### **Week 1-2: V4改良版の作成**
1. `detail_prompt_v4_modified.py` 作成
2. `generate_detail_page.py` 作成
3. 1つの温泉地でテスト（箱根など）

### **Week 3-4: ランキングプロンプト作成**
1. `ranking_prompt.py` 作成
2. `ranking_calculator.py` 作成
3. BH01（総合ランキング）でテスト

### **Week 5-6: 統合テスト**
1. BIG 1 + MID 2 + DETAIL 1 で動作確認
2. プロンプト品質の調整
3. 生成速度の最適化

### **Week 7-12: 大規模展開**
1. MID 全5ページ生成
2. LOW 35ページ生成
3. DETAIL 493ページ生成（自動化）

---

## ✅ V4プロンプトの強みを最大限活かす

### **1. "描写"スタイルの継承**
```markdown
❌ 悪い例（説明）:
「草津温泉はお風呂が良いです。泉質が優れています。」

✅ 良い例（描写 - V4スタイル）:
「湯畑から立ち上る湯けむりが、冬の冷たい空気の中で純白に輝く。
pH2.0の強酸性泉が、肌を刺すような心地よさで迎えてくれる。」
```

### **2. ストーリーテリングの活用**
DETAILページでは「ふたりで紡ぐ、宿の記憶」をそのまま継承。

### **3. 構造化された出力**
プレースホルダーによる後処理の容易さを全レベルで適用。

---

## 🎯 まとめ

### **統合のポイント**
1. ✅ **既存V4は壊さない**: 3,833ページはそのまま稼働
2. ✅ **V4の良さを継承**: 描写スタイル・ストーリー・構造化
3. ✅ **新しい用途に適応**: ランキング専用プロンプトを新規作成
4. ✅ **共通モジュール化**: Geminiクライアント等を共有

### **期待される効果**
- V4の高品質な文章を新ページにも適用
- ランキングページも情緒的で魅力的に
- 全534ページが統一された高い品質

---

## ❓ 次のステップ

1. この統合設計で進めてよろしいですか？
2. まずDETAIL用のV4改良版プロンプトを作成しますか？
3. それともランキング用の新プロンプトから始めますか？

フィードバックをお願いします！
