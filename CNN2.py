import math
from DATAeye import eyelist
from DATAmoji import mojilist
import numpy as np

def match_gaze_to_text(eyelist, mojilist, threshold=50):
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

# 滞在時間記録用辞書（ミリ秒単位）
gaze_duration = {(word, x, y): 0 for word, x, y in mojilist}
#print(gaze_duration)
#print("moji",mojilist)

# 視線の前回状態
previous_word = None
previous_time = None
previous_coords = None

# マッチした視線データで滞在時間を計算
for ((t, gx, gy), (word, tx, ty)) in matched_gaze:
    if previous_word == word and previous_coords == (tx, ty):
        # 前の視線と同じ文字なら時間差を加算
        gaze_duration[(word, tx, ty)] += t - previous_time
    # 状態更新
    previous_word = word
    previous_coords = (tx, ty)
    previous_time = t

# 結果表示（秒に変換）
for char, duration in gaze_duration.items():
    #print(f"文字「{char}」: {duration / 1000:.4f} 秒")
    print(f" {duration / 1000:.4f} 秒")