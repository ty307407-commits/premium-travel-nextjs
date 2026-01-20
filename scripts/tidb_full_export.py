"""
TiDB 完全エクスポートスクリプト
Google Colabで実行してください

実行方法:
1. Google Colabで新しいノートブックを作成
2. 以下のコードをセルに貼り付けて実行
3. 出力結果をコピーしてClaude Codeに共有、またはファイルとして保存

出力内容:
- データベース一覧
- テーブル一覧
- 各テーブルの構造（カラム情報）
- 各テーブルのデータ件数
- テーマ関連データの完全出力
"""

# ============================================
# セル1: パッケージインストール
# ============================================
# !pip install pymysql

# ============================================
# セル2: 完全エクスポート実行
# ============================================
import pymysql
import json
from datetime import datetime

# TiDB接続情報
CONFIG = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test',
    'ssl': {'ssl': {}}
}

def export_all():
    """TiDBの全情報をエクスポート"""
    result = {
        'export_date': datetime.now().isoformat(),
        'connection': {
            'host': CONFIG['host'],
            'database': CONFIG['database']
        },
        'databases': [],
        'tables': [],
        'data': {}
    }

    connection = pymysql.connect(**CONFIG)
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 1. データベース一覧
        print("=" * 60)
        print("1. データベース一覧")
        print("=" * 60)
        cursor.execute("SHOW DATABASES")
        databases = [list(d.values())[0] for d in cursor.fetchall()]
        result['databases'] = databases
        for db in databases:
            print(f"  - {db}")

        # 2. テーブル一覧（testデータベース）
        print("\n" + "=" * 60)
        print("2. テーブル一覧 (test データベース)")
        print("=" * 60)
        cursor.execute("SHOW TABLES")
        tables = [list(t.values())[0] for t in cursor.fetchall()]
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM `{table}`")
            count = cursor.fetchone()['cnt']
            print(f"  - {table}: {count}件")
            result['tables'].append({'name': table, 'count': count})

        # 3. 各テーブルの構造
        print("\n" + "=" * 60)
        print("3. テーブル構造")
        print("=" * 60)
        for table_info in result['tables']:
            table = table_info['name']
            print(f"\n【{table}】")
            cursor.execute(f"DESCRIBE `{table}`")
            columns = cursor.fetchall()
            table_info['columns'] = columns
            for col in columns:
                null_str = "NULL可" if col['Null'] == 'YES' else "NOT NULL"
                key_str = f" [{col['Key']}]" if col['Key'] else ""
                default_str = f" DEFAULT={col['Default']}" if col['Default'] else ""
                print(f"  {col['Field']}: {col['Type']} {null_str}{key_str}{default_str}")

        # 4. 全テーブルのデータ出力
        print("\n" + "=" * 60)
        print("4. テーブルデータ")
        print("=" * 60)
        for table_info in result['tables']:
            table = table_info['name']
            cursor.execute(f"SELECT * FROM `{table}`")
            data = cursor.fetchall()
            # datetime等をJSON serializable に変換
            data_serializable = []
            for row in data:
                row_clean = {}
                for k, v in row.items():
                    if hasattr(v, 'isoformat'):
                        row_clean[k] = v.isoformat()
                    else:
                        row_clean[k] = v
                data_serializable.append(row_clean)
            result['data'][table] = data_serializable

            print(f"\n【{table}】({len(data)}件)")
            if len(data) > 0:
                # 最初の3件をプレビュー
                for i, row in enumerate(data[:3]):
                    print(f"  {i+1}. {row}")
                if len(data) > 3:
                    print(f"  ... 他 {len(data)-3}件")

        # 5. JSON出力
        print("\n" + "=" * 60)
        print("5. 完全JSON出力（これをコピーしてファイルに保存）")
        print("=" * 60)
        json_output = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        print(json_output)

        # ファイル保存（Colab環境用）
        with open('tidb_export.json', 'w', encoding='utf-8') as f:
            f.write(json_output)
        print("\n✅ tidb_export.json に保存しました")

        return result

    finally:
        connection.close()

if __name__ == "__main__":
    export_all()
