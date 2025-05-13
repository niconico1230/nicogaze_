import csv
import pickle
import json  # ← 追加

#jsonファイルに書き写すプログラム(未知語捜索用)
def build_index(tsv_file="BCCWJ_frequencylist_luw_ver1_1.tsv", index_file="word_index_long.json"):
    word_index = {}  #空の辞書（index）を準備します。
    with open(tsv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            word = row["lemma"]
            full_pos = row["pos"]  # 品詞（pos）を取得
            pos_category = full_pos.split("-")[0]  # 先頭の品詞カテゴリだけ使う

             # ここでキーを (単語, 品詞) のタプルにします
            word_pos_key = (word, pos_category)

            if (word_pos_key not in word_index):
                # 既に存在しない場合、frequency と pmw を加
                word_index[word_pos_key] = {
                    "frequency": int(row["frequency"]),
                    "pmw": float(row["pmw"])
                }

  # 🔁 JSONのキーにタプルは使えないので、文字列に変換
    word_index_str_keys = {
        json.dumps(key, ensure_ascii=False): value for key, value in word_index.items()
    }
            

    # pickleで保存（バイナリファイル）
    with open(index_file, "w", encoding="utf-8")  as f:
        json.dump(word_index_str_keys, f, ensure_ascii=False, indent=2)
    print("✅ JSON形式でインデックス（辞書）を作成して保存しました！")


    # =====================
# 実行ボタンを押したときに動く場所！
# =====================
if __name__ == "__main__":
    build_index()  # 自動で実行されます！