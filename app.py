from flask import Flask, request, render_template_string
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# === Google Sheets 接続設定 ===
creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])  # Render 環境変数
scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

SHEET_ID = os.environ["1of-9NiJTC0gI60e9MI_dI-XVy9tUfD2MIYLxoNUPODM"]
sheet = client.open_by_key(SHEET_ID).sheet1


# === HTMLテンプレート ===
TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>歌唱リスト検索</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        input { padding: 5px; margin: 5px; }
        table { border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; }
    </style>
</head>
<body>
    <h1>歌唱リスト検索</h1>
    <form method="get">
        <input type="text" name="q" placeholder="曲名 or アーティスト" value="{{ query }}">
        <input type="submit" value="検索">
    </form>
    <table>
        <tr><th>曲名</th><th>アーティスト</th></tr>
        {% for song in results %}
            <tr><td>{{ song[0] }}</td><td>{{ song[1] }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""


# === ルーティング ===
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").lower()
    data = sheet.get_all_values()[1:]  # 1行目はヘッダーなのでスキップ

    if query:
        results = [row for row in data if query in row[0].lower() or query in row[1].lower()]
    else:
        results = data

    return render_template_string(TEMPLATE, results=results, query=query)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
