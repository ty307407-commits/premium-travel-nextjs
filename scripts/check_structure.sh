#!/bin/bash
# page_dataテーブルの構造を確認

echo "=== page_data テーブルの構造確認 ==="
echo ""

# Base64エンコードされた認証情報
AUTH=$(echo -n 'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286' | base64)

# APIエンドポイント（テーブル一覧）
echo "📊 テーブル一覧:"
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/tables" \
  -H "Authorization: Basic $AUTH" | python3 -m json.tool

echo ""
echo "📊 page_data の件数:"
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/test" \
  -H "Authorization: Basic $AUTH" | python3 -m json.tool

echo ""
echo "📊 page_data のサンプル（1件）:"
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_data_summary" \
  -H "Authorization: Basic $AUTH" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['data']['rows'][0] if data['data']['rows'] else {}, indent=2, ensure_ascii=False))"
