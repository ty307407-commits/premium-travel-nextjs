"""
TiDB テーマ一覧エクスポートスクリプト
Google Colabで実行してください

使用方法:
1. Google Colabで新しいノートブックを作成
2. このコードをセルに貼り付けて実行
3. 結果をコピーしてClaude Codeに共有
"""

# パッケージインストール（Colabで実行時）
# !pip install pymysql

import pymysql
import json

# TiDB接続情報
config = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test',
    'ssl': {'ssl': {}}
}

def get_themes():
    """テーマ一覧を取得"""
    connection = pymysql.connect(**config)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # テーブル一覧を確認
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("=== テーブル一覧 ===")
            for t in tables:
                print(list(t.values())[0])

            # themesテーブルがあれば取得
            cursor.execute("SHOW TABLES LIKE '%theme%'")
            theme_tables = cursor.fetchall()

            if theme_tables:
                table_name = list(theme_tables[0].values())[0]
                print(f"\n=== {table_name} テーブルの構造 ===")
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  {col['Field']}: {col['Type']}")

                print(f"\n=== {table_name} のデータ ===")
                cursor.execute(f"SELECT * FROM {table_name}")
                themes = cursor.fetchall()
                print(f"件数: {len(themes)}")

                # JSON出力
                print("\n=== JSON出力 ===")
                print(json.dumps(themes, ensure_ascii=False, indent=2, default=str))

                return themes
            else:
                print("\nテーマ関連のテーブルが見つかりません。")
                print("全テーブルのデータを確認します...")

                for t in tables:
                    table_name = list(t.values())[0]
                    cursor.execute(f"SELECT COUNT(*) as cnt FROM {table_name}")
                    count = cursor.fetchone()['cnt']
                    print(f"  {table_name}: {count}件")

    finally:
        connection.close()

if __name__ == "__main__":
    get_themes()
