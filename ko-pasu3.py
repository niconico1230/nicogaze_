import csv
import pickle
import json  # ← 追加

#jsonファイルに書き写すプログラム(未知語作成用)
def build_index(tsv_file="BCCWJ_frequencylist_suw_ver1_1.tsv", index_file="shortword.json"):
    word_index = {}  #空の辞書（index）を準備します。
    seen_pos_categories = set()  # 品詞カテゴリを格納する集合
    with open(tsv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        num=1
        for row in reader:
            word = row["lemma"]
            word2=row["lForm"]
            full_pos = row["pos"]  # 品詞（pos）を取得
            type=row["wType"]#文字のタイプ
            pos_category = full_pos.split("-")[0]  # 先頭の品詞カテゴリだけ使う

            

             # ここでキーを (単語, 品詞) のタプルにします
            word_pos_key = (word, pos_category)

            if (word_pos_key not in word_index ):
                if(type=="和" or type=="漢"):#どちらかに一致するか
                    if(pos_category!="接尾辞" and pos_category!="接頭辞" and pos_category!="助詞" and pos_category!="助動詞"):
                        # 既に存在しない場合、frequency と pmw を加
                        word_index[num] = {#num番目
                            "word":word,
                            "word2":word2,
                            "pos_category":pos_category,
                            "frequency": int(row["frequency"]),
                        }
                        num=num+1

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