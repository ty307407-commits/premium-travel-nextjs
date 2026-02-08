#!/bin/bash
# Gemini APIを使った口コミ分析スクリプト（curl版）

API_KEY="AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
HOTEL_ID="13462"
HOTEL_NAME="奥日光 ホテル四季彩"
REVIEW_URL="https://review.travel.rakuten.co.jp/hotel/voice/13462/"

echo "🚀 口コミ分析開始: $HOTEL_NAME ($HOTEL_ID)"
echo "URL: $REVIEW_URL"

# 1. 口コミHTML取得（簡易テキスト化）
echo "📥 口コミページを取得中..."
REVIEW_TEXT=$(curl -s "$REVIEW_URL" | sed -n '/<dl class="commentRep">/,/<\/dl>/p' | sed 's/<[^>]*>//g' | tr -d '\n' | tr -s ' ' | cut -c 1-20000)

if [ -z "$REVIEW_TEXT" ]; then
  echo "❌ 口コミ取得失敗"
  exit 1
fi

echo "📄 口コミテキスト抽出完了（$(echo "$REVIEW_TEXT" | wc -c)文字）"

# 2. JSONペイロード作成（エスケープ処理が必要）
# JSON内の改行や特殊文字をエスケープ
SAFE_TEXT=$(echo "$REVIEW_TEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
# python3 -c ... は文字列エスケープのためだけに使用（依存なし）

JSON_PAYLOAD=$(cat <<EOF
{
  "contents": [{
    "parts": [{
      "text": "以下の楽天トラベルの口コミページの内容を分析してください。\n\n旅館名: $HOTEL_NAME\n\n【口コミデータ】\n$SAFE_TEXT\n\n【タスク】\n1. 最新の口コミから具体的な声を3件抽出\n2. 高評価のポイント（キーワード）\n3. 低評価のポイント（改善点）\n4. どんな人におすすめか\n\n出力形式: JSONのみ"
    }]
  }]
}
EOF
)

# 3. Gemini API送信
echo "🤖 Gemini APIに送信中..."
RESPONSE=$(curl -s -H 'Content-Type: application/json' \
  -d "$JSON_PAYLOAD" \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$API_KEY")

# 4. 結果表示
echo ""
echo "✅ 分析結果:"
echo "$RESPONSE" | grep -A 100 '"text":'
echo ""
