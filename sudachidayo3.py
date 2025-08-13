from sudachipy import dictionary, tokenizer
import json
import ast  # 安全な eval の代替]import json
import ast
import pickle


# JSONファイルを読み込む
with open("word_index_short.json", "r", encoding="utf-8") as f:
    raw_index = json.load(f)
# キーを (基本形, 品詞) タプルに変換
word_index = {}
for i, (key, value) in enumerate(raw_index.items()):
    #if i % 1000 == 0:
        #print(f"変換中: {i} / {len(raw_index)}")
    word_index[tuple(ast.literal_eval(key))] = value

# Pickleファイルとして保存
with open("word_index_short.pkl", "wb") as f:
    pickle.dump(word_index, f)

print("✅ Pickleファイルの作成が完了しました")