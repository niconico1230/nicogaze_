import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from eyedata import x_list,time_list
from DATAmojiy import moji_list,char_list
import matplotlib.font_manager as fm

# 日本語フォントを指定（例：Windows）
plt.rcParams['font.family'] = 'MS Gothic'  # Windows標準

# ---------- 1. gaze_dfの作成 ----------
gaze_df = pd.DataFrame({
    "timestamp": time_list,
    "gaze_x": x_list
})
print(f"✅ gaze_df 読み込み完了: {len(gaze_df)}行")

# ---------- 2. char_dfの作成 ----------
char_df = pd.DataFrame({
    "char": char_list,
    "x_center": moji_list
})

# 範囲と滞在時間の初期化
char_df["x_start"] = char_df["x_center"] - 50
char_df["x_end"] = char_df["x_center"] + 50
char_df["duration_ms"] = 0

print(f"✅ char_df 読み込み完了: {len(char_df)}文字")

# ---------- 3. 滞在時間の集計 ----------

for i in range(len(gaze_df) - 1):
    t1, x1 = gaze_df.iloc[i]["timestamp"], gaze_df.iloc[i]["gaze_x"]
    t2 = gaze_df.iloc[i + 1]["timestamp"]
    duration = t2 - t1
    matched = False

    min_dist = float("inf")
    target_idx = None

    for idx, row in char_df.iterrows():
        dist = abs(x1 - row["x_center"])
        if dist < min_dist:
            min_dist = dist
            target_idx = idx

    if target_idx is not None:
        char_df.at[target_idx, "duration_ms"] += duration
        print(f"... → 文字 {char_df.at[target_idx, 'char']} (範囲 {row['x_start']:.1f}〜{row['x_end']:.1f}) にHIT")

# ---------- 4. ヒートマップ表示 ----------
print("\n📊 各文字ごとの滞在時間（ms）:")
#print(char_df[["char", "duration_ms"]])
print(char_df[["char", "duration_ms"]].to_csv(index=False, header=False))


max_dur = char_df["duration_ms"].max()
if max_dur == 0:
    print("\n⚠ 滞在時間がすべて0のため、ヒートマップは白くなります。")
else:
    plt.figure(figsize=(max(12, len(char_df)), 4))  # 幅は文字数に応じて調整
    colors = plt.cm.YlOrRd(char_df["duration_ms"] / (max_dur + 1e-5))

    y_level = 0.5
    for i, row in char_df.iterrows():
        plt.text(row["x_center"], y_level, row["char"],
                 fontsize=16, ha='center', va='center',
                 bbox=dict(facecolor=colors[i], edgecolor='none', boxstyle='round,pad=0.3'))

    plt.xlim(char_df["x_center"].min() - 50, char_df["x_center"].max() + 50)
    plt.ylim(0, 1)  # y方向を明示
    plt.axis('off')
    plt.title("視線滞在時間ヒートマップ")
    plt.tight_layout()
    #plt.show()