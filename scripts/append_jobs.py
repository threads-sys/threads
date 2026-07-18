#!/usr/bin/env python3
"""外国人材紹介 営業アプローチリストへ、Apps Script Web アプリ経由で求人情報を追記する。

使い方:
    python3 scripts/append_jobs.py data/sample_jobs.json
    python3 scripts/append_jobs.py data/sample_jobs.json --dry-run

入力 JSON は求人オブジェクトの配列。各オブジェクトのキーは COLUMNS の
見出し（日本語）またはそのエイリアス（英語）で指定できる。未指定の列は空欄。

エンドポイントとシークレットは環境変数で上書きできる:
    APPS_SCRIPT_URL     Web アプリの /exec URL
    APPS_SCRIPT_SECRET  認証シークレット（既定: 1223）
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

DEFAULT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzaoYeWgn7BPoMXZTNT3r8t0RxyMwc8wTgTPbBLnlF5DEPs1lhcMYdMStxRtZU4LJFENw/exec"
)
DEFAULT_SECRET = "1223"

# スプレッドシートの列順（見出し行と同じ並び）。
COLUMNS = [
    "No.",
    "情報源",
    "会社名",
    "業種",
    "従業員規模",
    "担当部署・担当者名",
    "電話番号",
    "メールアドレス",
    "HP/SNS URL",
    "外国人雇用実績",
    "言語対応",
    "求人番号",
    "採用人数",
    "賃金目安",
    "所在地",
    "データ入力日",
    "初回アプローチ日",
    "最終コンタクト日",
    "ステータス",
    "提案職種",
    "対応分野",
    "備考・メモ",
]

# 英語エイリアス -> 正式な見出し。入力 JSON をどちらのキーでも書けるようにする。
ALIASES = {
    "no": "No.",
    "source": "情報源",
    "company": "会社名",
    "industry": "業種",
    "employees": "従業員規模",
    "contact": "担当部署・担当者名",
    "phone": "電話番号",
    "email": "メールアドレス",
    "url": "HP/SNS URL",
    "foreign_hiring": "外国人雇用実績",
    "language": "言語対応",
    "job_number": "求人番号",
    "headcount": "採用人数",
    "wage": "賃金目安",
    "location": "所在地",
    "entry_date": "データ入力日",
    "first_approach": "初回アプローチ日",
    "last_contact": "最終コンタクト日",
    "status": "ステータス",
    "proposed_role": "提案職種",
    "field": "対応分野",
    "notes": "備考・メモ",
}


def normalize(job):
    """求人オブジェクトを COLUMNS の順に並べたセル値の配列へ変換する。"""
    resolved = {}
    for key, value in job.items():
        header = key if key in COLUMNS else ALIASES.get(key)
        if header is None:
            raise ValueError(f"未知のフィールド名: {key!r}")
        resolved[header] = value
    return ["" if resolved.get(col) is None else resolved.get(col, "") for col in COLUMNS]


def build_payload(jobs, secret):
    rows = [normalize(job) for job in jobs]
    return {"secret": secret, "rows": rows}


def post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:  # 302 は自動で追従される
        return resp.read().decode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="求人オブジェクト配列の JSON ファイル")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="送信せず、生成される payload を表示する",
    )
    parser.add_argument("--url", default=os.environ.get("APPS_SCRIPT_URL", DEFAULT_URL))
    parser.add_argument(
        "--secret", default=os.environ.get("APPS_SCRIPT_SECRET", DEFAULT_SECRET)
    )
    args = parser.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        jobs = json.load(f)
    if not isinstance(jobs, list):
        print("入力 JSON は求人オブジェクトの配列である必要があります。", file=sys.stderr)
        return 1

    payload = build_payload(jobs, args.secret)

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"\n(dry-run) {len(payload['rows'])} 行を送信対象として生成しました。", file=sys.stderr)
        return 0

    body = post(args.url, payload)
    print(body)
    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        print("エンドポイントから JSON 以外の応答が返りました。", file=sys.stderr)
        return 1
    if result.get("status") != "ok":
        print(f"追記に失敗しました: {result}", file=sys.stderr)
        return 1
    print(f"{result.get('appended')} 行を追記しました。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
