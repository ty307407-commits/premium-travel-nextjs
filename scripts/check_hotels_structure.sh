#!/bin/bash
# hotelsテーブルの構造を確認（楽天のレビュー項目を調査）

echo "=== hotelsテーブルの構造確認 ==="
echo ""

AUTH=$(echo -n 'S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286' | base64)

# サンプルデータを1件取得してカラム名を確認
echo "📊 hotelsテーブルのサンプルデータ（1件）:"
curl -s "https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint/page_data_summary" \
  -H "Authorization: Basic $AUTH" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('data', {}).get('rows'):
    # page_data_summaryは使えないので別の方法を考える
    print('page_data_summaryは利用不可')
" 2>/dev/null

echo ""
echo "💡 hotelsテーブルの構造をSQLで直接確認する必要があります"
echo ""
echo "以下のSQLをTiDB Cloud Consoleで実行してください:"
echo ""
echo "-- ステップ1: テーブル構造確認"
echo "DESCRIBE test.hotels;"
echo ""
echo "-- ステップ2: サンプルデータ確認"
echo "SELECT * FROM test.hotels LIMIT 1;"
echo ""
echo "-- ステップ3: レビュー項目カラムの確認"
echo "SHOW COLUMNS FROM test.hotels LIKE '%review%';"
echo "SHOW COLUMNS FROM test.hotels LIKE '%average%';"
