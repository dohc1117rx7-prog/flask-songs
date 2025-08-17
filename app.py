from flask import Flask, render_template_string, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Google Sheets 認証
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    "service_account.json", scopes=SCOPES
)
client = gspread.authorize(creds)

# シートIDを入れる
SHEET_ID = "1of-9NiJTC0gI60e9MI_dI-XVy9tUfD2MIYLxoNUPODM"
sheet = client.open_by_key(SHEET_ID).sheet1


# HTMLテンプレート（簡易版）
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>歌唱リスト検索</title>
</head>
<body>
    <h1>歌唱リスト検索</h1>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="曲名 or アーティスト" value="{{query}}">
        <button type="submit">検索</button>
    </form>
    <hr>
    {% if results %}
        <ul>
        {% for row in results %}
            <li>{{ row['曲名'] }} - {{ row['アーティスト'] }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>検索結果なし</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "")
    records = sheet.get_all_records()

    if query:
        results = [
            row for row in records
            if query.lower() in row["曲名"].lower() or query.lower() in row["アーティスト"].lower()
        ]
    else:
        results = records  # 未検索なら全部表示

    return render_template_string(HTML, query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)
