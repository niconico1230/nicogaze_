import pandas as pd
import numpy as np
import pickle
from fugashi import Tagger
import matplotlib.pyplot as plt
import sys
from scipy.stats import trim_mean

tagger = Tagger()
plt.rcParams['font.family'] = 'MS Gothic'   # または 'Meiryo', 'Yu Gothic'

# 1. ファイル読み込み
df = pd.read_csv("made.csv")
moji_df = pd.read_csv("moji.csv")

# 2. 文字ごとに「line」列を自動で付与（行ごとの位置調整、ここは元コードそのまま）
moji_df = moji_df.sort_values(by=["y", "x"]).reset_index(drop=True)
threshold = 20
lines = [0]
current_line = 0
for i in range(1, len(moji_df)):
    if abs(moji_df.loc[i, "y"] - moji_df.loc[i-1, "y"]) > threshold:
        current_line += 1
    lines.append(current_line)
moji_df["line"] = lines
line_df = moji_df.groupby("line")["y"].mean().reset_index()

# 3. 文字ごとの「滞留時間」「注視回数」計算
stay_time = {i: 0.0 for i in range(len(moji_df))}
count = {i: 0 for i in range(len(moji_df))}

dt = df['time'].diff() / 1000
dd = df['left_dist'].diff()
df['speed'] = dd / dt
dx = df['x'].diff()
df['x_speed'] = dx / dt
df['flag'] = 0

# --- 瞬き・改行除去等（ここは省略、上記の処理と同じまま） ---
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
    if ((df.loc[i, 'speed'] >= 40) or (df.loc[i, 'speed'] <= -40)) and (df.loc[i, 'left_dist'] <= 7):
        start = now_time
        end = now_time + FLAG_DURATION
        latest_flag_interval = (start, end)  # ← 最新の区間で上書き
        df.at[i, 'flag'] = 1

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


# --- 改行・瞬きフラグ付きでCSV出力 ---
df.to_csv("madeout.csv", index=False, encoding="utf-8-sig")  # もとのmade.csvにflag列を書き足した形で保存



####################################################
# 改行flag==2が最初に現れるインデックスを取得
first_kaigyo_idx = df.index[df['flag'] == 2]
if len(first_kaigyo_idx) > 0:
    first_kaigyo = first_kaigyo_idx[0]
    t0 = df.loc[0, 'time']
    sub_df = df.loc[:first_kaigyo-1].copy()
    mask = (sub_df['flag'] != 1) & (sub_df['time'] > t0 + 500)
    y_vals = sub_df.loc[mask, 'y'].values
    if len(y_vals) > 0:
        mean_y = trim_mean(y_vals, proportiontocut=0.05)  # 10%トリム平均（両端5%ずつカット）
        median_y = np.median(y_vals)#中央値
    else:
        mean_y = None
else:
    mean_y = None

print("トリム平均（flag==1、開始500ms以内除外、両端5%カット）:", mean_y)

# mean_y（もしくはmedian_y）をmoji.csvの1行目（最初の文字）のy座標から引く
moji_first_y = moji_df.loc[0, 'y']  # moji.csvの最初のy座標

diff_y = moji_first_y - mean_y  # 平均値との差分
print("moji.csv最初のy - mean_y =", diff_y)#この差分をｙに足していく

######################################################







# 4. 文字ごと注視データ集計（ここも元コードのまま）
prev_idx = None
prev_time = None
prev_flag = 0
look=0 #そのループで対応する文字が見つかったか　１がみつけた　
one_line_mode = True  # 1行目モード


for i, row in df.iterrows():
    gaze_x = row['x']
    gaze_y = row['y']
    t = row['time']

     # 直前データへの加算を必ず先頭で実施
    if prev_idx is not None and prev_flag != 1 :  # 前のデータがあり、除外対象orデータが見つかっていない　でないならば
        stay_time[prev_idx] += t - prev_time

    # flag==2が出たら以降はone_line_mode=Falseに切り替え
    if row['flag'] == 2:
        one_line_mode = False

    if one_line_mode:
        if row['flag'] == 0:
            # 1行目モードではline==0のみを対象とする
            line_mojis = moji_df[moji_df["line"] == 0]
            x_diffs = np.abs(line_mojis["x"] - gaze_x)
            if (x_diffs <= 13.5).any():
                nearest_char_idx = x_diffs.idxmin()
                moji_idx = line_mojis.index[nearest_char_idx]
                count[moji_idx] += 1
                prev_idx = moji_idx
                prev_flag = 0
                look = 1
        if row['flag'] == 1 or row['flag'] == 2 or look == 0:
            prev_flag = 1
    else:
        # 2行目以降（y補正あり）: 通常通りy, x両方で行+文字判定
        if mean_y is not None and diff_y is not None:
            gaze_y_corr = gaze_y + diff_y
        else:
            gaze_y_corr = gaze_y

        if row['flag'] == 0:
            y_diffs = np.abs(line_df["y"] - gaze_y_corr)
            if (y_diffs <= 60).any():
                nearest_line_idx = y_diffs.idxmin()
                line_mojis = moji_df[moji_df["line"] == nearest_line_idx]
                x_diffs = np.abs(line_mojis["x"] - gaze_x)
                if (x_diffs <= 13.5).any():
                    nearest_char_idx = x_diffs.idxmin()
                    moji_idx = nearest_char_idx  # ←これでmoji_dfで一意にアクセスできる
                    count[moji_idx] += 1
                    prev_idx = moji_idx
                    prev_flag = 0
                    look = 1
        if row['flag'] == 1 or row['flag'] == 2 or look == 0:
            prev_flag = 1

    prev_time = t
    look = 0




# 5. 必要な単語情報のため形態素解析


line_text = "".join(moji_df["moji"].tolist())  # moji_dfからテキスト生成
with open("word_index_short.pkl", "rb") as f:
    word_index_short = pickle.load(f)

# 正解ラベルの読込み（moji_dfに「難しい単語か」のラベル列を追加する想定）
# moji_df["true_label"] ... ここは用意されているものを使う（たとえば0/1）

# 6. 単語単位で評価
def make_words():
    words = []
    char_pos = 0
    true_flag = moji_df["true_label"].tolist()  # 事前にmoji_dfへ正解ラベル追加しておく想定
    for token in tagger(line_text):
        surface = token.surface
        length = len(surface)
        start = char_pos
        end = char_pos + length - 1
        raw_lemma = token.feature[7] if len(token.feature) > 7 else surface
        base = raw_lemma.split("-")[0]
        if base == "*" or base == "":
            base = surface
        pos = token.feature[0]
        words.append({
            "word": surface,
            "base": base,
            "pos": pos,
            "start": start,
            "end": end
        })
        char_pos += length
    for w in words:
        char_indices = range(w["start"], w["end"]+1)
        true = 0
        for idx in char_indices:
            if idx < len(true_flag) and true_flag[idx] == 1:
                true = 1
                break
        w["true"] = true
    return words

# 7. パラメータ範囲ループで精度評価
th_range = list(range(300, 1001, 100))
freq_range = list(range(120, 9, -10))  # → [120,110,100,…,10]
#freq_range = list(range(10, 121, 10))
F1_mat = np.zeros((len(freq_range), len(th_range)))
ACC_mat = np.zeros_like(F1_mat)
PREC_mat = np.zeros_like(F1_mat)
RECALL_mat = np.zeros_like(F1_mat)




for j, th in enumerate(th_range):
    words = make_words()

    # 滞留時間thで難しい文字フラグ作成（この時点ではfreq_thを使わない
    # 文字ごとに難しい文字フラグ（flagged_char）を作る
    flagged_char = [0] * len(moji_df)
    for idx in range(len(moji_df)):
        if stay_time.get(idx, 0) > th:
            # 横方向
            for d in range(-1, 2):
                ni = idx + d
                if 0 <= ni < len(moji_df):
                    flagged_char[ni] = 1
            # 縦方向
            x = moji_df.loc[idx, "x"]
            now_line = moji_df.loc[idx, "line"]
            lines = moji_df["line"].unique()
            for line in lines:
                if line != now_line and abs(line - now_line) == 1:
                    # 同じx座標・指定lineのすべての文字indexを取得
                    y_idx_list = moji_df[(moji_df["x"] == x) & (moji_df["line"] == line)].index
                    for y_idx in y_idx_list:
                        # さらにその中心+前後2文字にもフラグ
                        for d in range(-1, 2):
                            ni = y_idx + d
                            if 0 <= ni < len(moji_df):
                                flagged_char[ni] = 1

    # 単語ごと判定（flagged_charだけでpred=1/0仮付け）
    for w in words:
        if any(flagged_char[idx] for idx in range(w["start"], w["end"]+1)):
            w["pred"] = 1
        else:
            w["pred"] = 0

    # 頻度閾値ごとに評価（ここでだけpred=1→0に変更がある）
    for i, freq_th in enumerate(freq_range):
        for w in words:
            key = (w["base"], w["pos"])
            info = word_index_short.get(key)

            if info is not None:
                freq = info.get('frequency', 0)
            else:       
                freq = 0
            w["freq"] = freq  # ←ここで毎回格納！
                
            if w["pred"] == 1:
                if info is None or freq > freq_th:
                    w["pred"] = 0
        
        # ←評価値の計算・保存処理
        # 混同行列計算
        TP = FP = TN = FN = 0
        for w in words:
            pred = w["pred"]
            true = w["true"]
            if pred == 1 and true == 1:
                TP += 1
            elif pred == 1 and true == 0:
                FP += 1
            elif pred == 0 and true == 0:
                TN += 1
            elif pred == 0 and true == 1:
                FN += 1

        accuracy = (TP + TN) / (TP + FP + TN + FN) if (TP+FP+TN+FN) > 0 else 0
        precision = TP / (TP + FP) if (TP+FP) > 0 else 0
        recall = TP / (TP + FN) if (TP+FN) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision+recall) > 0 else 0
        fnr = FN / (TP + FN) if (TP + FN) > 0 else 0   # ★ココ追加
        fpr = FP / (FP + TN) if (FP + TN) > 0 else 0
        specificity = TN / (TN + FP) if (TN+FP) > 0 else 0


        # 保存
        F1_mat[i, j] = f1
        ACC_mat[i, j] = accuracy
        PREC_mat[i, j] = precision
        RECALL_mat[i, j] = recall

# --- 以降はグラフや出力は同じ構造でOK ---


        if freq_th==110:
            print("秒数閾値：",th,"　　頻度閾値",freq_th)

            print(f"正解（1）を正解（1）と判定（TP率/Recall）      : {recall:.3f}")
            print(f"正解（1）を不正解（0）と判定（FN率/FN/TP+FN）  : {fnr:.3f}")
            print(f"不正解（0）を不正解（0）と判定（TN率/Specificity）: {specificity:.3f}")
            print(f"不正解（0）を正解（1）と判定（FP率/FP/FP+TN）    : {fpr:.3f}")
            print(f"適合率（Precision）                               : {precision:.3f}")
            print(f"F1スコア                                        : {f1:.3f}")
            print(f"全体精度（Accuracy）                             : {accuracy:.3f}")


            print("\n【正解を不正解と判定した単語（偽陰性/FN）一覧】")
            for w in words:
                if w["true"] == 1 and w["pred"] == 0:
                    print(f'{w["word"]} （位置 {w["start"]}-{w["end"]}）')

            print("\n【不正解を正解と判定した単語一覧】")
            for w in words:
                if w["true"] == 0 and w["pred"] == 1:
                    print(f'{w["word"]} （位置 {w["start"]}-{w["end"]}）')

            print("\n\n")
    




# 出力例
#print("\n【文全体の正解と予測】")
#for w in words:
#    freq_str = f' (頻度補正)' if w.get("freq_override") else ""
#    print(f'{w["word"]} pred:{w["pred"]} true:{w["true"]}{freq_str}')


# Accuracy
"""
plt.figure(figsize=(12, 7))
for i, freq_th in enumerate(freq_range):
    plt.plot(th_range, ACC_mat[i, :], label=f'頻度閾値={freq_th}')
plt.xlabel('秒数の閾値（ms）')
plt.ylabel('Accuracy')
plt.title('頻度閾値ごとのAccuracy（折れ線グラフ）')
plt.legend(title='頻度閾値', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()
"""

# Precision
plt.figure(figsize=(12, 7))
for i, freq_th in enumerate(freq_range):
    plt.plot(th_range, PREC_mat[i, :], label=f'頻度閾値={freq_th}')
plt.xlabel('秒数の閾値（ms）')
plt.ylabel('Precision（適合率）')
plt.title('頻度閾値ごとのPrecision（折れ線グラフ）')
plt.legend(title='頻度閾値', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()

# Recall
plt.figure(figsize=(12, 7))
for i, freq_th in enumerate(freq_range):
    plt.plot(th_range, RECALL_mat[i, :], label=f'頻度閾値={freq_th}')
plt.xlabel('秒数の閾値（ms）')
plt.ylabel('Recall（再現率）')
plt.title('頻度閾値ごとのRecall（折れ線グラフ）')
plt.legend(title='頻度閾値', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()


# F1スコア
plt.figure(figsize=(12, 7))
for i, freq_th in enumerate(freq_range):
    plt.plot(th_range, F1_mat[i, :], label=f'頻度閾値={freq_th}')
plt.xlabel('秒数の閾値（ms）')
plt.ylabel('F1スコア')
plt.title('頻度閾値ごとのF1スコア（折れ線グラフ）')
plt.legend(title='頻度閾値', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()



# 必要なら最適組み合わせも出力
best_idx = np.unravel_index(F1_mat.argmax(), F1_mat.shape)
print(f"最大F1={F1_mat[best_idx]:.3f}（秒数閾値: {th_range[best_idx[1]]}, 頻度閾値: {freq_range[best_idx[0]]}）")




max_f1 = F1_mat.max()
indices = np.argwhere(F1_mat == max_f1)
for idx in indices:
    print(f"最大F1={max_f1:.3f}（秒数閾値: {th_range[idx[1]]}, 頻度閾値: {freq_range[idx[0]]}）")


# ---- ここまでが評価・グラフ出力などのメイン処理 ----

# moji_dfに各種フラグや注視データを追加
moji_df["count"] = pd.Series(count)
moji_df["stay_time"] = pd.Series(stay_time)
moji_df["flagged_char"] = flagged_char  # 直近ループのもの

# 必要なら単語ごとの難しい判定フラグも
moji_df["pred_word"] = 0
for w in words:
    if w["pred"] == 1:
        for idx in range(w["start"], w["end"] + 1):
            if 0 <= idx < len(moji_df):
                moji_df.at[idx, "pred_word"] = 1

# まず初期値（0またはNone）で列を追加
moji_df["word_freq"] = 0
# 単語ごとに、自分のカバー範囲すべてにfreqをセット
for w in words:
    for idx in range(w["start"], w["end"] + 1):
        if 0 <= idx < len(moji_df):
            moji_df.at[idx, "word_freq"] = w.get("freq", 0)


# 保存
moji_df.to_csv("mojiout.csv", index=False, encoding="utf-8-sig")
print("mojiout.csvとして出力しました。")