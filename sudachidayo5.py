from fugashi import Tagger
import pickle



# --- Pickleファイルを読み込む ---
with open("word_index_short.pkl", "rb") as f:
    word_index_short = pickle.load(f)

#with open("word_index_long.pkl", "rb") as f:
    #word_index_long = pickle.load(f)

# --- fugashiタガーの初期化 ---
tagger = Tagger()

# --- 単語と品詞を検索する関数 ---
def search_word(word, pos):
    key = (word, pos)
    if key in word_index_short:
        info = word_index_short[key]
        print(f"{word} : {pos} ✅〔short〕頻度: {info['frequency']}")
    #elif key in word_index_long:
        #info = word_index_long[key]
        #print(f"{word} : {pos} ✅〔long〕頻度: {info['frequency']}")
    else:
        print(f"{word} : {pos} ❌（見つからず）")

# --- テキストを解析し逐次検索 ---
text = "その厳格さがテーマの中心にあるのだ。そのため"


for token in tagger(text):
    # lemma を優先するが、"-" があれば前半のみ使用（例: "アレルゲン-allergen" → "アレルゲン"）
    raw_lemma = token.feature[7] if len(token.feature) > 7 else token.surface
    base = raw_lemma.split("-")[0]
    if base == "*" or base == "":
        base = token.surface  # 最後の保険
    pos = token.feature[0]  # 品詞（大分類）
    search_word(base, pos)
