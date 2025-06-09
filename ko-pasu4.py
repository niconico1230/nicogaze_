import json
import random


#検索するプログラム

# JSONファイルを読み込む
with open("shortword.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 中身を表示（最初の10個の単語だけ表示）
#for i, (word, info) in enumerate(word_index.items()):
    #print(word, info)
    #if i >= 20:
        #break


# frequencyが10以上30以下のアイテムを抽出
low_frequency_words = {
    key: value for key, value in data.items() if 1 <= value["frequency"] <=20
}



# アイテムをリストに変換
low_freq_items = list(low_frequency_words.items())

# 1%だけランダム抽出（100個に1個）
sample_size = max(1, len(low_freq_items) //1000)  # 少なくとも1個は取る
sampled_items = random.sample(low_freq_items, sample_size)

# 結果を表示
for key, value in sampled_items:
    print(f"{value["word"]}",f"{value["word2"]}",f"{value["frequency"]}",f"{value["pos_category"]}")
    #print(f"{value["word"]}")


