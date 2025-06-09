import numpy as np
from scipy.spatial.distance import cdist
from dtaidistance import dtw_ndim
from DATAeye import numbers_list2
#dtwとは別で距離を求めている

# 仮の視線データ（y座標）
#eye_tracking_data = np.array([[10], [12], [14], [18], [20], [30], [32], [35], [40]])
eye_tracking_data=np.array(numbers_list2).reshape(-1, 1)  # 形状: (N, 1)

# 仮の文字位置（y座標）
text_positions = np.array([144.4,184.4,224.4,264.4,304.4,344.4,384.4,424.4,464.4,504.4]).reshape(-1, 1)  # ← ここで修正

# ユークリッド距離行列の作成
distance_matrix = cdist(eye_tracking_data, text_positions, metric='euclidean')

# DTW の適用（ND次元データ用）
path = dtw_ndim.warping_path(eye_tracking_data.flatten(), text_positions.flatten())  # 必須引数を追加

#print("距離行列:\n", distance_matrix)
#print("DTW のマッチングパス:", path)
# 修正後の視線データを適用
corrected_eye_tracking = np.array([text_positions[p[1]] for p in path])

# 1行ずつ出力
for value in corrected_eye_tracking:
    print(value)