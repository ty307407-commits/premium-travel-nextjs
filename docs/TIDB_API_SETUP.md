# TiDB Data API に page_by_slug エンドポイントを追加する手順

## 背景

Next.jsで `/company` や `/privacy` などのページを動的に生成するため、
TiDB Data APIに新しいエンドポイントを追加する必要があります。

## 手順

### 1. TiDB Cloud Console にログイン

https://tidbcloud.com/console/clusters

### 2. Data Service に移動

左メニューから「Data Service」を選択

### 3. 既存のData Appを開く

`dataapp-pgnDYdcU` を選択

### 4. 新しいエンドポイントを作成

「Create Endpoint」をクリック

**設定値:**
- Name: `page_by_slug`
- Path: `/page_by_slug`
- Method: `GET`
- Description: `Get page data by URL slug`

### 5. SQLクエリを入力

```sql
SELECT 
  page_id,
  page_title,
  url_slug,
  meta_description,
  page_template,
  temp_full_markdown,
  created_at,
  updated_at
FROM test.page_data
WHERE url_slug = ${slug}
LIMIT 1;
```

### 6. パラメータを設定

「Parameters」タブで以下を追加:

- Name: `slug`
- Type: `STRING`
- Required: `true`
- Default: (空欄)

### 7. テスト実行

「Test」タブで以下のパラメータでテスト:

```json
{
  "slug": "/company"
}
```

期待される結果:
```json
{
  "data": {
    "columns": [...],
    "rows": [
      {
        "page_id": 9998,
        "page_title": "特定商取引法に基づく表記 | Premium Travel Japan",
        "url_slug": "/company",
        ...
      }
    ]
  }
}
```

### 8. デプロイ

「Deploy」ボタンをクリックしてエンドポイントを有効化

## 確認

curlでテスト:

```bash
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_by_slug?slug=/company" \
  -H "Authorization: Basic $(echo -n 'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286' | base64)"
```

---

## 代替方法: 既存のエンドポイントを使用

もし新しいエンドポイント作成が面倒な場合、
既存の `page_data_summary` エンドポイントを使って、
Next.js側でフィルタリングすることも可能です。

ただし、パフォーマンス的には専用エンドポイントの方が優れています。
