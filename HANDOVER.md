# Premium Travel Japan - 引き継ぎ書類

**作成日**: 2025年11月6日  
**プロジェクト**: Premium Travel Japan（箱根×結婚5周年記念ページ + 11,800ページ自動生成システム）

---

## 📊 プロジェクト概要

### 最終目標
1. **箱根×結婚5周年記念ページの完成**（1ページの完璧な品質確立）
2. **11,800ページ自動生成システムの構築**（温泉地 × テーマの組み合わせ）

### 技術スタック
- **フロントエンド**: React 19 + Tailwind 4 + shadcn/ui
- **バックエンド**: Express 4 + tRPC 11
- **データベース**: PostgreSQL (MySQL互換 via Drizzle ORM)
- **LLM**: Gemini 2.0 Flash Exp
- **認証**: Manus OAuth
- **デプロイ**: Manus Platform

---

## 🗂️ プロジェクト構成

### 現在のプロジェクト状態

**メインプロジェクト**: `/home/ubuntu/premium-travel-nextjs`
- ✅ PostgreSQL + tRPC + 認証システム完備
- ✅ DB スキーマ設計完了
- ✅ DB 操作関数実装完了
- ✅ tRPC procedure 実装完了
- ❌ 箱根ページ未実装（明日移植予定）

**プロトタイプ**: `/home/ubuntu/premium-travel-nextjs-v2`
- ✅ 箱根ページ実装済み（Next.js 15 App Router）
- ✅ Gemini API 統合済み
- ✅ アフィリエイトコンポーネント実装済み
- ❌ DB なし（リロードで再生成される問題あり）
- **用途**: 箱根ページのコードを参照・移植する

---

## 📋 本日の作業内容（2025-11-06）

### Phase 1: Content_Templatesシート詳細分析 ✅
1. Content_Templatesシート全43件を分析
2. 必須テンプレート11件を特定
3. プレースホルダー置換ルールを理解
4. `/home/ubuntu/premium-travel-nextjs-v2/docs/content_templates_analysis.md` に記録

### Phase 2: PostgreSQLデータベース追加とスキーマ設計 ✅
1. web-db-user機能を追加
2. Drizzleスキーマ設計
   - `generated_contents` テーブル: LLM生成コンテンツを保存
   - `hotels` テーブル: 楽天トラベルAPIから取得した宿情報を保存
3. マイグレーション実行完了
4. DB操作関数実装
   - `saveGeneratedContent()`: 生成コンテンツをDBに保存
   - `getGeneratedContent()`: 特定のコンテンツを取得
   - `getAllGeneratedContentsForPage()`: ページ全体のコンテンツを取得
   - `saveHotel()`: 宿情報を保存
   - `getHotelsByRegion()`: 地域の宿一覧を取得
5. tRPC procedure実装
   - `trpc.content.save.useMutation()`: コンテンツ保存
   - `trpc.content.get.useQuery()`: コンテンツ取得
   - `trpc.content.getAll.useQuery()`: ページ全体のコンテンツ取得
   - `trpc.hotel.save.useMutation()`: 宿情報保存
   - `trpc.hotel.getByRegion.useQuery()`: 地域の宿一覧取得

---

## 🔧 データベーススキーマ

### generated_contents テーブル
```sql
CREATE TABLE generated_contents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  region_name VARCHAR(100) NOT NULL,      -- 温泉地名（例: "箱根温泉"）
  theme_name VARCHAR(100) NOT NULL,       -- テーマ名（例: "結婚5周年記念"）
  hotel_no INT,                           -- 楽天宿ID（ページレベルコンテンツはNULL）
  hotel_name VARCHAR(200),                -- 宿名（参照用）
  template_id VARCHAR(10) NOT NULL,       -- テンプレートID（例: "1", "2", "4"）
  template_name VARCHAR(100) NOT NULL,    -- テンプレート名（例: "宿見出し"）
  content TEXT NOT NULL,                  -- 生成されたテキスト
  word_count INT NOT NULL,                -- 実際の文字数
  generated_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);
```

### hotels テーブル
```sql
CREATE TABLE hotels (
  id INT AUTO_INCREMENT PRIMARY KEY,
  hotel_no INT NOT NULL UNIQUE,           -- 楽天宿ID
  hotel_name VARCHAR(200) NOT NULL,       -- 宿名
  hotel_image_url VARCHAR(500),           -- 画像URL
  hotel_min_charge INT,                   -- 最低料金
  address1 VARCHAR(100),                  -- 住所1
  address2 VARCHAR(200),                  -- 住所2
  access TEXT,                            -- アクセス情報
  hotel_information_url VARCHAR(500),     -- 詳細URL
  review_average INT,                     -- 評価平均（450 = 4.50）
  review_count INT,                       -- レビュー数
  hotel_special TEXT,                     -- 特徴
  region_name VARCHAR(100) NOT NULL,      -- 温泉地名
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);
```

---

## 📚 重要なファイル

### メインプロジェクト（/home/ubuntu/premium-travel-nextjs）

**データベース関連**:
- `drizzle/schema.ts`: DBスキーマ定義
- `server/db.ts`: DB操作関数
- `server/routers.ts`: tRPC procedure定義

**設定ファイル**:
- `drizzle.config.ts`: Drizzle ORM設定
- `vite.config.ts`: Vite設定
- `package.json`: 依存関係

**ドキュメント**:
- `todo.md`: タスク管理
- `HANDOVER.md`: この引き継ぎ書類

### プロトタイプ（/home/ubuntu/premium-travel-nextjs-v2）

**参照用コード**:
- `app/hakone/page.tsx`: 箱根ページ（Server Component）
- `app/hakone/HakoneClient-v2.tsx`: 箱根ページ（Client Component）
- `components/affiliate/*.tsx`: アフィリエイトコンポーネント（4種類）
- `lib/gemini-v2.ts`: Gemini API クライアント（リトライロジック付き）
- `app/api/generate-content-v2/route.ts`: LLM生成API

**ドキュメント**:
- `docs/content_templates_analysis.md`: Content_Templatesシート分析結果
- `docs/phase1_completion_report.md`: Phase 1完了報告

---

## 🎯 明日の作業計画

### Phase 3: 箱根ページのDB連携実装（推定時間: 2-3時間）

#### Step 1: 箱根ページの移植（60分）
1. `/home/ubuntu/premium-travel-nextjs-v2/app/hakone/` の内容を確認
2. `/home/ubuntu/premium-travel-nextjs/client/src/pages/Hakone.tsx` を作成
3. アフィリエイトコンポーネントを移植
   - `components/affiliate/AffiliateHeading.tsx`
   - `components/affiliate/AffiliateButton.tsx`
   - `components/affiliate/AffiliateClosingLink.tsx`
   - `components/affiliate/AffiliateSpecialPlanButton.tsx`
4. Gemini API クライアントを移植
   - `lib/gemini.ts`（リトライロジック付き）

#### Step 2: DB連携機能の実装（60分）
1. LLM生成 → DB保存の機能実装
   ```typescript
   // 生成後、DBに保存
   await trpc.content.save.mutate({
     regionName: "箱根温泉",
     themeName: "結婚5周年記念",
     templateId: "4",
     templateName: "導入文",
     content: generatedText,
     wordCount: generatedText.length,
   });
   ```

2. ページ表示時、DBから取得
   ```typescript
   // DBから取得（生成済みなら即表示）
   const { data: existingContent } = trpc.content.get.useQuery({
     regionName: "箱根温泉",
     themeName: "結婚5周年記念",
     templateId: "4",
   });
   ```

3. 未生成の場合のみLLM生成
   ```typescript
   if (!existingContent) {
     // Gemini APIで生成
     const generated = await generateContent(...);
     // DBに保存
     await trpc.content.save.mutate(...);
   }
   ```

#### Step 3: 11個の必須テンプレート実装（30分）
1. ページレベル（2件）
   - template_id=4: 導入文（175字）
   - template_id=11: 温泉地導入セクション（300字）

2. 宿レベル（9件 × 5宿 = 45件）
   - template_id=1: 宿見出し
   - template_id=2: おすすめポイント（125字）
   - template_id=3: 感動体験ボタン
   - template_id=5: アクセス情報（175字）
   - template_id=6: ふたりで紡ぐ、宿の記憶（400字）
   - template_id=7: 感情的クロージングリンク
   - template_id=8: 特別プランボタン
   - template_id=9: 関連温泉地リンク
   - template_id=10: 著者情報

#### Step 4: 動作確認（30分）
1. 初回アクセス: LLM生成 → DB保存
2. 2回目アクセス: DBから即座に表示（再生成なし）
3. デザイン・レイアウト確認
4. レスポンシブデザイン確認

---

## ⚠️ 既知の問題と対策

### 1. Gemini APIレート制限
**問題**: Gemini 2.0 Flash Expは10リクエスト/分の制限
**影響**: 17件のコンテンツ生成に約2.5分かかる
**対策**:
- ✅ リトライロジック実装済み（`lib/gemini-v2.ts`）
- ✅ リクエスト間隔を7秒に設定済み
- 本番環境: バッチ生成で事前にDBに保存（ユーザーは待たない）

### 2. 文字数制限の遵守
**問題**: Geminiが指定文字数を超える場合がある
**対策**:
- ✅ プロンプトで厳密な文字数指定
- ✅ 生成後に文字数チェック（±10%の範囲外で警告）
- 必要に応じて再生成

### 3. プレースホルダー置換
**問題**: Content_Templatesのプレースホルダー（{{hotel_name}}等）を正しく置換する必要がある
**対策**:
- プレースホルダーマッピングを定義
- 生成前に置換処理を実装

---

## 🚀 コマンド一覧

### 開発サーバー起動
```bash
cd /home/ubuntu/premium-travel-nextjs
pnpm dev
```

### データベースマイグレーション
```bash
cd /home/ubuntu/premium-travel-nextjs
pnpm db:push
```

### ビルド
```bash
cd /home/ubuntu/premium-travel-nextjs
pnpm build
```

### チェックポイント保存
```bash
# Manus UIから実行
# または webdev_save_checkpoint ツールを使用
```

---

## 📖 参考資料

### Content_Templatesシート
- 場所: `/home/ubuntu/project-document-management-system/data/Content_Templates.xlsx`
- 分析結果: `/home/ubuntu/premium-travel-nextjs-v2/docs/content_templates_analysis.md`

### 楽天トラベルAPI
- エリアコード: 箱根 = `hakone`
- 取得宿数: 5件（評価順）
- 参考実装: `/home/ubuntu/premium-travel-nextjs-v2/app/hakone/page.tsx`

### Gemini API
- モデル: `gemini-2.0-flash-exp`
- レート制限: 10リクエスト/分
- 参考実装: `/home/ubuntu/premium-travel-nextjs-v2/lib/gemini-v2.ts`

---

## ✅ チェックリスト（明日の作業開始前）

- [ ] `/home/ubuntu/premium-travel-nextjs` でプロジェクトを開く
- [ ] `pnpm dev` で開発サーバーを起動
- [ ] データベース接続を確認
- [ ] `/home/ubuntu/premium-travel-nextjs-v2` の箱根ページコードを確認
- [ ] この引き継ぎ書類を読み直す

---

## 💡 重要な設計判断

### なぜpremium-travel-nextjsを使うのか？
1. **Manus標準テンプレート**: 本番運用を想定した設計
2. **PostgreSQL統合**: 11,800ページのデータ永続化に必須
3. **tRPC**: 型安全なAPI通信
4. **認証システム**: 将来的な管理画面に対応

### なぜpremium-travel-nextjs-v2を破棄しないのか？
1. **参照用コード**: 箱根ページの実装が完成している
2. **アフィリエイトコンポーネント**: 4種類すべて実装済み
3. **Gemini API統合**: リトライロジック付きで安定動作
4. **Content_Templates分析**: 貴重なドキュメントが保存されている

---

## 🎯 最終ゴール

### Phase 4: 完全なページの生成とユーザー確認
- 箱根×結婚5周年記念ページの完成
- 11個の必須テンプレートすべての表示確認
- 文字数・品質の確認
- レスポンシブデザインの確認

### Phase 5: 11,800ページ生成システムの設計
- バッチ生成スクリプトの設計
- 並列処理の実装
- レート制限対策の最適化
- 進捗管理システム

### Phase 6: 最終成果物の提示
- 技術ドキュメント作成
- 運用マニュアル作成
- チェックポイント保存
- デモページ公開

---

## 📞 質問・不明点がある場合

1. `todo.md` を確認
2. `/home/ubuntu/premium-travel-nextjs-v2/docs/` のドキュメントを確認
3. この引き継ぎ書類を再読

---

**作成者**: Manus AI Agent  
**最終更新**: 2025年11月6日 10:45  
**次回作業開始**: 2025年11月7日
