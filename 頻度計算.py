import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'MS Gothic'   # または 'Meiryo', 'Yu Gothic'

# 1. データ定義
# CSVファイル読み込み
df = pd.read_csv("fre.csv")

# ソート（頻度の昇順）
df = df.sort_values("fre")

# 3. 全体のmichi数（Recall計算に必要）
total_michi = df["michi"].sum()

# 4. 閾値ごとに指標を計算
thresholds = sorted(df["fre"].unique())
precision_list = []
recall_list = []
f1_list = []

for th in thresholds:
    predicted_unknown = df[df["fre"] <= th]  # 閾値以下を未知語と予測
    TP = predicted_unknown["michi"].sum()
    FP = predicted_unknown["kichi"].sum()
    FN = df[df["fre"] > th]["michi"].sum()

    # Precision
    if TP + FP > 0:
        precision = TP / (TP + FP)
    else:
        precision = None

    # Recall
    if total_michi > 0:
        recall = TP / total_michi
    else:
        recall = None

    # F1スコア
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None

    # 保存
    precision_list.append(precision)
    recall_list.append(recall)
    f1_list.append(f1)

# 5. グラフ描画
plt.figure(figsize=(8, 5))
plt.plot(thresholds, precision_list, label="Precision")
plt.plot(thresholds, recall_list, label="Recall")
plt.plot(thresholds, f1_list, label="F1 Score")

plt.xlabel("頻度閾値（以下を未知語と判定）")
plt.ylabel("指標値")
plt.title("頻度による未知語判定の精度・再現率・F1スコア")
plt.grid(True)
plt.ylim(0, 1.05)
plt.legend()
plt.show()


# 6. 最良の閾値を出力（F1最大のとき）
max_f1 = max((f for f in f1_list if f is not None))
best_idx = f1_list.index(max_f1)
best_threshold = thresholds[best_idx]
best_precision = precision_list[best_idx]
best_recall = recall_list[best_idx]

# 7. 結果表示
print(f"📌 最もF1スコアが高かった閾値: {best_threshold}")
print(f"　Precision: {best_precision:.3f}")
print(f"　Recall:    {best_recall:.3f}")
print(f"　F1 Score:  {max_f1:.3f}")