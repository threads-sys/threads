# 求人情報 追記ツール（Apps Script 連携）

「外国人材紹介 営業アプローチリスト（統合版）」スプレッドシートへ、Google Apps Script の
Web アプリ経由で求人情報を追記するための仕組み一式です。

- スプレッドシート: [外国人材紹介 営業アプローチリスト（統合版）](https://docs.google.com/spreadsheets/d/1d-7ziprX6wXpeXyYGXSYLf4FSybhlLN0KnxQkPgQUh8/edit)
- Web アプリ (`/exec`): デプロイ済み。POST で行を追記する。

## エンドポイントの契約

| 項目 | 値 |
| --- | --- |
| メソッド | `POST` |
| Content-Type | `application/json` |
| ボディ | `{ "secret": "<シークレット>", "rows": [ [列1, 列2, ...], ... ] }` |
| 認証 | `secret` フィールド（既定値 `1223`）。不一致なら `{"status":"unauthorized"}` |
| 成功レスポンス | `{"status":"ok","appended": <追記した行数>}` |

`rows` は「1 行 = セル値の配列」を並べた二次元配列です。各配列の要素は下記の列順に対応します。

### 列順（22 列）

| # | 見出し | 英語エイリアス |
| --- | --- | --- |
| 1 | No. | `no` |
| 2 | 情報源 | `source` |
| 3 | 会社名 | `company` |
| 4 | 業種 | `industry` |
| 5 | 従業員規模 | `employees` |
| 6 | 担当部署・担当者名 | `contact` |
| 7 | 電話番号 | `phone` |
| 8 | メールアドレス | `email` |
| 9 | HP/SNS URL | `url` |
| 10 | 外国人雇用実績 | `foreign_hiring` |
| 11 | 言語対応 | `language` |
| 12 | 求人番号 | `job_number` |
| 13 | 採用人数 | `headcount` |
| 14 | 賃金目安 | `wage` |
| 15 | 所在地 | `location` |
| 16 | データ入力日 | `entry_date` |
| 17 | 初回アプローチ日 | `first_approach` |
| 18 | 最終コンタクト日 | `last_contact` |
| 19 | ステータス | `status` |
| 20 | 提案職種 | `proposed_role` |
| 21 | 対応分野 | `field` |
| 22 | 備考・メモ | `notes` |

## 使い方（クライアント）

求人情報を JSON 配列で用意し、`scripts/append_jobs.py` で送信します。各オブジェクトのキーは
見出し（日本語）でも英語エイリアスでも指定でき、未指定の列は空欄になります。

```bash
# 送信内容の確認だけ（送信しない）
python3 scripts/append_jobs.py data/sample_jobs.json --dry-run

# 実際に追記する
python3 scripts/append_jobs.py data/sample_jobs.json
```

エンドポイントとシークレットは環境変数で上書きできます。

```bash
export APPS_SCRIPT_URL="https://script.google.com/macros/s/.../exec"
export APPS_SCRIPT_SECRET="1223"
python3 scripts/append_jobs.py data/my_jobs.json
```

`curl` で直接送る例:

```bash
curl -L -X POST "$APPS_SCRIPT_URL" \
  -H "Content-Type: application/json" \
  -d '{"secret":"1223","rows":[["","ハローワーク","株式会社サンプル", ... ]]}'
```

## Apps Script 側（`apps-script/`）

`apps-script/コード.gs` は、デプロイ済み Web アプリと同じ入出力契約を再現したリファレンス
実装です。スプレッドシートにバインドした Apps Script プロジェクト（ファイル名「コード」）へ
貼り付け、「デプロイ > 新しいデプロイ > ウェブアプリ」で公開すると同じエンドポイントとして
動作します。`appsscript.json` はそのマニフェスト例です。

## 注意点

- **シークレットの取り扱い**: 既定値 `1223` はこのリポジトリにも記載されています。運用上は
  Apps Script の Script Properties へ移し、クライアントは環境変数から渡す方式を推奨します。
- **追記位置**: `appendRow` はシート内で「最後に値が入っている行」の直後に追記します。
  既存のテンプレート空行（No. だけ入っている行）には差し込まれず、その下に新しい行が
  追加されます。
