# Premium Travel Japan - TODO

## 📦 リポジトリ情報（重要！）

### ドキュメント管理リポジトリ
- URL: https://github.com/ty307407-commits/project-document-management-system.git
- ローカル: `/home/ubuntu/project-document-management-system`
- 用途: 引き継ぎ書類、分析結果、プロジェクト管理

### Webアプリケーションリポジトリ（このリポジトリ）
- URL: Manus内部リポジトリ（s3://...）
- ローカル: `/home/ubuntu/premium-travel-nextjs`
- 用途: ソースコード

---

## 🎯 現在のタスク（2025-11-08）

### Phase 1: Google Sheets統合
- [x] server/googlesheets.ts作成
- [x] googleapisパッケージインストール
- [x] 接続テスト成功（43テンプレート、箱根データ、235テーマ取得）
- [ ] tRPC procedures追加（次のPhase）
- [ ] ✅ チェックポイント作成: "Phase 1: Google Sheets API integration"

### Phase 2: Rakuten Travel API修正
- [ ] server/rakuten.ts作成（正しいエリアコード使用）
  - largeClassCode: japan
  - middleClassCode: kanagawa
  - smallClassCode: hakone
- [ ] tRPC procedures追加（rakuten.searchHotels）
- [ ] 箱根の宿5件取得テスト
- [ ] ✅ チェックポイント作成: "Phase 2: Rakuten Travel API"

### Phase 3: Rakuten tRPC統合
- [ ] routers.tsにrakuten proceduresを追加
- [ ] curlでテスト
- [ ] ✅ チェックポイント作成: "Phase 3: Rakuten tRPC procedures"

### Phase 4: 箱根ページ（最小版）
- [ ] client/src/pages/Hakone.tsx作成
- [ ] 楽天トラベルAPI統合（LLM生成なし）
- [ ] ブラウザで表示確認
- [ ] ✅ チェックポイント作成: "Phase 4: Hakone page basic layout"

### Phase 5: LLM生成統合
- [ ] server/gemini.ts作成
- [ ] Hakone.tsxにLLM生成機能追加
- [ ] コンテンツ生成テスト
- [ ] ✅ チェックポイント作成: "Phase 5: LLM content generation"

---

## 📋 完了したタスク

### 2025-11-06
- [x] PostgreSQLデータベース追加（web-db-user機能）
- [x] Drizzleスキーマ設計（generated_contents, hotels）
- [x] マイグレーション実行
- [x] tRPC procedure実装（content.save, content.get）

### 2025-11-08
- [x] PROJECT_INFO.md作成
- [x] todo.md作成
- [x] Git情報の記録

---

## 🔑 重要な情報

### Google Sheets
- スプレッドシートID: `1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs`
- 認証ファイル: `/home/ubuntu/upload/gen-lang-client-0978608719-8ac8ccf348c6.json`

### 楽天トラベルAPI
- Application ID: `1029472204308393704`
- Affiliate ID: `12426598.beaffa49.12426599.e0b47e86`

### 箱根の正しいエリアコード
- largeClassCode: `japan`
- middleClassCode: `kanagawa`
- smallClassCode: `hakone`

---

## ⚠️ 注意事項

### 各Phase完了時の手順
1. 動作確認
2. `git add . && git commit -m "Phase X complete"`
3. `webdev_save_checkpoint`
4. todo.mdのチェックボックスを更新

### ロールバック時
- 直前のチェックポイントに戻る
- todo.mdで進捗を確認
- PROJECT_INFO.mdで設定を確認

---

**最終更新: 2025-11-08 06:40 JST**
