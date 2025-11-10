import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'MS Gothic'   # または 'Meiryo', 'Yu Gothic'



# 例: 0~300:1行目, 301~450:2行目, ... をdictで定義
def get_line_idx(idx):
    # 0-based index
    if 1 <= idx <= 130:
        return 1
    elif  138<= idx <= 251:
        return 2
    elif 259 <= idx <=425:
        return 3
    elif 436 <= idx <= 559:
        return 4
    elif 568 <= idx <= 741:
        return 5
    elif 748 <= idx <= 859:
        return 6
    elif 869 <= idx <= 975:
        return 7
    elif 983 <= idx <= 1120:
        return 8
    elif 1127 <= idx <= 1265:
        return 9
    elif  1273 <= idx <= 1355:
        return 10
    else:
        return -1  # 範囲外
    


# CSV読み込み
df = pd.read_csv("made.csv")
moji_df = pd.read_csv("moji.csv")

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

FLAG_DURATION = 325.3  # ms
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

##########瞬き除去end###################################


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
            if move>=504 and kaigyo==0:
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


# 5点移動平均（最初の4つは空白）
# 5点移動平均・sflag計算
results = []
ranges = list(range(10, 301, 10))  # -40, -20, 0, ..., 280, 300
lower = -250  # 下限を固定

for a in range(5, 16):

    # x_speedの「差分」を計算
    dx_speed = df['x_speed'].diff().fillna(0)  # 最初は0で埋める

    for upper in ranges[1:]:
        sflag = [0] * len(df)
        i = 0
        while i < len(df) - a:
            window = df['x_speed'].iloc[i:i+a+1]  # x_speedの区間（a+1個）
            flag_window = df['flag'].iloc[i:i+a+1]
            # フラグ判定
            if ((flag_window == 1) | (flag_window == 2)).any():
                i += 1
                continue
            # x_speedの絶対値がupper未満の個数がa-2個以上
            if (window.abs() < upper).sum() >= (a-2):
                for j in range(i, i+a+1):
                    sflag[j] = 1
                i += a+1  # 重複避けるならa+1進める
            else:
                i += 1
        sflag = ['' if idx < a else sflag[idx] for idx in range(len(df))]
        df['sflag'] = sflag



        moji_df['sflag'] = 0
        for idx, row in df[df['sflag'] == 1].iterrows():
            gaze_x = row['x']
            line_idx = get_line_idx(idx)
            if line_idx == -1:
                continue
            moji_line = moji_df[moji_df['line'] == line_idx]
            if len(moji_line) == 0:
                continue
            nearest_idx = (moji_line['x'] - gaze_x).abs().idxmin()
            moji_df.at[nearest_idx, 'sflag'] = 1

        # --- 評価指標 ---
        pred = moji_df['sflag'].fillna(0).astype(int)
        true = moji_df['true_label'].fillna(0).astype(int)

        TP = ((pred == 1) & (true == 1)).sum()
        FP = ((pred == 1) & (true == 0)).sum()
        FN = ((pred == 0) & (true == 1)).sum()
        TN = ((pred == 0) & (true == 0)).sum()

        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall    = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        results.append([a,upper, precision, recall, f1, TP, FP, FN, TN])

import pandas as pd
import matplotlib.pyplot as plt

result_df = pd.DataFrame(results, columns=['a', 'upper', 'precision', 'recall', 'f1', 'TP', 'FP', 'FN', 'TN'])


# f1が最大の行を取得
best_row = result_df.loc[result_df['f1'].idxmax()]
best_a = int(best_row['a'])
best_upper = best_row['upper']
best_f1 = best_row['f1']
best_precision = best_row['precision']
best_recall = best_row['recall']

print("=== F1が最大となるパラメータ ===")
print(f"連続回数: {best_a}")
print(f"速度閾値: {best_upper}")
print(f"F1-score: {best_f1:.3f}")
print(f"Precision: {best_precision:.3f}")
print(f"Recall: {best_recall:.3f}")

# （必要ならbest_rowごとprint(best_row)でもOK）

# オプション：heatmap的な可視化もできる
import seaborn as sns
pivot = result_df.pivot(index='a', columns='upper', values='f1')
plt.figure(figsize=(12,6))
sns.heatmap(pivot, annot=True, fmt=".2f", cmap="viridis")
plt.title("F1-score heatmap (連続回数 vs 速度閾値)")
plt.xlabel("速度閾値")
plt.ylabel("連続回数")
plt.tight_layout()
plt.show()


# mojiout.csvとして保存
moji_df.to_csv('mojiout.csv', index=False)

# madeout.csvも保存
out_df = df[['time','x','y', 'flag', 'sflag']]
out_df.to_csv('madeout.csv', index=False)


