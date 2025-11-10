import pandas as pd
import numpy as np


# CSV読み込み
df = pd.read_csv("made.csv")
moji_df = pd.read_csv("moji1.csv")

# もとのmoji_dfに自動でline列を付与する
moji_df = moji_df.sort_values(by=["y", "x"]).reset_index(drop=True)
threshold = 20   # 行のy間隔（データにより調整）

lines = [0]
current_line = 0
for i in range(1, len(moji_df)):
    if abs(moji_df.loc[i, "y"] - moji_df.loc[i-1, "y"]) > threshold:
        current_line += 1
    lines.append(current_line)
moji_df["line"] = lines

line_df = moji_df.groupby("line")["y"].mean().reset_index()


#滞在時間
stay_time = {i: 0.0 for i in range(len(moji_df))}
#注視回数
count = {i: 0 for i in range(len(moji_df))}




# 時刻差分（ms→秒換算）  
dt = df['time'].diff() / 1000

# left_distの差分
dd = df['left_dist'].diff()
# 速度算出（初期値はnan）
df['speed'] = dd / dt

# x座標の移動速度
dx = df['x'].diff()
df['x_speed'] = dx / dt

# 最初はフラグを全部0
df['flag'] = 0




#### 瞬き除去 start##############################

FLAG_DURATION = 338.33  # ms
future_flags = []
# 最新のフラグ区間（なければNone）
latest_flag_interval = None


for i in range(1, len(df)):
    now_time = df.loc[i, 'time']
    
    # もし直前までに区間が宣言されていて、今のデータがその区間内ならフラグ
    if latest_flag_interval is not None:
        start, end = latest_flag_interval
        if start <= now_time <= end:
            df.at[i, 'flag'] = 1
            continue


    # speed/left_dist条件を満たしたら、新しい区間で上書き
    if ((df.loc[i, 'speed'] >= 50) or (df.loc[i, 'speed'] <= -50)) and (df.loc[i, 'left_dist'] <= 7):
        start = now_time
        end = now_time + FLAG_DURATION
        latest_flag_interval = (start, end)  # ← 最新の区間で上書き
        df.at[i, 'flag'] = 1

##########瞬き除去end###################################

"""
##########改行除去start###################################
# 条件A: x_speedが-150以下
after_B_flag = False
move=0
kaigyo=0

#A_idx = df.index[df['x_speed'] <= -150]

for idx in range(1, len(df)):
    A = df.at[idx-1, 'x_speed']
    B = df.at[idx, 'x_speed']

    # すでにB以降で継続中の場合
    if after_B_flag:
        if B > 0:
            after_B_flag = False  # x_speedが正になったら解除、フラグ付けない
            kaigyo=0
        else:
            df.at[idx, 'flag'] = 1  # 0以下の間だけフラグ付与
            move+= df.at[idx-1, 'x']-df.at[idx, 'x']
            if B<=-3000 and kaigyo==0:
                df.at[idx, 'flag'] = 2#改行であることの証拠
                kaigyo=1
            continue  # 下のifには入らず、次のループへ



    # 条件：Aが-150以下、かつ (B-A)>=-1000
    if (A <= -150) and ((B - A) <= -1000):
        df.at[idx-1, 'flag'] = 1  # Aにフラグ
        df.at[idx, 'flag'] = 1    # Bにフラグ
        after_B_flag = True
        move=df.at[idx-2, 'x']-df.at[idx-1, 'x']
        move+= df.at[idx-1, 'x']-df.at[idx, 'x']
    
    


##########改行除去end###################################
"""




##########文字と視線のつなぎstart###################################
#→ｙ軸で一番近い行をみつけ、そのあとにｘ座標を試す

prev_idx = None      # 前回の注視文字インデックス
prev_time = None     # 前回の時刻

for i, row in df.iterrows():
    gaze_x = row['x']
    gaze_y = row['y']
    t = row['time']

    # 距離条件を満たす文字を抽出
    # 1. y座標が一番近い行を見つける
    y_diffs = np.abs(line_df["y"] - gaze_y)
    if (y_diffs <= 60).any():
        nearest_line_idx = y_diffs.idxmin()   # 行インデックス
        line_y = line_df.loc[nearest_line_idx, "y"]

        # 2. その行に属する文字だけに絞る
        line_mojis = moji_df[moji_df["line"] == nearest_line_idx]

        # 3. その中でx座標が近い文字を探す
        x_diffs = np.abs(line_mojis["x"] - gaze_x)
        if (x_diffs <= 13.5).any():
            nearest_char_idx = x_diffs.idxmin()
            moji_idx = nearest_char_idx  # ←これだけにする！

            count[moji_idx] += 1

            if prev_idx is not None:
                stay_time[prev_idx] += t - prev_time

            prev_idx = moji_idx
            prev_time = t

# 出力
#for i, row in moji_df.iterrows():
    #print(f"{row['moji']}: 注視回数 {count[i]}, 合計滞留時間 {stay_time[i]:.2f} ms")

##########文字と視線のつなぎend###################################

df.to_csv("madeout.csv", index=False, encoding='utf-8-sig')