from sudachipy import dictionary, tokenizer
import pickle
from fugashi import Tagger

# --- Pickleファイルを読み込む ---
with open("word_index_short.pkl", "rb") as f:
    word_index_short = pickle.load(f)

with open("word_index_long.pkl", "rb") as f:
    word_index_long = pickle.load(f)

# --- fugashi タガーの初期化 ---
fugashi_tagger = Tagger()

# --- 単語と品詞を検索する関数 ---
def search_word(word="ありがとう", pos="感動詞", try_fallback=True):
    word_pos_key = (word, pos)

    if word_pos_key in word_index_short:
        info = word_index_short[word_pos_key]
        print(f"{word} : {pos} ✅〔short〕頻度: {info['frequency']}")
    elif word_pos_key in word_index_long:
        info = word_index_long[word_pos_key]
        print(f"{word} : {pos} ✅〔long〕頻度: {info['frequency']}")
    elif try_fallback:
        print(f"{word} : {pos} ❌ → fugashi fallback")
        # fugashiで再解析
        for token in fugashi_tagger(word):
            fallback_base = token.feature[7] if len(token.feature) > 7 else token.surface
            fallback_pos = token.feature[0]
            if fallback_base == "*":
                fallback_base = token.surface
            # 再帰的にfallbackをfalseにして再検索（無限ループ防止）
            search_word(fallback_base, fallback_pos, try_fallback=False)
    else:
        print(f"{word} : {pos} ❌（fugashiでも見つからず）")
    

# --- 形態素解析＋逐次出力 ---
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

text = "藤棚の下の小さな舞台で、男が熱演を繰り広げる中、観客はわずか数名だった。老婦人は懐から古びた電文を取り出し、それをそっと書き留める。そこには、若き日の接得の失敗と、今は亡き友に捧げる積徳の誓いが綴られていた。隣では学生が、風に揺れる花粉を頼りに繊毛の動きとアレルゲンの挙動を観察している。舞台裏では、銘酒を交わし合う裏方たちが、与太話に花を咲かせていた。やがて演目が終わると、老婦人はそっと立ち上がり、手紙を舞台へと差し出した。かつてこの舞台の上で、ともに夢を語り合った友の面影が、今目の前に蘇ったように思えたのだ。"

for token in tokenizer_obj.tokenize(text, mode):
    base = token.dictionary_form()
    pos = token.part_of_speech()[0]
    search_word(base, pos)