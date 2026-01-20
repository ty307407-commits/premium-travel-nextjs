# TiDB Cloud データベース情報

## 接続情報

| 項目 | 値 |
|------|-----|
| Host | gateway01.ap-northeast-1.prod.aws.tidbcloud.com |
| Port | 4000 |
| Database | test |
| Username | 4VWXcjUowH2PPCE.root |
| Password | 6KcooGBdpDcmeIGI |
| API Public Key | S2R9M3V0 |
| API Private Key | 8cc2d2cd-7567-422a-a9d1-8a96b5643286 |

## 接続文字列

```
mysql://4VWXcjUowH2PPCE.root:6KcooGBdpDcmeIGI@gateway01.ap-northeast-1.prod.aws.tidbcloud.com:4000/test
```

## データエクスポート

最新のデータは以下のファイルを参照:
- `data/active_themes.json` - 使用中テーマ一覧（91件）
- `data/tidb_export.json` - 完全エクスポート（Colabで生成時）

---

## テーブル一覧

| テーブル名 | 件数 | 説明 |
|-----------|------|------|
| age_group_colors | 4件 | 年齢グループの色設定 |
| articles | 4件 | 記事データ |
| authors | 40件 | 著者情報 |
| content_templates | 45件 | コンテンツテンプレート |
| hotels | 12,154件 | ホテル情報（楽天トラベル） |
| onsen_areas | 493件 | 温泉エリア情報 |
| page_blocks | 5件 | ページブロック |
| page_content | 0件 | ページコンテンツ |
| **page_data** | **3,831件** | ページデータ（実際のページ） |
| rakuten_area_master | 312件 | 楽天エリアマスタ |
| seo_keyword_seeds | 191件 | SEOキーワードシード |
| **themes** | **241件** | テーマ一覧（全体） |

---

## テーマ運用状況

- **themesテーブル**: 241件（全テーマ）
- **page_dataで使用中**: 91件（実際に使われているテーマ）
- **総ページ数**: 3,831件

### 使用中テーマの内訳

詳細は `data/active_themes.json` を参照

| カテゴリ | テーマ例 |
|---------|---------|
| 記念日系 | 昇進記念、転職記念、結婚記念日など |
| 健康系 | 病気回復、ダイエット成功、健康診断クリアなど |
| 美容・スパ系 | リンパマッサージ、美容・スパ特化など |
| 地域特化系 | 房総半島、紀伊半島、九州火山温泉など |
| 高級・VIP系 | 最高級旅館、VIP専用、コンシェルジュ付きなど |
| 夫婦・家族系 | 夫婦の絆、家族会議、セカンドハネムーンなど |
| シニア向け | 終活準備、健康長寿、シニア世代の安心など |

---

## テーブル構造

### themes テーブル

| カラム | 型 | 説明 |
|--------|-----|------|
| id | int(11) | 主キー |
| theme_id | varchar(50) | テーマID |
| theme_title | varchar(200) | テーマタイトル |
| category | varchar(100) | カテゴリ |
| theme_slug | varchar(100) | URLスラッグ |
| target_keywords | text | ターゲットキーワード |
| hotel_search_keywords | text | ホテル検索キーワード |
| preferred_hotel_types | text | 推奨ホテルタイプ |
| content_tone | varchar(100) | コンテンツのトーン |
| image_style | varchar(100) | 画像スタイル |
| selected_items | text | 選択アイテム |
| target_audience | varchar(100) | ターゲットオーディエンス |
| created_at | timestamp | 作成日時 |
| updated_at | timestamp | 更新日時 |
| selected_onsen | longtext | 選択温泉 |
| pickup_reason | text | ピックアップ理由 |

### page_data テーブル

| カラム | 型 | 説明 |
|--------|-----|------|
| id | int(11) | 主キー |
| page_id | int(11) | ページID |
| theme_id | int(11) | テーマID（themesとの紐付け） |
| theme_title | varchar(300) | テーマタイトル |
| region_name | varchar(200) | 地域名 |
| page_title | varchar(300) | ページタイトル |
| url_slug | varchar(500) | URLスラッグ |
| meta_description | text | メタディスクリプション |
| author_id | int(11) | 著者ID |
| rakuten_area_code | varchar(50) | 楽天エリアコード |
| rakuten_prefecture | varchar(100) | 都道府県 |
| rakuten_area_name | varchar(200) | 楽天エリア名 |
| page_template | varchar(100) | ページテンプレート |
| introduction_text | text | 導入文 |
| related_links | text | 関連リンク |
| created_at | timestamp | 作成日時 |
| updated_at | timestamp | 更新日時 |
| temp_full_markdown | longtext | 一時Markdown |
| temp_full_html | longtext | 一時HTML |
| content_generated_at | timestamp | コンテンツ生成日時 |
| image_url | varchar(500) | 画像URL |
| hero_image_url | varchar(500) | ヒーロー画像URL |

---

## Colab接続スクリプト

```python
!pip install pymysql

import pymysql
import json

CONFIG = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test',
    'ssl': {'ssl': {}}
}

connection = pymysql.connect(**CONFIG)
cursor = connection.cursor(pymysql.cursors.DictCursor)

# テーブル一覧
cursor.execute("SHOW TABLES")
for t in cursor.fetchall():
    print(list(t.values())[0])

connection.close()
```

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-20 | テーブル構造・テーマ運用状況を記録 |
| 2026-01-20 | ドキュメント作成 |
