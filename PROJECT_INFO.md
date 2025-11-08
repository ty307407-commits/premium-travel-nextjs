# Premium Travel Japan - 技術詳細情報

**最終更新**: 2025年11月8日 08:30 JST

---

## 📦 GitHubリポジトリ情報

### このリポジトリ
- **URL**: https://github.com/ty307407-commits/premium-travel-nextjs
- **役割**: サイト作成に伴う実際のコード等の保管
- **Personal Access Token**: 環境変数 `GITHUB_TOKEN` として管理

### ドキュメント管理リポジトリ
- **URL**: https://github.com/ty307407-commits/project-document-management-system
- **役割**: 作業の引き継ぎ、進行状況の保管

---

## 🔧 技術スタック

### フロントエンド
- **React**: 19.1.1
- **TypeScript**: 5.9.3
- **Vite**: 7.1.9
- **TailwindCSS**: 4.x
- **shadcn/ui**: 最新版
- **React Router**: wouter
- **State Management**: @tanstack/react-query v5.90.7

### バックエンド
- **Node.js**: 22.13.0
- **Express**: 4.x
- **tRPC**: 11.7.1
- **Superjson**: 1.13.3（Date型のシリアライズ）

### データベース
- **PostgreSQL**: Manus提供
- **ORM**: Drizzle ORM 0.44.5
- **Migration**: drizzle-kit 0.31.4

### API統合
- **Google Sheets API**: googleapis
- **Rakuten Travel API**: REST API
- **Gemini AI**: gemini-2.0-flash-exp

---

## 🗂️ プロジェクト構造

```
premium-travel-nextjs/
├── client/                    # フロントエンド
│   ├── public/               # 静的ファイル
│   └── src/
│       ├── pages/            # ページコンポーネント
│       │   ├── Home.tsx
│       │   ├── Hakone.tsx    # 箱根ページ（実装中）
│       │   └── NotFound.tsx
│       ├── components/       # 再利用可能なコンポーネント
│       │   └── ui/          # shadcn/ui コンポーネント
│       ├── lib/             # ユーティリティ
│       │   ├── trpc.ts      # tRPCクライアント
│       │   └── trpc-provider.tsx
│       ├── App.tsx          # ルーティング
│       └── main.tsx         # エントリーポイント
│
├── server/                   # バックエンド
│   ├── _core/               # フレームワークコア
│   │   └── index.ts         # サーバーエントリーポイント
│   ├── googlesheets.ts      # Google Sheets API クライアント
│   ├── rakuten.ts           # Rakuten Travel API クライアント
│   ├── router.ts            # tRPC ルーター定義
│   ├── trpc.ts              # tRPC 初期化
│   └── db.ts                # データベース操作（予定）
│
├── drizzle/                 # データベース
│   ├── schema.ts            # スキーマ定義
│   └── migrations/          # マイグレーションファイル
│
├── shared/                  # 共有型定義
│   └── const.ts            # 共有定数
│
├── package.json            # 依存関係
├── vite.config.ts          # Vite設定
├── drizzle.config.ts       # Drizzle設定
└── tsconfig.json           # TypeScript設定
```

---

## 🔑 API認証情報

### Google Sheets API
- **認証ファイル**: `/home/ubuntu/upload/gen-lang-client-0978608719-8ac8ccf348c6.json`
- **スプレッドシートID**: `1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs`
- **シート名**:
  - `Content_Templates`: コンテンツテンプレート（43件）
  - `OnsenAreas`: 温泉地情報
  - `Themes`: テーマ情報（235件）

### Rakuten Travel API
- **エンドポイント**: `https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426`
- **環境変数**: 
  - `RAKUTEN_APPLICATION_ID`: 楽天APIアプリケーションID
  - `RAKUTEN_AFFILIATE_ID`: 楽天アフィリエイトID
- **箱根エリアコード**:
  - `largeClassCode`: `japan`
  - `middleClassCode`: `kanagawa`
  - `smallClassCode`: `hakone`

### Gemini AI
- **環境変数**: `GEMINI_API_KEY`
- **モデル**: `gemini-2.0-flash-exp`
- **レート制限**: 10リクエスト/分

---

## 📊 データベーススキーマ

### generated_contents テーブル
```typescript
export const generatedContents = mysqlTable("generated_contents", {
  id: int("id").autoincrement().primaryKey(),
  regionName: varchar("region_name", { length: 100 }).notNull(),
  themeName: varchar("theme_name", { length: 100 }).notNull(),
  hotelNo: int("hotel_no"),
  hotelName: varchar("hotel_name", { length: 200 }),
  templateId: varchar("template_id", { length: 10 }).notNull(),
  templateName: varchar("template_name", { length: 100 }).notNull(),
  content: text("content").notNull(),
  wordCount: int("word_count").notNull(),
  generatedAt: timestamp("generated_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});
```

### hotels テーブル
```typescript
export const hotels = mysqlTable("hotels", {
  id: int("id").autoincrement().primaryKey(),
  hotelNo: int("hotel_no").notNull().unique(),
  hotelName: varchar("hotel_name", { length: 200 }).notNull(),
  hotelImageUrl: varchar("hotel_image_url", { length: 500 }),
  hotelMinCharge: int("hotel_min_charge"),
  address1: varchar("address1", { length: 100 }),
  address2: varchar("address2", { length: 200 }),
  access: text("access"),
  hotelInformationUrl: varchar("hotel_information_url", { length: 500 }),
  reviewAverage: int("review_average"),
  reviewCount: int("review_count"),
  hotelSpecial: text("hotel_special"),
  regionName: varchar("region_name", { length: 100 }).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});
```

---

## 🚀 開発環境

### サーバー構成
- **バックエンド**: ポート 3000（Express + tRPC）
- **フロントエンド開発サーバー**: Vite（開発時のみ）
- **tRPCエンドポイント**: `/api/trpc`

### 環境変数（.env）
```bash
# Database
DATABASE_URL=mysql://...

# Rakuten API
RAKUTEN_APPLICATION_ID=...
RAKUTEN_AFFILIATE_ID=...

# Gemini AI
GEMINI_API_KEY=...

# Manus System (自動設定)
JWT_SECRET=...
VITE_APP_ID=...
OAUTH_SERVER_URL=...
VITE_OAUTH_PORTAL_URL=...
```

### 起動コマンド
```bash
# 依存関係インストール
pnpm install

# 開発サーバー起動（バックエンド + フロントエンド）
pnpm dev

# データベースマイグレーション
pnpm db:push

# ビルド
pnpm build

# 型チェック
pnpm check
```

---

## 🔌 tRPC API定義

### sheets ルーター
```typescript
sheets: router({
  getContentTemplates: publicProcedure.query(),
  getOnsenArea: publicProcedure
    .input(z.object({ areaCode: z.string() }))
    .query(),
  getThemes: publicProcedure.query(),
})
```

### rakuten ルーター
```typescript
rakuten: router({
  searchHotels: publicProcedure
    .input(z.object({
      largeClassCode: z.string(),
      middleClassCode: z.string(),
      smallClassCode: z.string(),
    }))
    .query(),
})
```

### フロントエンドでの使用例
```typescript
// Google Sheetsからテンプレート取得
const { data: templates } = trpc.sheets.getContentTemplates.useQuery();

// 楽天APIからホテル検索
const { data: hotels } = trpc.rakuten.searchHotels.useQuery({
  largeClassCode: 'japan',
  middleClassCode: 'kanagawa',
  smallClassCode: 'hakone',
});
```

---

## 📝 開発フェーズ

### Phase 1: Google Sheets API統合 ✅
- googleapis パッケージインストール
- `server/googlesheets.ts` 作成
- データ取得テスト成功（43 templates, 235 themes）
- **Checkpoint**: `3aaacc77`

### Phase 2: データベース設計 ✅
- PostgreSQL + Drizzle ORM
- スキーマ定義（generated_contents, hotels）
- マイグレーション実行
- **Checkpoint**: `0c6cfa75`

### Phase 3: Rakuten Travel API統合 ✅
- `server/rakuten.ts` 作成
- 箱根ホテルデータ取得成功（5件）
- **Checkpoint**: `b41bd38a`

### Phase 4: tRPCサーバーセットアップ ✅
- tRPC 11.7.1 インストール
- `server/router.ts` 作成
- フロントエンド・バックエンド型安全性確立
- **Checkpoint**: `5624f175`

### Phase 5: 箱根ページ実装（進行中）
- `client/src/pages/Hakone.tsx` 作成
- ホテル一覧表示
- 画像、価格、評価表示
- **現在**: 開発環境の修正中

### Phase 6: Gemini AI統合（未着手）
- コンテンツ生成ロジック
- テンプレートベース生成
- DB保存機能

### Phase 7: 11,800ページ自動生成（未着手）
- バッチ生成スクリプト
- 並列処理実装
- 進捗管理

### Phase 8: 本番環境デプロイ（未着手）
- ビルドテスト
- Management UI Publishボタンでデプロイ

---

## ⚠️ 既知の問題

### 1. 開発環境の構造問題
**問題**: web-static と web-db-user テンプレートの混在
**影響**: サーバーが正しく起動しない
**対策**: 現在修正中

### 2. Gemini APIレート制限
**問題**: 10リクエスト/分の制限
**影響**: 17件のコンテンツ生成に約2.5分
**対策**: 
- リトライロジック実装予定
- バッチ生成で事前にDB保存

### 3. 文字数制限の遵守
**問題**: Geminiが指定文字数を超える場合がある
**対策**:
- プロンプトで厳密な文字数指定
- 生成後に文字数チェック

---

## 🔧 トラブルシューティング

### サーバーが起動しない
```bash
# 依存関係を再インストール
rm -rf node_modules pnpm-lock.yaml
pnpm install

# .envファイルを確認
cat .env

# server/_core/index.ts の存在確認
ls -la server/_core/
```

### フロントエンドが表示されない
```bash
# ブラウザのコンソールエラーを確認
# tRPCクライアント設定を確認
cat client/src/lib/trpc-provider.tsx
```

### データベース接続エラー
```bash
# DATABASE_URL を確認
echo $DATABASE_URL

# マイグレーションを実行
pnpm db:push
```

---

## 📚 参考リンク

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Rakuten Travel API Documentation](https://webservice.rakuten.co.jp/documentation/travel-simple-hotel-search)
- [tRPC Documentation](https://trpc.io/)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)

---

## 🎯 次のステップ

1. 開発環境の修正完了
2. 箱根ページの実装完了
3. Gemini AI統合
4. 自動生成システム構築
5. 本番デプロイ

---

**作成者**: Manus AI Agent  
**最終更新**: 2025年11月8日 08:30 JST  
**次回セッション開始時**: このファイルを確認してから作業開始
