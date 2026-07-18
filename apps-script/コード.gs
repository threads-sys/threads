/**
 * 外国人材紹介 営業アプローチリスト（統合版）へ求人情報を追記する Web アプリ。
 *
 * これは、すでにデプロイ済みの Web アプリ
 *   https://script.google.com/macros/s/AKfycbz.../exec
 * と同じ入出力契約を再現したリファレンス実装です。リポジトリ上でコードを
 * バージョン管理するために置いています。実際に動かすには、この内容を対象
 * スプレッドシートにバインドした Apps Script プロジェクト（ファイル名「コード」）へ
 * 貼り付け、ウェブアプリとしてデプロイしてください。
 *
 * 契約:
 *   - メソッド: POST
 *   - Content-Type: application/json
 *   - ボディ: { "secret": "1223", "rows": [ [列1, 列2, ...], ... ] }
 *       secret が一致しない場合は {"status":"unauthorized"} を返す。
 *       rows は「1 行 = セル値の配列」を並べた二次元配列。
 *   - レスポンス(JSON):
 *       成功  : {"status":"ok","appended": <追記した行数>}
 *       認証NG: {"status":"unauthorized"}
 */

// 認証用の共有シークレット。運用では Script Properties 等での管理を推奨。
var SECRET = '1223';

// 追記先スプレッドシート。空文字の場合はコンテナ（バインド元）を使用する。
var SPREADSHEET_ID = '1d-7ziprX6wXpeXyYGXSYLf4FSybhlLN0KnxQkPgQUh8';

// 追記先シート名。空文字の場合は先頭シートを使用する。
var SHEET_NAME = '';

function doPost(e) {
  var body = JSON.parse(e.postData.contents);
  if (body.secret !== SECRET) {
    return jsonOutput({ status: 'unauthorized' });
  }

  var sheet = getTargetSheet_();
  var count = 0;
  body.rows.forEach(function (row) {
    sheet.appendRow(row);
    count++;
  });

  return jsonOutput({ status: 'ok', appended: count });
}

function getTargetSheet_() {
  var ss = SPREADSHEET_ID
    ? SpreadsheetApp.openById(SPREADSHEET_ID)
    : SpreadsheetApp.getActiveSpreadsheet();
  if (SHEET_NAME) {
    var named = ss.getSheetByName(SHEET_NAME);
    if (named) return named;
  }
  return ss.getSheets()[0];
}

function jsonOutput(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
