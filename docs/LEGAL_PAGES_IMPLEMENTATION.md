# 法的ページ（特定商取引法・プライバシーポリシー）実装ガイド

**作成日**: 2026年2月7日  
**ステータス**: 実装準備完了

---

## 📋 **実装の全体像**

```
TiDB (page_data)
  ↓
TiDB Data API (page_by_slug)
  ↓
Next.js (LegalPage component)
  ↓
ユーザー
```

---

## ✅ **完了した作業**

### 1. SQLスクリプト作成 ✅
- ファイル: `scripts/insert_legal_pages.sql`
- 内容: 特定商取引法とプライバシーポリシーのMarkdown

### 2. Next.jsコンポーネント作成 ✅
- ファイル: `components/LegalPage.tsx`
- 機能: TiDBからMarkdownを取得してレンダリング

### 3. ページファイル作成 ✅
- `/app/company/page.tsx` - 特定商取引法
- `/app/privacy/page.tsx` - プライバシーポリシー

### 4. 依存関係確認 ✅
- `react-markdown`: インストール済み
- `remark-gfm`: インストール済み

---

## 🔧 **次に実行すること**

### **Step 1: TiDBにデータを挿入**

#### 方法A: TiDB Cloud Console（推奨）

1. https://tidbcloud.com/console/clusters にアクセス
2. クラスターを選択 → 「SQL Editor」をクリック
3. `scripts/insert_legal_pages.sql` の内容をコピー&ペースト
4. 「Run」をクリック

#### 方法B: MySQLコマンドライン

```bash
mysql -h gateway01.ap-northeast-1.prod.aws.tidbcloud.com \
  -P 4000 \
  -u 4VWXcjUowH2PPCE.root \
  -p'6KcooGBdpDcmeIGI' \
  test < scripts/insert_legal_pages.sql
```

#### 確認

```sql
SELECT page_id, page_title, url_slug
FROM test.page_data
WHERE page_id IN (9997, 9998);
```

期待される結果:
```
9998 | 特定商取引法に基づく表記 | Premium Travel Japan | /company
9997 | プライバシーポリシー | Premium Travel Japan | /privacy
```

---

### **Step 2: TiDB Data APIにエンドポイント追加**

詳細は `docs/TIDB_API_SETUP.md` を参照

**クイックガイド:**

1. https://tidbcloud.com/console/data-service にアクセス
2. `dataapp-pgnDYdcU` を選択
3. 「Create Endpoint」
4. 以下を設定:
   - Name: `page_by_slug`
   - Path: `/page_by_slug`
   - Method: `GET`
   - SQL:
     ```sql
     SELECT 
       page_id, page_title, url_slug,
       meta_description, page_template,
       temp_full_markdown,
       created_at, updated_at
     FROM test.page_data
     WHERE url_slug = ${slug}
     LIMIT 1;
     ```
   - Parameter: `slug` (STRING, required)
5. 「Deploy」

#### 確認

```bash
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_by_slug?slug=/company" \
  -H "Authorization: Basic $(echo -n 'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286' | base64)"
```

---

### **Step 3: デプロイ**

```bash
cd /Users/rk/Library/CloudStorage/Dropbox/AI\ ブログ自動投稿プロジェクト/premium-travel-japan

# 新しいブランチを作成（または既存のfeature/update-about-pageに追加）
git checkout -b feature/add-legal-pages

# ファイルを追加
git add app/company/page.tsx
git add app/privacy/page.tsx
git add components/LegalPage.tsx
git add scripts/insert_legal_pages.sql
git add docs/TIDB_API_SETUP.md

# コミット
git commit -m "feat: Add legal pages (company, privacy) with TiDB integration"

# プッシュ
git push origin feature/add-legal-pages
```

---

### **Step 4: 動作確認**

デプロイ後、以下のURLにアクセス:

- https://www.premium-travel-japan.com/company
- https://www.premium-travel-japan.com/privacy

**確認ポイント:**
- ✅ ページが正しく表示される
- ✅ Markdownが適切にレンダリングされる
- ✅ スタイリングが崩れていない
- ✅ リンク（/contact）が動作する

---

## 🎯 **今後の拡張**

### aboutページもTiDB化

```sql
INSERT INTO test.page_data (
  page_id,
  page_title,
  url_slug,
  page_template,
  temp_full_markdown,
  created_at,
  updated_at
) VALUES (
  9999,
  '編集部について | Premium Travel Japan',
  '/about',
  'about_page',
  '...(aboutページのMarkdown)...',
  NOW(),
  NOW()
);
```

### ランキングページもTiDB化

BIG/MID/LOW/DETAILの全534ページをTiDBに保存し、
Next.jsで動的生成する。

---

## ⚠️ **注意事項**

### エラーハンドリング

もし`page_by_slug`エンドポイントが作成できない場合、
`LegalPage.tsx`を以下のように修正：

```typescript
// 既存のpage_data_summaryエンドポイントを使用
async function getPageData(slug: string) {
  const apiUrl = 'https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_data_summary';
  
  const response = await fetch(apiUrl, {
    headers: {
      'Authorization': `Basic ${auth}`,
    },
    next: { revalidate: 3600 },
  });

  const data = await response.json();
  
  // クライアント側でフィルタリング
  const page = data.data.rows.find((row: any) => row.url_slug === slug);
  return page || null;
}
```

ただし、パフォーマンス的には専用エンドポイントの方が優れています。

---

## 📊 **完成後の構成**

```
Premium Travel Japan
├─ / (ホーム)
├─ /about (編集部について) ← 現在は静的、将来TiDB化
├─ /company (特定商取引法) ← TiDB化完了
├─ /privacy (プライバシーポリシー) ← TiDB化完了
├─ /contact (お問い合わせ)
└─ /onsen-ranking/ (今後実装)
    ├─ / (総合ランキング) ← TiDB化予定
    ├─ /bath-rating/ (お風呂評価) ← TiDB化予定
    └─ /detail/hakone/ (箱根温泉) ← TiDB化予定
```

---

**準備完了！TiDBにデータを挿入して、エンドポイントを作成すればすぐに動きます！** 🚀
