import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.font_manager as fm

# 日本語フォントを指定（例：Windows）
plt.rcParams['font.family'] = 'MS Gothic'  # Windows標準


# ---------- 1. gaze_dfの作成 (視線.csv から読み込み) ----------
try:
    # 視線.csvを読み込み（1行目:時刻, 2行目:x座標）
    # ヘッダーなし (header=None) として読み込み、列名を指定 (names)
    gaze_df = pd.read_csv("視線xと時刻と瞼.csv", header=None, names=["timestamp", "gaze_x","left_dist"])
    print(f"✅ gaze_df (視線xと時刻.csv) 読み込み完了: {len(gaze_df)}行")

except FileNotFoundError:
    print("❌ エラー: '視線xと時刻と瞼.csv' が見つかりません。ファイルが存在することを確認してください。")
    # 代替データで処理を続行したい場合はここで定義
    # gaze_df = pd.DataFrame({"timestamp": [100, 200, 300], "gaze_x": [500, 500, 500]})
    exit() # ファイルがない場合は終了

# ---------- 2. char_dfの作成 (文字.csv から読み込み) ----------
try:
    # 文字.csvを読み込み（1行目:文字, 2行目:位置情報）
    # ヘッダーなし (header=None) として読み込み、列名を指定 (names)
    char_df = pd.read_csv("文字と座標.csv", header=None, names=["char", "x_center"])
    # 必要に応じてデータ型を変換
    char_df["x_center"] = char_df["x_center"].astype(float)
    print(f"✅ char_df (文字と座標.csv) 読み込み完了: {len(char_df)}文字")

except FileNotFoundError:
    print("❌ エラー: '文字と座標.csv' が見つかりません。ファイルが存在することを確認してください。")
    # 代替データで処理を続行したい場合はここで定義
    # char_df = pd.DataFrame({"char": ["あ", "い", "う"], "x_center": [100, 200, 300]})
    exit() # ファイルがない場合は終了
except pd.errors.ParserError:
    print("❌ エラー: '文字と座標.csv' のフォーマットが正しくありません。列数や区切り文字を確認してください。")
    exit()

# delta_left_dist: left_dist の差分 (距離の変化量)
delta_left_dist = gaze_df['left_dist'].diff().values

# delta_time: timestamp の差分 (時間の間隔)
# timestamp はミリ秒単位と仮定
delta_time = gaze_df['timestamp'].diff().values
epsilon = 1e-9 # ゼロ除算を避けるための微小量
with np.errstate(divide='ignore', invalid='ignore'):
    # 距離の差分を時間の差分で割る
    # delta_timeが非常に小さい（0に近い）場合は、結果を 0.0 とします。
    dist_speed_before = np.divide(
        delta_left_dist, 
        delta_time, 
        out=np.zeros_like(delta_left_dist, dtype=float), 
        where=np.abs(delta_time) > epsilon
    )
dist_speed_sec = dist_speed_before * 1000.0
gaze_df['dist_speed_calc'] = dist_speed_sec
dist_speed = np.nan_to_num(gaze_df['dist_speed_calc'].values, nan=0.0)



# 範囲と滞在時間の初期化
char_df["x_start"] = char_df["x_center"] - 57
char_df["x_end"] = char_df["x_center"] + 57
char_df["duration_ms"] = 0



print(f"✅ char_df 読み込み完了: {len(char_df)}文字")

# ---------- 3. 滞在時間の集計 ----------
count=0
FLAG_DURATION = 338.33  # ms　瞬きの継続時間
bring=0 #瞬きしているかのフラグ
bring_array=[]
latest_flag_interval = None # latest_flag_intervalをNoneで初期化
for i in range(len(gaze_df) - 1):
    t1, x1 = gaze_df.iloc[i]["timestamp"], gaze_df.iloc[i]["gaze_x"]
    t2 = gaze_df.iloc[i + 1]["timestamp"]
    duration = abs(t2 - t1)
    matched = False

    min_dist = float("inf")
    target_idx = None

    for idx, row in char_df.iterrows():
        dist = abs(x1 - row["x_center"])
        if dist < min_dist:
            min_dist = dist
            target_idx = idx


    # もし直前までに区間が宣言されていて、今のデータがその区間内ならフラグ
    if latest_flag_interval is not None:
        start, end = latest_flag_interval
        if start <=gaze_df.iloc[i]["timestamp"] <= end : 
            bring=1 #瞬き中のフラグ


    # speed/left_dist条件を満たしたら、新しい区間で上書き
    if ((dist_speed[i] >= 40) or (dist_speed[i] <= -40)) and (gaze_df.iloc[i]["left_dist"] <= 7):
        if latest_flag_interval is None or gaze_df.iloc[i]["timestamp"] > latest_flag_interval[1]:
            start = gaze_df.iloc[i]["timestamp"]
            end = gaze_df.iloc[i]["timestamp"] + FLAG_DURATION
            latest_flag_interval = (start, end)  # ← 最新の区間で上書き
            bring=1 #瞬き中のフラグ

    if bring==0 and target_idx is not None:
        char_df.at[target_idx, "duration_ms"] += duration

    bring_array.append(bring) #確認で出力するための瞬きフラグ
    if bring==1:
        count+=1
    bring=0



   
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

bring_series = pd.Series(bring_array, name="bring") # ★ 2. Seriesに変換し、列名 (header) を指定

# CSVに出力（index=Falseで左側の行番号（インデックス）を除外、header=Trueで列名を出力）
bring_series.to_csv("ヒートマップ時の視線情報out.csv", index=False, header=True, encoding="utf-8-sig")
print("ヒートマップ時の視線情報out.csvとして出力しました。")
print("count",count)