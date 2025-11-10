from flask import Flask, render_template, request, jsonify, send_file
from fugashi import Tagger
import unidic_lite
from pathlib import Path
import csv
from io import StringIO
import datetime

app = Flask(__name__)

# 複数の文章をリストで管理（順番に処理するため）
TEXTS = [
    "新商品の企画会議は白熱した。だが、市場競争において、他社とのパリティーを保つだけでは生き残れない。革新的なアイデアこそが、此処許から次の一手を打つための鍵となる。我々のチームは、課題に対してのべつに議論を重ね、その根底に通底する解決の糸口を探り続けた。一度見つけた突破口は、囲碁における掛粘のように、その後の展開を確実に有利にするための布石となる。失敗を恐れず仲間と共に挑戦し、常に先を見据える姿勢が重要だ。その確固たる連携と絶え間ない努力が、最終的な成功へと導くのだ。我々の道のりは始まったばかりであり、真の成功はまだその野末に隠されている。",
    "都市の景観と環境の質を向上させることは、まちづくりにおいて大切な仕事であり、都市計画の現場では、街路の修景や緑地の整備が日常的に行われている。ある日、暗合する設計案を巡って議論が交わされたが、リケッチアのような微細な問題点が指摘され、計画は再考を余儀なくされた。しかし、担当者はその指摘を殊勝と受け止め、より良い解決策を模索する姿勢を見せた。かつて逓信局が置かれていた場所の活用提案も検討され、錚々たる専門家が意見を寄せた。工事現場には塵芥が散乱していたものの、適切な処理方法を導入することで安全性が確保された。こうして、多様な要素を調整しながら街の魅力を高める取り組みが続けられている。",
]

# 現在の文章インデックスとすべての回答データを管理
current_text_index = 0
# 【追加】全回答データを保持するリスト
ALL_RESPONSES = [] 
# 【追加】回答者名を保持（開発/デモ目的のためグローバル変数）
current_respondent_name = ""



# 現在の文章インデックスをグローバル変数（またはセッション）で管理
# 開発/デモ目的のためグローバル変数を使用（本番環境ではセッションを使うべき）
current_text_index = 0

# 形態素解析関数 (変更なし)
def tokenize_with_index(text):
    dic_path = Path(unidic_lite.DICDIR)
    tagger = Tagger(f'-d "{dic_path}"')
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
    global current_text_index, ALL_RESPONSES, current_respondent_name
    current_text_index = 0  # ページアクセス時にインデックスをリセット
    ALL_RESPONSES = [] # 回答データもリセット
    current_respondent_name = "" # 回答者名もリセット
    initial_text = TEXTS[current_text_index]
    tokenized_words = tokenize_with_index(initial_text)
    
    return render_template(
        "index.html",
        text=initial_text,
        tokenized_words=tokenized_words,
        # HTMLにはテキストIDがないため、Flask側でインデックスを管理
    )

# 【新規関数】CSVファイルをディスクに保存する関数
def write_responses_to_csv(responses):
    """
    回答データをCSVファイルとしてサーバー側のディスクに書き出す。
    """
    global current_respondent_name
    respondent_name_safe = current_respondent_name.replace(' ', '_').replace('　', '_') # ファイル名に使えない文字を置換
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"No.{respondent_name_safe}_{now}.csv"

    fieldnames = ['回答者名', '文章インデックス', '未知語リスト']

    # 'w' ではなく 'w', encoding='utf-8-sig' を使用してExcel互換性を高める
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            
            for response in responses:
                row = [
                    response['respondent'],
                    response['text_index'],
                    " | ".join(response['unknown_words'])
                ]
                writer.writerow(row)
        print(f"✅ CSV file successfully written to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error writing CSV file: {e}")
        return None

# 【新規】回答者名を設定するエンドポイント
@app.route("/set_name", methods=["POST"])
def set_name():
    global current_respondent_name
    data = request.json
    current_respondent_name = data.get("name", "Unknown")
    print(f"Respondent Name Set: {current_respondent_name}")
    # 成功をクライアントに返す
    return jsonify({"status": "success"})


# 👈 新しいエンドポイント: データ受信と次の文章送信
@app.route("/submit_and_next", methods=["POST"])
def submit_and_next():
    global current_text_index, current_respondent_name
    
    # 1. 現在の未知語データを受信し、回答者名とインデックスを付けて保存
    data = request.json
    unknown_words = data.get("unknown_words", [])
    
    # 【追加】回答データを保存
    response_entry = {
        "respondent": current_respondent_name,
        "text_index": current_text_index,
        "unknown_words": [w["word"] for w in unknown_words], # 単語のみをリストとして保存
        "raw_unknown_words": unknown_words # 詳細情報も保存（デバッグ用）
    }
    ALL_RESPONSES.append(response_entry)
    print(f"Saved response for {current_respondent_name} (Text {current_text_index}): {response_entry['unknown_words']}")


    # 2. インデックスを次に進める
    current_text_index += 1
    
    # 3. 次の文章を準備
    if current_text_index < len(TEXTS):
        # 次の文章が存在する場合
        next_text = TEXTS[current_text_index]
        tokenized_words = tokenize_with_index(next_text)
        
        return jsonify({
            "text": next_text,
            "tokenized_words": tokenized_words,
            "is_last": False
        })
    else:
        # すべての文章が終了した場合
        csv_filename = write_responses_to_csv(ALL_RESPONSES) 
        
        final_message = f"{current_respondent_name}番さん、アンケートが終了しました。ご協力ありがとうございました！"
        if csv_filename:
            final_message += f"（結果はサーバーに**{csv_filename}**として自動保存されました）"
            
        # トークンリストを空にして、クリック不可の通常テキストとして表示させる (変更なし)
        return jsonify({
            "text": final_message,
            "tokenized_words": [],  
            "is_last": True
        })
  
if __name__ == "__main__":
    # ユニディック辞書が存在しない場合に自動ダウンロード
    # unidic_liteをインストールしていても、念のためPathで存在確認
    if not Path(unidic_lite.DICDIR).exists():
        print("Unidic-lite dictionary not found. It will be downloaded automatically by fugashi.")
    app.run(debug=True)