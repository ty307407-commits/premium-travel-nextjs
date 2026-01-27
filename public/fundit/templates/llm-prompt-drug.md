# LLM記事生成プロンプト：薬紹介ページ

以下のプロンプトをLLM（ChatGPT、Claude等）にコピペして使用してください。

---

## 基本プロンプト

```
あなたは医療ライターです。以下の薬について、WordPress用の記事コンテンツを生成してください。

【対象の薬】
薬名：{{DRUG_NAME}}

【出力形式】
JSON形式で出力してください。出力後、そのJSONを使ってHTMLを生成します。

【JSON構造】
{
  "drug_name": "薬の正式名称",
  "drug_name_kana": "やくのせいしきめいしょう",
  "symptom": "対象となる症状・疾患",
  "category": "カテゴリ（例：ステロイド外用薬、鎮痛剤など）",

  "catch_copy": {
    "main": "メインキャッチコピー（20文字以内）",
    "sub": "サブキャッチコピー（40文字以内）"
  },

  "intro": "導入文（100-150文字）",

  "benefit_list": [
    "メリット1",
    "メリット2",
    "メリット3",
    "メリット4"
  ],

  "problem_list": [
    {
      "problem": "よくある悩み・問題",
      "solution": "この薬での解決方法"
    }
  ],

  "doctor_comment": {
    "name": "鍵野 太郎",
    "title": "QBCスキンクリニック院長",
    "credential": "皮膚科専門医・医学博士",
    "image_url": "https://pub-72bbcf8e61fe4f5c89e5b1d0b6409eae.r2.dev/hospital_director_kagino.webp",
    "comments": [
      {
        "context": "コメントを入れる文脈（例：使用上の注意点について）",
        "text": "医師としてのコメント（100-200文字）"
      },
      {
        "context": "別の文脈",
        "text": "別のコメント"
      }
    ]
  },

  "drug_info": {
    "ingredient": "主成分名",
    "ingredient_detail": "成分についての詳細説明",
    "effect": "効果・効能の説明",
    "mechanism": "作用機序の説明",
    "strength_rank": "薬の強さランク（該当する場合）",
    "dosage_form": "剤形（軟膏、クリーム、錠剤など）"
  },

  "usage": {
    "basic": "基本的な使い方",
    "frequency": "使用頻度",
    "duration": "使用期間の目安",
    "precautions": [
      "使用上の注意点1",
      "使用上の注意点2"
    ]
  },

  "flow_steps": [
    {
      "step": 1,
      "title": "ステップタイトル",
      "description": "ステップの説明"
    }
  ],

  "comparison_table": {
    "title": "比較表タイトル",
    "headers": ["項目", "この薬", "類似薬A", "類似薬B"],
    "rows": [
      ["強さ", "マイルド", "ストロング", "ウィーク"],
      ["価格", "○", "△", "○"],
      ["使いやすさ", "◎", "○", "○"]
    ]
  },

  "price_info": {
    "prescription": {
      "price": "処方薬の価格目安",
      "insurance": "保険適用の有無と自己負担額"
    },
    "otc": {
      "available": true,
      "price_range": "市販薬の価格帯",
      "products": ["市販薬名1", "市販薬名2"]
    }
  },

  "side_effects": {
    "common": [
      {
        "symptom": "よくある副作用",
        "frequency": "頻度",
        "action": "対処法"
      }
    ],
    "rare": [
      {
        "symptom": "まれな副作用",
        "action": "対処法"
      }
    ],
    "contraindications": [
      "使用してはいけないケース1",
      "使用してはいけないケース2"
    ]
  },

  "faq": [
    {
      "question": "よくある質問1",
      "answer": "回答1"
    },
    {
      "question": "よくある質問2",
      "answer": "回答2"
    },
    {
      "question": "よくある質問3",
      "answer": "回答3"
    }
  ],

  "user_voice": [
    {
      "age": "30代",
      "gender": "女性",
      "symptom": "使用した症状",
      "comment": "使用者の声・感想",
      "rating": 4
    }
  ],

  "competitors": [
    {
      "name": "類似薬・競合薬名",
      "comparison": "この薬との違い",
      "recommendation": "どちらが適しているか"
    }
  ],

  "cta": {
    "primary_text": "メインCTAボタンのテキスト",
    "primary_url": "#",
    "secondary_text": "サブCTAボタンのテキスト（任意）",
    "secondary_url": "#"
  },

  "related_articles": [
    {
      "title": "関連記事タイトル1",
      "description": "関連記事の説明",
      "url": "#"
    }
  ],

  "meta": {
    "title": "SEOタイトル（60文字以内）",
    "description": "メタディスクリプション（120文字以内）",
    "keywords": ["キーワード1", "キーワード2", "キーワード3"]
  },

  "last_updated": "2024-01-27",
  "medical_disclaimer": "この記事は医療情報の提供を目的としており、医師の診断・治療の代わりとなるものではありません。症状がある場合は必ず医師に相談してください。"
}

【重要な注意事項】
1. 医学的に正確な情報を記載すること
2. 「個人差があります」「医師に相談してください」などの注意喚起を適切に含める
3. 誇大表現や断定的な効果の記載は避ける
4. 副作用や禁忌事項は正確に記載する
5. 鍵野院長のコメントは専門家らしい口調で、かつ患者に寄り添った内容にする

出力はJSON形式のみでお願いします。
```

---

## 使用例

### 入力
```
薬名：ロコイド軟膏
```

### 期待される出力
（上記JSON構造に沿ったデータ）

---

## カスタマイズ可能な項目

### カテゴリ別の追加項目

**ステロイド外用薬の場合：**
- strength_rank: 強さランク（ストロンゲスト〜ウィーク）
- absorption_rate: 吸収率
- suitable_area: 適した部位

**内服薬の場合：**
- interaction: 相互作用のある薬
- food_interaction: 食事との関係
- timing: 服用タイミング

**点眼薬の場合：**
- drop_method: 点眼方法
- contact_lens: コンタクトレンズとの関係
- storage: 保管方法

---

## 鍵野院長情報（固定）

```json
{
  "name": "鍵野 太郎",
  "title": "QBCスキンクリニック院長",
  "credential": "皮膚科専門医・医学博士",
  "image_url": "https://pub-72bbcf8e61fe4f5c89e5b1d0b6409eae.r2.dev/hospital_director_kagino.webp"
}
```

---

## 出力後の次のステップ

1. 生成されたJSONをコピー
2. HTMLテンプレートに流し込み
3. WordPressにHTMLを貼り付け
4. 画像を適宜差し替え
5. 公開前に医療監修者チェック
