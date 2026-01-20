# TiDB Cloud データベース情報

## 接続情報

| 項目 | 値 |
|------|-----|
| Host | gateway01.ap-northeast-1.prod.aws.tidbcloud.com |
| Port | 4000 |
| Database | test |
| Username | 4VWXcjUowH2PPCE.root |
| Password | cDRDyvsJTMHJdiR7 |
| API Public Key | S2R9M3V0 |
| API Private Key | 8cc2d2cd-7567-422a-a9d1-8a96b5643286 |

## 接続文字列

```
mysql://4VWXcjUowH2PPCE.root:cDRDyvsJTMHJdiR7@gateway01.ap-northeast-1.prod.aws.tidbcloud.com:4000/test
```

## データエクスポート

最新のデータは以下のファイルを参照:
- `data/tidb_export.json` - 完全エクスポート（Colabで生成）
- `data/themes_current.json` - 現在のテーマ一覧

## エクスポート方法

Google Colabで `scripts/tidb_full_export.py` を実行:

```python
# セル1
!pip install pymysql

# セル2
# scripts/tidb_full_export.py の内容を貼り付けて実行
```

---

## テーブル構造

> ⚠️ 以下はColabでエクスポート後に更新してください

### テーブル一覧

（Colabの実行結果をここに貼り付け）

### テーマテーブル

（Colabの実行結果をここに貼り付け）

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-20 | ドキュメント作成 |

