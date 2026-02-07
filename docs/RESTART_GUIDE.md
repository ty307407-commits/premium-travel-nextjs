# セッション再開ガイド - 2026年2月7日

**作成日**: 2026年2月7日 13:05  
**用途**: 次回セッション開始時のクイックスタート

---

## 🎯 次回セッションで最初にやること

### **Step 1: 状況確認（5分）**

以下のドキュメントを読んでください：

1. **`docs/V4_INTEGRATION_DESIGN.md`** - V4統合設計（最重要）
2. **`docs/BH01_COMPLETE_DESIGN.md`** - BH01完全設計
3. **`docs/CURRENT_SESSION_20260207.md`** - このセッションまとめ

### **Step 2: 優先順位の確認（3分）**

実装には大きく2つのアプローチがあります：

#### **アプローチA: SEO基盤から固める**（推奨）
```
Week 1: SEO基盤
├─ E-E-A-T: 運営者情報ページ
├─ 構造化データ: JSON-LD
├─ レーダーチャート実装
└─ 目次（TOC）実装

Week 2: コンテンツ生成
├─ BH01（総合ランキング）
├─ BH01-bath（お風呂評価）
└─ DETAIL（箱根温泉）

理由: SEO基盤ができてからコンテンツを作る方が効率的
```

#### **アプローチB: プロトタイプから始める**
```
Week 1: 最小限のプロトタイプ
├─ BH01（総合ランキング）1ページのみ
└─ 基本的なSEO設定

Week 2: SEO強化
├─ レーダーチャート追加
├─ 構造化データ追加
└─ E-E-A-T追加

理由: 早く成果物を見たい場合
```

### **Step 3: 即座に決定が必要なこと**

以下を決めてください：

1. **アプローチAかB、どちらで進むか？**
2. **レーダーチャートは必須か？**（実装に時間がかかる）
3. **まず何ページ作るか？**（1ページ / 3ページ / 全部）

---

## 📊 4層構造の最終確認

```
【確定した構造】

BIG (1)
└─ /onsen-ranking/
   全国総合ランキング

MID (5)
├─ /onsen-ranking/bath-rating/        お風呂評価
├─ /onsen-ranking/meal-rating/        料理評価
├─ /onsen-ranking/service-rating/     サービス評価
├─ /onsen-ranking/room-rating/        部屋評価
└─ /onsen-ranking/equipment-rating/   設備評価

LOW (35)
├─ /onsen-ranking/bath-rating/kanto/  関東×お風呂
├─ /onsen-ranking/bath-rating/kansai/ 関西×お風呂
└─ ... (5評価 × 7地域 = 35ページ)

DETAIL (493)
├─ /onsen-ranking/detail/hakone/      箱根温泉の全28軒
├─ /onsen-ranking/detail/kusatsu/     草津温泉の全150軒
└─ ... (全493温泉地)

合計: 534ページ
```

---

## 🔧 データベース準備（未実施）

次回の最初に以下を実行：

```bash
# 方法1: Pythonスクリプト
cd /Users/rk/Library/CloudStorage/Dropbox/AI\ ブログ自動投稿プロジェクト/premium-travel-japan/scripts
python3 setup_big_pages.py

# 方法2: 手動SQL（TiDB Cloud Console）
# scripts/setup_big_pages.py の中身を確認して手動実行
```

**内容:**
1. page_dataテーブルに新カラム追加（page_level, parent_page_id, etc.）
2. BH01のマスターレコード挿入（page_id: 9001）

---

## 🎨 V4プロンプトの活用方針

### **DETAILページ（493ページ）**
- ✅ V4プロンプト改良版を使用
- ✅ 「ふたりで紡ぐ、宿の記憶」継続
- ✅ 描写スタイル継続

### **ランキングページ（BIG/MID/LOW）**
- ✅ 新プロンプト作成
- ✅ V4の描写スタイルを応用
- ✅ データドリブン + 情緒的表現

### **既存LOWページ（3,833ページ）**
- ✅ V4プロンプトそのまま継続
- ✅ 一切変更なし

---

## 🚀 次回のタスク候補

### **タスクA: SEO基盤構築**（所要時間: 3-4時間）

1. **運営者情報ページ作成**（1時間）
   ```
   app/about/page.tsx
   app/methodology/page.tsx
   ```

2. **レーダーチャート実装**（1.5時間）
   ```
   npm install react-chartjs-2 chart.js
   components/OnsenRadarChart.tsx 作成
   ```

3. **構造化データ実装**（1時間）
   ```
   JSON-LD for ItemList
   JSON-LD for FAQPage
   JSON-LD for Article
   ```

4. **目次（TOC）実装**（30分）
   ```
   components/TableOfContents.tsx 作成
   ```

### **タスクB: プロトタイプ作成**（所要時間: 4-5時間）

1. **データベースセットアップ**（30分）
2. **ランキングデータ生成**（1時間）
   ```python
   scripts/ranking/ranking_calculator.py
   ```

3. **BH01ページ実装**（2時間）
   ```typescript
   app/onsen-ranking/page.tsx
   components/RankingList.tsx
   ```

4. **コンテンツ生成**（1時間）
   ```python
   scripts/ranking/generate_ranking_page.py
   ```

5. **デプロイ & 確認**（30分）

---

## 📋 決定が必要な事項

次回セッション開始時に以下を決定：

### **1. 実装アプローチ**
- [ ] アプローチA: SEO基盤から（推奨）
- [ ] アプローチB: プロトタイプから

### **2. レーダーチャート**
- [ ] 必須で実装する
- [ ] オプション（余裕があれば）
- [ ] 見送り（後回し）

### **3. 初回実装ページ数**
- [ ] 1ページ（BH01のみ）
- [ ] 3ページ（BH01 + bath + meal）
- [ ] 全部（534ページ、自動化前提）

### **4. 運営者情報**
- [ ] 実名で作成
- [ ] ペンネームで作成
- [ ] 組織名のみ（個人名なし）

### **5. データ公開**
- [ ] CSV公開して被リンク獲得を狙う
- [ ] 見送り（リスク考慮）

---

## 💬 次回セッション開始時の質問

Claudeに以下を伝えてください：

```
docs/CURRENT_SESSION_20260207.md と 
docs/RESTART_GUIDE.md を読んでください。

次に、以下を決定したいです：
1. 実装アプローチ（AかB）
2. レーダーチャートの扱い
3. 初回実装ページ数

決定後、すぐに実装を開始します。
```

---

## 🎯 ゴール明確化

### **短期ゴール（1-2週間）**
- BH01グループ Phase 1完成（3ページ）
- SEO基盤実装完了
- Google Search Console登録

### **中期ゴール（1-2ヶ月）**
- BH01グループ Phase 2-3完成（41ページ）
- 月間1,000PV達成
- 一部キーワードでTOP30入り

### **長期ゴール（3-4ヶ月）**
- 全534ページ完成
- 月間10,000-50,000PV達成
- ロングテールキーワードでTOP10多数

---

## 📚 重要リンク

- **GitHub**: https://github.com/ty307407-commits/premium-travel-nextjs
- **本番サイト**: https://www.premium-travel-japan.com/
- **TiDB Console**: https://tidbcloud.com/console/clusters

---

**準備完了！次回のセッションを楽しみにしています！** 🚀
