# 認証情報・接続情報テンプレート

**最終更新**: 2026年1月20日

> **注意**: このファイルはテンプレートです。実際の認証情報は `docs/CREDENTIALS.md`（ローカルのみ、.gitignore対象）に記載されています。

---

## 📁 GitHubリポジトリ

| リポジトリ | URL | 用途 |
|-----------|-----|------|
| premium-travel-nextjs | https://github.com/ty307407-commits/premium-travel-nextjs | コード保管 |
| project-document-management-system | https://github.com/ty307407-commits/project-document-management-system | ドキュメント管理 |
| premium-travel-v3 | https://github.com/ty307407-commits/premium-travel-v3 | 旧バージョン（参照用） |

---

## 🗄️ TiDB Cloud データベース

### MySQL直接接続（Colab等）
- Host: `gateway01.ap-northeast-1.prod.aws.tidbcloud.com`
- Port: `4000`
- Database: `test`
- Username: `[CREDENTIALS.mdを参照]`
- Password: `[CREDENTIALS.mdを参照]`

### Data API（HTTP経由 - Claude Code等）
- Base URL: `https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/`
- 認証: Basic認証（`[CREDENTIALS.mdを参照]`）

### Data APIエンドポイント一覧
| エンドポイント | メソッド | 用途 | 件数 |
|--------------|---------|------|------|
| `/active_themes` | GET | 使用中テーマ一覧 | 91件 |
| `/page_data_summary` | GET | page_data全件 | 3,831件 |
| `/tables` | GET | テーブル一覧 | 12テーブル |
| `/test` | GET | page_data件数確認 | - |

---

## 🏨 楽天トラベルAPI

- エンドポイント: `https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426`
- Application ID: `[CREDENTIALS.mdを参照]`
- Affiliate ID: `[CREDENTIALS.mdを参照]`

### 箱根エリアコード例
```
largeClassCode: japan
middleClassCode: kanagawa
smallClassCode: hakone
```

---

## 📊 Google Sheets

- スプレッドシートID: `1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs`

| シート名 | 内容 |
|---------|------|
| `Content_Templates` | コンテンツテンプレート |
| `OnsenAreas` | 温泉地情報 |
| `Themes` | テーマ情報 |

---

## 📈 データベース概要（TiDB）

| テーブル | 件数 | 用途 |
|---------|------|------|
| themes | 241件 | テーママスタ（全体） |
| page_data | 3,831件 | ページデータ（使用中テーマ91件） |
| hotels | 12,154件 | ホテル情報 |
| onsen_areas | 493件 | 温泉エリア情報 |
| authors | 40件 | 著者情報 |
| content_templates | 45件 | コンテンツテンプレート |
| rakuten_area_master | 312件 | 楽天エリアマスタ |
| seo_keyword_seeds | 191件 | SEOキーワードシード |

---

## 📝 セットアップ手順

1. `docs/CREDENTIALS.md` をローカルに作成
2. 実際の認証情報を記入
3. このファイルはGitにコミットされない（.gitignore対象）

---

## 📝 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-20 | TiDB Data API接続確立、テンプレート作成 |
