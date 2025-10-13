from flask import Flask, render_template, request, jsonify
from fugashi import Tagger
import unidic_lite
from pathlib import Path

app = Flask(__name__)

# 表示する文章（デモ用）
TEXT = "私は昨日、図書館で本を読みました。"

# 形態素解析して、単語ごとの開始・終了位置を取得
def tokenize_with_index(text):
    dic_path = Path(unidic_lite.DICDIR)  # pathlib で安全にパスを扱う
    tagger = Tagger(f'-d "{dic_path}"')  # ダブルクオートでパス全体を囲む
    tokens = []
    pos = 0
    for word in tagger(text):
        surface = word.surface
        tokens.append({
            "word": surface,
            "start": pos,
            "end": pos + len(surface)
        })
        pos += len(surface)
    return tokens

@app.route("/")
def index():
    tokenized_words = tokenize_with_index(TEXT)
    return render_template("index.html", tokenized_words=tokenized_words)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    print("Received unknown words:", data["unknown_words"])
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
