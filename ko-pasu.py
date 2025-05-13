import pickle

#検索するプログラム

# バイナリファイルを読み込む
with open("word_index.pkl", "rb") as f:
    word_index = pickle.load(f)

# 中身を表示（最初の10個の単語だけ表示）
#for i, (word, info) in enumerate(word_index.items()):
    #print(word, info)
    #if i >= 20:
        #break

def search_word(index_file="word_index_long.pkl", word="ありがとう",pos="感動詞"):

     # 単語と品詞でキーを作成
    word_pos_key = (word, pos)

    # 単語がインデックスにあるか確認
    if word_pos_key in word_index:
        info = word_index[word_pos_key]
        print(f"🔍 単語: {word}（品詞: {pos}）")
        print(f"📊 出現頻度: {info['frequency']} 回")
        print(f"📈 PMW（百万語あたり）: {info['pmw']}")
    else:
        print(f"❌ 単語「{word}」はインデックスに見つかりませんでした。")


search_word("word_index.pkl", word="事",pos="名詞")
search_word("word_index.pkl", word="協力する",pos="動詞")


