from sudachipy import dictionary, tokenizer
import json
import ast  # 安全な eval の代替]import json
import ast
import pickle

# --- 1. JSONファイルを読み込んで辞書に変換 ---
with open("word_index_long.json", "r", encoding="utf-8") as f:
    raw_index = json.load(f)

# キーを (基本形, 品詞) のタプルに変換
#word_index = {tuple(eval(key)): value for key, value in raw_index.items()}

# eval を ast.literal_eval に変更（安全で高速）
word_index = {tuple(ast.literal_eval(key)): value for key, value in raw_index.items()}

# --- 2. 単語と品詞を検索する関数 ---
def search_word(word="ありがとう", pos="感動詞"):
    word_pos_key = (word, pos)
    if word_pos_key in word_index:
        info = word_index[word_pos_key]
        print(f"{word} : {pos} {info['frequency']}")
    else:
        print(f"{word} : {pos} ❌ インデックスに見つかりませんでした")



# --- 3. 形態素解析で基本形と品詞を抽出して検索 ---

# 形態素解析器を作成
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A  # A, B, C から選択可能（Cは最も長い単位）

# 解析対象のテキスト
text = "藤棚の下、小さな舞台で男が渾身の熱演を繰り広げていた。観客はわずか数名。老婦人は懐から古びた電文を取り出し、それをそっと書き留める。"

# トークン化（形態素解析）
tokens = tokenizer_obj.tokenize(text, mode)



# トークンごとに解析＋即時出力
for token in tokenizer_obj.tokenize(text, mode):
    base = token.dictionary_form()
    pos = token.part_of_speech()[0]
    search_word(base, pos)

#for token in tokens:
#    base = token.dictionary_form()
 #   pos = token.part_of_speech()[0]  # 「名詞」など
  #  search_word(base, pos)

