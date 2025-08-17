from flask import Flask, render_template_string, request
import os
import json
import gspread
from google.oauth2.service_account import Credentials
app = Flask(__name__)

# ==== Google Sheets 認証 ====
# Renderの環境変数からキーを取得
creds_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)

scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# ==== スプレッドシート設定 ====
SHEET_ID = os.getenv("1of-9NiJTC0gI60e9MI_dI-XVy9tUfD2MIYLxoNUPODM")  # Renderの環境変数に追加してね
sheet = client.open_by_key(SHEET_ID).sheet1


# ==== HTMLテンプレート ====
HTML = """
<!doctype html>
<html>
<head>
  <title>歌唱リスト</title>
</head>
<body>
  <h1>歌唱リスト 🎤</h1>
  <form method="get">
    <input type="text" name="q" placeholder="曲名やアーティストで検索" value="{{query}}">
    <button type="submit">検索</button>
  </form>
  <ul>
    {% for song in results %}
      <li>{{song[0]}} - {{song[1]}}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""

# ==== ルーティング ====
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").lower()
    data = sheet.get_all_values()[1:]  # ヘッダーを除く
    results = [row for row in data if query in row[0].lower() or query in row[1].lower()]
    if not query:  # 検索なしなら全件
        results = data
    return render_template_string(HTML, results=results, query=query)


# ==== メイン ====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
