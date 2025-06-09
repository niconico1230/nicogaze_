import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.spatial import cKDTree
import matplotlib.font_manager as fm

# 日本語フォントを指定（例：Windows）
plt.rcParams['font.family'] = 'MS Gothic'  # Windows標準

# === 1. 入力（仮データ） ===
gaze_x = np.array([166.2466921, 204.7973334, 204.9154162, 237.2043159, 239.0059286, 272.0114284, 276.2618194, 291.3884427, 302.4838238, 304.3103446, 307.4546749, 303.8332949, 299.3821016, 323.0864381, 349.5994263, 368.6642173, 386.2335319, 377.7172258, 403.1428532, 499.3464077, 542.8625748, 565.2541682, 607.2898023, 657.1870955, 689.9316322, 717.6697439, 730.1351142, 749.8345529, 715.0140923, 759.619627, 758.9362123, 770.3322534, 782.6905252, 786.0371811, 786.2548453, 790.3163661, 840.2867173, 861.3738629, 870.0743855, 866.8669987, 857.6134361, 840.6705009, 904.4660278, 898.3723293, 914.3302291, 903.5817406, 878.6918764, 900.7951718, 927.8194703, 950.0766786, 963.2212686], dtype=np.float32)  # 視線x
char_x = np.array([303.3, 330.0, 354.0, 378.0, 401.8, 422.6, 443.6, 464.5, 488.3, 514.9, 541.6, 566.3, 586.6, 608.8, 632.5, 656.2, 682.9, 706.6, 730.4, 754.2, 774.8, 798.3, 821.2, 840.0, 859.3, 882.6, 909.3, 932.6, 952.6], dtype=np.float32)  # 文字のx中心

# y座標は無関係（1行分なので）

# === 2. 1次分数変換 ===
def projective_x(x, a, b, c, d):
    epsilon = 1e-6
    return (a * x + b) / (c * x + d + epsilon)

# === 3. 誤差関数（x'と最も近い文字xとの差の平均） ===
# 目的関数に範囲差ペナルティを加える
range_weight = 2.0# 重みは実験で調整

def objective(params):
    a, b, c, d = params
    x_trans = projective_x(gaze_x, a, b, c, d)
    tree = cKDTree(char_x.reshape(-1, 1))
    distances, _ = tree.query(x_trans.reshape(-1, 1))
    
    range_penalty = np.abs((x_trans.max() - x_trans.min()) - (char_x.max() - char_x.min()))
    return np.mean(distances) + range_weight * range_penalty
# === 4. 最適化 ===
initial_params = [1.0, 0.0, 0.0, 1.0]  # 初期値（恒等変換）
bounds = [(-10, 10), (-100, 100), (-0.1, 0.1), (0.5, 2.0)]

result = minimize(objective, initial_params, bounds=bounds, method='L-BFGS-B')

# === 5. 結果適用 ===
a, b, c, d = result.x
transformed_x = projective_x(gaze_x, a, b, c, d)

print(f"最適パラメータ: a={a:.4f}, b={b:.2f}, c={c:.4f}, d={d:.2f}")
print(f"補正前の範囲: {gaze_x.min():.1f} ~ {gaze_x.max():.1f}")
print(f"補正後の範囲: {transformed_x.min():.1f} ~ {transformed_x.max():.1f}")
print(f"文字xの範囲: {char_x.min():.1f} ~ {char_x.max():.1f}")
# === 追加：修正後の視線座標を表示 ===
print("\n補正後の視線x座標（transformed_x）:")
for i, val in enumerate(transformed_x):
    print(f"{val:.2f}")

# === 6. 可視化 ===
plt.figure(figsize=(8, 3))
plt.scatter(char_x, np.zeros_like(char_x), c='blue', label='文字位置')
plt.scatter(gaze_x, np.ones_like(gaze_x), c='red', label='視線（補正前）')
plt.scatter(transformed_x, np.full_like(transformed_x, 2), c='green', label='視線（補正後）')
plt.yticks([])
plt.legend()
plt.title("視線のx座標補正（射影変換）")
plt.grid(True)
plt.show()

