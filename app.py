from flask import Flask, request, render_template_string, make_response
import os
import json
import gspread
from google.oauth2.service_account import Credentials
import unicodedata  # ← 追加：全角/半角のゆらぎ対策
 
app = Flask(__name__)
 
@app.after_request
def add_header(response):
   # Canva からの iframe 埋め込みを許可（* は広すぎるので Canva ドメインに限定）
   response.headers['Content-Security-Policy'] = "frame-ancestors https://*.canva.com https://canva.com 'self';"
   response.headers['X-Frame-Options'] = 'ALLOWALL'
   return response
 
# === Google Sheets 接続設定 ===
creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])  # Render 環境変数（JSON）
scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)
 
SHEET_ID = os.environ["SHEET_ID"]
sheet = client.open_by_key(SHEET_ID).sheet1
 
# === HTMLテンプレート ===
TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
   <meta charset="UTF-8">
   <title>歌唱リスト検索</title>
   <meta name="viewport" content="width=device-width, initial-scale=1" />
   <style>
       body { font-family: Arial, system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans JP", sans-serif; padding: 20px; }
       h1 { margin: 0 0 12px; font-size: 18px; }
       form { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
       input[type="text"] { padding: 8px; min-width: 220px; border: 1px solid #ddd; border-radius: 8px; }
       input[type="submit"] { padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; cursor: pointer; }
       table { border-collapse: collapse; margin-top: 16px; width: 100%; }
       th, td { border: 1px solid #eee; padding: 8px; text-align: left; }
       tr:hover { background: #fafafa; }
       .muted { color: #666; font-size: 12px; }
   </style>
</head>
<body>
   <h1>歌唱リスト検索 <span class="muted">(空検索で全件表示 / 全角・半角OK)</span></h1>
   <form method="get">
       <input type="text" name="q" placeholder="曲名 or アーティスト" value="{{ query }}">
       <input type="submit" value="検索">
   </form>
   <table>
       <tr><th>曲名</th><th>アーティスト</th></tr>
       {% for song in results %}
           <tr>
               <td>{{ song[0] if song|length > 0 else "" }}</td>
               <td>{{ song[1] if song|length > 1 else "" }}</td>
           </tr>
       {% endfor %}
   </table>
</body>
</html>
"""
 
# === ルーティング ===
@app.route("/", methods=["GET"])
def index():
   # 入力値（そのまま表示に使う raw）と、検索用（正規化・小文字化・トリム）を分ける
   raw = request.args.get("q", "")
   query = unicodedata.normalize("NFKC", raw).strip().lower()
 
   # シート読み込み（1行目はヘッダーなのでスキップ）
   data = sheet.get_all_values()[1:]
 
   if query == "":
       # 空検索（半角/全角スペースのみ含む場合も含めて）→ 全件表示
       results = data
   else:
       # 比較対象も正規化＋小文字化して、全角/半角差を吸収
       results = []
       for row in data:
           title = row[0] if len(row) > 0 else ""
           artist = row[1] if len(row) > 1 else ""
           title_n = unicodedata.normalize("NFKC", title).lower()
           artist_n = unicodedata.normalize("NFKC", artist).lower()
           if query in title_n or query in artist_n:
               results.append(row)
 
   # 入力欄にはユーザーが打った生の文字列（raw）を戻す
   html = render_template_string(TEMPLATE, results=results, query=raw)
   resp = make_response(html, 200)
   # 念のためルートでもヘッダ付与（after_requestでも付く）
   resp.headers['Content-Security-Policy'] = "frame-ancestors https://*.canva.com https://canva.com 'self';"
   resp.headers['X-Frame-Options'] = 'ALLOWALL'
   return resp
 
if __name__ == "__main__":
   # Render で動かすなら host/port は環境に合わせて
   app.run(host="0.0.0.0", port=5000)
