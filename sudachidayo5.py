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
text = "町のカフェで、新人スタッフが操作を誤り、マシンの圧力が暴発した。激流のようにフォームがあふれ出し、厨房は一瞬騒然となる。先輩は反切した手順書をめくりながら、壁際の小さな玉櫛笥へ駆け寄り、慣れた手つきで工具を取り出した。マシンのゆるんだ部分をしっかり締め直すと、圧力は元に戻り、泡の噴き出しも収まった。空木のカウンター越しに聞こえた騒音は客席に筒抜けだったが、特待のマネージャーは憐憫の笑みを浮かべ、落ち着いた口調で状況を収めた。入り口の七竈は、店主の故地から届いたものだった。思い出に守られるように、カフェは再び静けさを取り戻した。"


for token in tagger(text):
    # lemma を優先するが、"-" があれば前半のみ使用（例: "アレルゲン-allergen" → "アレルゲン"）
    raw_lemma = token.feature[7] if len(token.feature) > 7 else token.surface
    base = raw_lemma.split("-")[0]
    if base == "*" or base == "":
        base = token.surface  # 最後の保険
    pos = token.feature[0]  # 品詞（大分類）
    search_word(base, pos)
