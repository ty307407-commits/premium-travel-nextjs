# セッション状態サマリー

**最終更新**: 2026年1月21日

---

## 現在の状態

### 完了したこと
- [x] mainブランチを `d376aaf` にリセット（安定版に戻した）
- [x] V4記事生成スクリプトを復元 (`scripts/v4/`)
- [x] GitHub Actions CI + Auto-merge 設定
- [x] Vercelデプロイ成功 (`premium-travel-v2`)
- [x] Colabでの記事生成動作確認済み

### 動作確認済みURL
- **プレビュー**: https://premium-travel-v2.vercel.app/preview?id=897
- **GitHub**: https://github.com/ty307407-commits/premium-travel-nextjs

---

## プロジェクト構成

```
premium-travel-nextjs/
├── api/                    # Vercel Serverless Functions
│   └── article.ts          # TiDBから記事取得API
├── client/                 # フロントエンド（Vite + React）
│   └── src/pages/
│       └── Preview.tsx     # 記事プレビューページ
├── scripts/
│   └── v4/                 # V4記事生成スクリプト（Colab用）
│       ├── generate_article_v4.py   # メインスクリプト
│       ├── modules/
│       │   ├── hotel_fetcher.py     # ホテルデータ取得
│       │   ├── gemini_client.py     # Gemini API
│       │   └── post_processor.py    # 後処理
│       ├── prompts/
│       │   └── master_prompt.py     # プロンプト生成
│       └── config/
│           └── settings.py          # 設定
├── server/                 # バックエンドサーバー
├── docs/                   # ドキュメント
│   ├── CREDENTIALS_TEMPLATE.md
│   └── SESSION_STATUS.md   # このファイル
├── vercel.json             # Vercel設定
└── .github/workflows/      # CI/CD
    ├── ci.yml              # ビルド・テスト
    └── auto-merge.yml      # 自動マージ
```

---

## 認証情報

### TiDB Database
- Host: `gateway01.ap-northeast-1.prod.aws.tidbcloud.com`
- Port: `4000`
- User: `4VWXcjUowH2PPCE.root`
- Password: `6KcooGBdpDcmeIGI`
- Database: `test`

### Gemini API
- Key: `AIzaSyDdUFyY8Rmwx2blpmd9IkK4xMNbpBCR94E`

### 楽天アフィリエイト
- Affiliate ID: `12426598.beaffa49.12426599.e0b47e86`

---

## Colabでの使い方

```python
# セットアップ
!rm -rf premium-travel-nextjs
!git clone https://github.com/ty307407-commits/premium-travel-nextjs.git
%cd premium-travel-nextjs/scripts/v4
!pip install -q python-dotenv mysql-connector-python google-generativeai

# 環境変数
import os
os.environ['TIDB_HOST'] = 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com'
os.environ['TIDB_PORT'] = '4000'
os.environ['TIDB_USER'] = '4VWXcjUowH2PPCE.root'
os.environ['TIDB_PASSWORD'] = '6KcooGBdpDcmeIGI'
os.environ['TIDB_DATABASE'] = 'test'
os.environ['GEMINI_API_KEY'] = 'AIzaSyDdUFyY8Rmwx2blpmd9IkK4xMNbpBCR94E'
os.environ['RAKUTEN_AFFILIATE_ID'] = '12426598.beaffa49.12426599.e0b47e86'

# 記事生成
from generate_article_v4 import ArticleGeneratorV4
generator = ArticleGeneratorV4()
result = generator.generate_for_page(page_id=897)
```

---

## 次のタスク（未完了）

1. **Next.js への移行**
   - 現在: Vite + React (SPA)
   - 目標: Next.js App Router (SSG/SSR)
   - 理由: SEO対応、静的生成、パフォーマンス向上

2. **URL Slug対応**
   - 現在: `/preview?id=897`
   - 目標: `/area/izu-kogen/theme-name` のようなSEOフレンドリーURL

3. **一括記事生成**
   - Colabで複数ページを一括生成
   - TiDBに保存

---

## データベース概要

| テーブル | 件数 | 用途 |
|---------|------|------|
| page_data | 3,831件 | ページメタデータ |
| themes | 241件 | テーママスタ |
| hotels | 12,154件 | ホテル情報 |
| onsen_areas | 493件 | 温泉エリア情報 |
| articles | 生成記事 | 生成された記事本文 |
| authors | 40件 | 著者情報 |

---

## 明日のセッション開始時

以下のファイルを読むよう指示してください：

```
docs/SESSION_STATUS.md を読んで、前回の状態を把握してください。
```

これで全ての情報が分かります。
