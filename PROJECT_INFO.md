# Premium Travel Japan - プロジェクト情報

## 📦 リポジトリ構成

### 1. ドキュメント管理リポジトリ
```
リポジトリ: https://github.com/ty307407-commits/project-document-management-system.git
ローカルパス: /home/ubuntu/project-document-management-system
役割: プロジェクト全体のドキュメント管理
内容:
- Content_Templates.xlsx（データ）
- 分析結果ドキュメント
- 引き継ぎ書類
- プロジェクト全体の進捗管理
```

### 2. Webアプリケーションリポジトリ（このリポジトリ）
```
リポジトリ: Manus内部リポジトリ（s3://vida-prod-gitrepo/...）
ローカルパス: /home/ubuntu/premium-travel-nextjs
役割: Webアプリケーションのソースコード
内容:
- React + tRPC + PostgreSQL のコード
- DBスキーマ
- フロントエンド・バックエンド実装
```

## 🔑 重要な情報

### Google Sheets
- スプレッドシートID: `1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs`
- 認証ファイル: `/home/ubuntu/upload/gen-lang-client-0978608719-8ac8ccf348c6.json`
- シート:
  - Content_Templates: コンテンツテンプレート
  - OnsenAreas: 温泉地データ（50地域）
  - Themes: テーマデータ（236テーマ）

### 楽天トラベルAPI
- Application ID: `1029472204308393704`
- Affiliate ID: `12426598.beaffa49.12426599.e0b47e86`
- エンドポイント:
  - SimpleHotelSearch: `https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426`
  - HotelDetailSearch: `https://app.rakuten.co.jp/services/api/Travel/HotelDetailSearch/20170426`

### Gemini API
- モデル: Gemini 2.5 Flash
- 用途: LLMコンテンツ生成

## 📋 バックアップ戦略

### Phase完了時の手順

#### 1. コードリポジトリ（premium-travel-nextjs）
```bash
cd /home/ubuntu/premium-travel-nextjs
git add .
git commit -m "Phase X: [説明]"
# Manus内部リポジトリに自動保存
```

#### 2. Manusチェックポイント
```bash
# webdev_save_checkpoint tool を使用
# スナップショット + UI + 環境変数 + DB状態を保存
```

#### 3. ドキュメントリポジトリ（必要に応じて）
```bash
cd /home/ubuntu/project-document-management-system
# 引き継ぎ書類や分析結果を更新
git add .
git commit -m "Update: [説明]"
git push origin main
```

## 🎯 現在の開発フェーズ

### Phase 1: Google Sheets統合（計画中）
- [ ] server/googlesheets.ts作成
- [ ] tRPC procedures追加
- [ ] 接続テスト

### Phase 2: Rakuten Travel API修正（計画中）
- [ ] server/rakuten.ts作成（正しいエリアコード使用）
- [ ] tRPC procedures追加
- [ ] 箱根の宿5件取得テスト

### Phase 3: 箱根ページ実装（計画中）
- [ ] client/src/pages/Hakone.tsx作成
- [ ] 楽天トラベルAPI統合
- [ ] LLM生成機能追加

## 📞 参考リンク

- 開発サーバー: https://3000-i61hjmb629vuqn64ktql3-abbdbd38.manusvm.computer/
- 参考サイト: https://federatedsocialweb.net/awara-onsen/
- Google Sheets: https://docs.google.com/spreadsheets/d/1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs/edit

## 📅 更新履歴

- 2025-11-08 06:40: プロジェクト情報ファイル作成
- 2025-11-06 12:00: Phase 2完了（PostgreSQL追加）
- 2025-11-06 09:00: プロジェクト初期化

---

**このファイルは各Phase完了時に更新してください**
