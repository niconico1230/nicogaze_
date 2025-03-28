import math
from DATAeye import eyelist
from DATAmoji import mojilist
import numpy as np

def match_gaze_to_text(eyelist, mojilist, threshold=80):#50
    matched = []
    for t, gx, gy in eyelist:
        min_dist = float("inf")
        closest_word = None
        for word, tx, ty in mojilist:
            dist = np.sqrt((gx - tx)**2 + (gy - ty)**2)
            if dist < threshold and dist < min_dist:
                min_dist = dist
                closest_word = (word, tx, ty)
        if closest_word:
            matched.append(((t, gx, gy), closest_word))
    return matched

# マッチング処理
matched_gaze = match_gaze_to_text(eyelist, mojilist)
#print(matched_gaze)

# 滞在時間記録用辞書（ミリ秒単位）
gaze_duration = {(word, x, y): 0 for word, x, y in mojilist}
#print(gaze_duration)
#print("moji",mojilist)


previous_time = None

# 単語ごとの合計滞在時間を計算
#word_duration = {}

# マッチした視線データで滞在時間を計算
for ((t, gx, gy), (word, tx, ty)) in matched_gaze:
    if previous_time is not None:  # 初回でなければ処理する
        gaze_duration[(word, tx, ty)] += t - previous_time

    previous_time = t



# 結果表示（秒に変換）
for word, duration in gaze_duration.items():
    #print(f"文字「{word}」: {duration / 1000:.4f} 秒")
    print(f" {duration / 1000:.4f} 秒")