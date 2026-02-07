# BIGページ実装計画

**最終更新**: 2026年2月7日

---

## 目標

12のBIGピラーページを作成し、トピッククラスター戦略を実装してGoogleからの評価を獲得する。

---

## Phase 1: プロトタイプ作成（BH01）

### BH01: 人気温泉地ランキング

#### URL
`/onsen-ranking/`

#### ページ構成
1. **ヒーローセクション**
   - キャッチコピー: 「2026年最新版！日本全国の人気温泉地ランキング」
   - サブコピー: 「12,000軒以上の温泉旅館データから厳選」
   - ヒーロー画像: 日本の温泉風景

2. **導入文**（300-500文字）
   - 温泉地選びの重要性
   - このランキングのユニークな価値（データ駆動、最新レビュー等）
   - ページの使い方

3. **温泉地ランキング TOP 20**
   各エリアに以下を表示：
   - 順位
   - エリア名
   - 代表画像
   - 旅館数
   - 平均レビュー評価
   - 特徴（3-4行）
   - 詳細ページへのリンク

4. **選び方ガイド**（1,000文字）
   - 目的別の選び方
   - シーズン別のおすすめ
   - 予算別の選び方

5. **カテゴリ別ランキングへの誘導**
   - 露天風呂付き客室ランキング（BH03へ）
   - 高級温泉旅館ランキング（BH04へ）
   - カップル向けランキング（BH05へ）
   - など

6. **FAQ**（5-7問）
   - 「温泉地の選び方は？」
   - 「おすすめの時期は？」
   - など

7. **関連記事リンク**
   - MIDページ（地域別）へのリンク

#### ランキング基準
```sql
-- ランキング計算式（仮）
ORDER BY (
  (旅館数 * 0.2) +
  (平均レビュー評価 * 0.4) +
  (総レビュー数 * 0.3) +
  (高評価旅館率 * 0.1)
) DESC
LIMIT 20
```

#### メタデータ
- **Title**: 「人気温泉地ランキング2026【最新版】全国おすすめ温泉地TOP20」
- **Description**: 「日本全国の人気温泉地をランキング形式でご紹介。12,000軒以上の温泉旅館データと最新レビューから厳選したおすすめ温泉地TOP20。目的別・予算別の選び方も解説。」
- **Keywords**: 温泉地、ランキング、人気、おすすめ、2026

#### 構造化データ（JSON-LD）
```json
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "人気温泉地ランキング2026",
  "description": "日本全国の人気温泉地TOP20",
  "url": "https://www.premium-travel-japan.com/onsen-ranking/",
  "provider": {
    "@type": "Organization",
    "name": "Premium Travel Japan"
  },
  "hasPart": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Place",
        "name": "箱根温泉",
        "description": "..."
      }
    }
  ]
}
```

---

## データベース拡張

### 新カラム追加（page_data テーブル）

```sql
ALTER TABLE test.page_data 
ADD COLUMN page_level VARCHAR(10) DEFAULT 'LOW',
ADD COLUMN parent_page_id INT DEFAULT NULL,
ADD COLUMN category_code VARCHAR(10) DEFAULT NULL,
ADD COLUMN primary_kw VARCHAR(200) DEFAULT NULL,
ADD COLUMN must_have_sections TEXT DEFAULT NULL;
```

### BH01のマスターレコード

```sql
INSERT INTO test.page_data (
  page_id,
  page_level,
  parent_page_id,
  category_code,
  primary_kw,
  url_slug,
  page_title,
  meta_description,
  must_have_sections,
  page_template
) VALUES (
  9001,
  'BIG',
  NULL,
  'BH01',
  '温泉地 ランキング',
  '/onsen-ranking/',
  '人気温泉地ランキング2026【最新版】全国おすすめ温泉地TOP20',
  '日本全国の人気温泉地をランキング形式でご紹介。12,000軒以上の温泉旅館データと最新レビューから厳選したおすすめ温泉地TOP20。目的別・予算別の選び方も解説。',
  '["hero", "intro", "ranking", "guide", "category_links", "faq", "related_articles"]',
  'big_pillar_ranking'
);
```

---

## Next.js実装

### ファイル構成

```
app/
├── onsen-ranking/
│   └── page.tsx           # BH01のサーバーコンポーネント
├── components/
│   └── BigPillarPage/
│       ├── OnsenRanking.tsx    # BH01専用コンポーネント
│       ├── RankingList.tsx     # ランキング表示
│       ├── GuideSection.tsx    # 選び方ガイド
│       ├── CategoryLinks.tsx   # 他BIGページへのリンク
│       └── FAQ.tsx             # FAQ
```

### API エンドポイント

```
/api/big-page/onsen-ranking
  - 温泉地ランキングデータを取得
  - onsen_areas + hotels テーブルを集計
```

---

## コンテンツ生成

### Geminiプロンプト

```
【役割】
あなたは温泉旅行の専門家です。日本全国の温泉地に精通しています。

【タスク】
「人気温泉地ランキング2026」ページの以下のセクションを執筆してください。

1. 導入文（400文字）
2. 選び方ガイド（1,000文字）
   - 目的別の選び方
   - シーズン別のおすすめ
   - 予算別の選び方
3. FAQ（7問）

【トーン】
- 専門的だが親しみやすい
- データに基づいた客観的な視点
- 読者の不安を解消する

【制約】
- 事実に基づいた内容
- 具体的な数字やデータを含める
- SEOを意識したキーワード使用
```

---

## 確認項目

### 公開前チェックリスト

- [ ] ページが正しく表示される
- [ ] ランキングデータが正確
- [ ] 内部リンクが機能している
- [ ] メタデータが適切
- [ ] 構造化データが有効（検証ツールで確認）
- [ ] モバイル表示が適切
- [ ] ページ速度が良好（Lighthouse 90+）
- [ ] 誤字脱字がない

---

## 次のステップ

BH01完成後：
1. 品質レビュー
2. 残り11のBIGページに同じパターンを適用
3. MIDページ作成開始
