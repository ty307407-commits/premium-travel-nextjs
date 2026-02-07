# 楽天レビュー項目を活用したランキング戦略

**作成日**: 2026年2月7日

---

## 🎯 戦略の核心

楽天トラベルAPIの**細分化されたレビュー項目**を活用して、競合が真似できない独自ランキングを作成する。

---

## 📊 楽天レビュー項目（推測）

楽天トラベルでは、通常以下のような細分化されたレビュー項目があります：

### 想定されるレビュー項目
1. **総合評価** (`review_average`)
2. **立地** (`location_average`)
3. **部屋** (`room_average`)
4. **食事** (`meal_average`)
5. **風呂** (`bath_average`)
6. **サービス** (`service_average`)
7. **設備・アメニティ** (`facility_average`)

---

## ✅ TODO: データベース確認

**まず実施すること：**

以下のSQLをTiDB Cloud Consoleで実行して、実際のカラムを確認してください：

```sql
-- hotelsテーブルの全カラムを確認
DESCRIBE test.hotels;

-- サンプルデータを1件取得
SELECT * FROM test.hotels LIMIT 1;

-- レビュー関連カラムのみを確認
SELECT 
  hotel_no,
  hotel_name,
  review_average,
  review_count
FROM test.hotels 
WHERE review_count > 50
LIMIT 5;
```

**確認してほしいこと：**
- `bath_average`, `meal_average`, `service_average` などのカラムが存在するか？
- 存在する場合、どのようなカラム名か？

---

## 🚀 レビュー項目別ランキングの実装案

### **想定される独自ランキング**

楽天のレビュー項目が利用可能な場合、以下のようなユニークなランキングを作成できます：

#### 1. **お風呂評価が高い温泉地ランキング**
```sql
SELECT 
  onsen_area,
  AVG(bath_average) as avg_bath_score,
  COUNT(*) as hotel_count
FROM hotels
WHERE bath_average IS NOT NULL
GROUP BY onsen_area
HAVING hotel_count >= 3
ORDER BY avg_bath_score DESC
LIMIT 20;
```

**狙えるキーワード:**
- 温泉 風呂 ランキング
- 温泉地 お風呂 おすすめ
- 露天風呂 評価 高い 温泉

#### 2. **料理評価が高い温泉地ランキング**
```sql
SELECT 
  onsen_area,
  AVG(meal_average) as avg_meal_score
FROM hotels
WHERE meal_average IS NOT NULL
GROUP BY onsen_area
ORDER BY avg_meal_score DESC
LIMIT 20;
```

**狙えるキーワード:**
- 温泉 料理 ランキング
- 温泉旅館 食事 美味しい
- グルメ 温泉 おすすめ

#### 3. **サービス評価が高い温泉地ランキング**
```sql
SELECT 
  onsen_area,
  AVG(service_average) as avg_service_score
FROM hotels
WHERE service_average IS NOT NULL
GROUP BY onsen_area
ORDER BY avg_service_score DESC
LIMIT 20;
```

**狙えるキーワード:**
- 温泉 おもてなし ランキング
- 温泉旅館 サービス 良い
- 接客 評価 高い 温泉

#### 4. **コスパが良い温泉地ランキング**
```sql
SELECT 
  onsen_area,
  AVG(review_average / (hotel_min_charge / 10000)) as value_score
FROM hotels
WHERE hotel_min_charge > 0 AND review_average > 4
GROUP BY onsen_area
ORDER BY value_score DESC
LIMIT 20;
```

**狙えるキーワード:**
- 温泉 コスパ ランキング
- 安い 良い 温泉
- お得 温泉旅館

---

## 📋 BH01への適用案

### **追加するセクション（レビュー項目別）**

```markdown
## レビュー項目別 温泉地ランキング

### お風呂評価が高い温泉地 TOP10
<!-- bath_average を使用 -->
<!-- "温泉 風呂 ランキング" で狙う -->

### 料理評価が高い温泉地 TOP10
<!-- meal_average を使用 -->
<!-- "温泉 料理 ランキング" で狙う -->

### サービス評価が高い温泉地 TOP10
<!-- service_average を使用 -->
<!-- "温泉 おもてなし ランキング" で狙う -->

### 立地が良い温泉地 TOP10
<!-- location_average を使用 -->
<!-- "温泉 アクセス 良い" で狙う -->

### 部屋評価が高い温泉地 TOP10
<!-- room_average を使用 -->
<!-- "温泉旅館 部屋 綺麗" で狙う -->
```

---

## 🎯 競合との差別化

### **他サイトとの違い**

| サイト | ランキング基準 | 弱点 |
|---|---|---|
| 楽天トラベル | 予約数ベース | 評価の内訳が見えない |
| じゃらん | アンケート投票 | 主観的、最新性に欠ける |
| 一休.com | 高級宿に偏る | 幅広い予算層に対応していない |
| **あなたのサイト** | **楽天の細分化レビュー** | **客観的・データドリブン・詳細** |

### **独自性のアピールポイント**

1. **データ量**: 12,000軒以上の旅館から集計
2. **客観性**: 実際の宿泊者レビューに基づく
3. **細分化**: 風呂・料理・サービスなど項目別で比較可能
4. **最新性**: 定期的に更新（毎月など）

---

## 🚀 実装ステップ

### **Phase 1: データ確認**
- [ ] hotelsテーブルのレビュー項目カラムを確認
- [ ] サンプルクエリでランキング生成をテスト

### **Phase 2: データベース拡張（必要な場合）**
- [ ] 不足しているレビュー項目カラムを追加
- [ ] 楽天APIから最新データを再取得

### **Phase 3: ランキング生成ロジック**
- [ ] 各レビュー項目別のランキング計算SQL作成
- [ ] onsen_areas テーブルとの結合
- [ ] API エンドポイント作成

### **Phase 4: BH01ページ実装**
- [ ] レビュー項目別セクションの追加
- [ ] 各ランキングの表示コンポーネント
- [ ] グラフ・チャート（視覚化）

---

## 💬 次のアクション

**ユーザーへの質問:**

1. hotelsテーブルに `bath_average`, `meal_average` などのカラムは存在しますか？
2. 存在する場合、具体的なカラム名を教えてください
3. 存在しない場合、楽天APIから取得する必要がありますか？

**回答をもとに、次のステップを決定します。**
