# TiDB Data API エンドポイント追加手順

## 実行手順

### 1. TiDB Cloud Data Service にアクセス

https://tidbcloud.com/console/data-service

### 2. 既存のData Appを選択

`dataapp-pgnDYdcU` をクリック

### 3. 新しいエンドポイントを作成

「Create Endpoint」ボタンをクリック

### 4. エンドポイント設定

以下の情報を入力：

**Basic Information:**
- Name: `page_by_slug`
- Path: `/page_by_slug`
- Description: `Get page data by URL slug for legal pages`
- Request Method: `GET`

### 5. SQLクエリ

「SQL」タブで以下のクエリを入力：

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
  AND page_id >= 10000
LIMIT 1;
```

### 6. パラメータ設定

「Parameters」タブで以下を追加：

| Name | Type | Required | Default |
|------|------|----------|---------|
| slug | STRING | Yes | (空欄) |

### 7. テスト

「Test」タブで以下を実行：

**Test Parameter:**
```json
{
  "slug": "/company"
}
```

**期待される結果:**
```json
{
  "type": "sql", 
  "data": {
    "columns": [...],
    "rows": [
      {
        "page_id": 10001,
        "page_title": "特定商取引法に基づく表記 | Premium Travel Japan",
        "url_slug": "/company",
        "page_template": "legal_page",
        "temp_full_markdown": "# 特定商取引法に基づく表記\n\n...",
        ...
      }
    ]
  }
}
```

### 8. デプロイ

「Deploy」ボタンをクリックして本番環境に反映

---

## 確認

curlでテスト：

```bash
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_by_slug?slug=/company" \
  -H "Authorization: Basic $(echo -n 'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286' | base64)"
```

成功すれば、JSON形式でページデータが返ってきます。

---

## 完了後

Next.jsアプリをデプロイすれば、以下のページが動作します：
- https://www.premium-travel-japan.com/company
- https://www.premium-travel-japan.com/privacy
