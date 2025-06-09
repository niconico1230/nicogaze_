import numpy as np
from scipy.spatial.distance import cdist
from dtaidistance import dtw_ndim
from DATAeye import numbers_list2
from DATAeye2 import y_list2
from DATAmojix import x_list
from DATAmojiy import y_list

# 仮の視線データ（x, y座標）
eye_tracking_data = np.column_stack((np.array(numbers_list2), np.array(y_list2)))  # (N, 2) の形

# 仮の文字位置（x, y座標）
#text_positions_x = np.array([50, 150, 250, 350, 450, 550, 650, 750, 850, 950])  # x座標
#text_positions_y = np.array([144.4, 184.4, 224.4, 264.4, 304.4, 344.4, 384.4, 424.4, 464.4, 504.4])  # y座標
text_positions = np.column_stack((np.array(x_list), np.array(y_list)))  # (M, 2) の形

# ユークリッド距離行列の作成（x, y両方を考慮）
distance_matrix = cdist(eye_tracking_data, text_positions, metric='euclidean')

# DTW の適用（2次元データ用）
path = dtw_ndim.warping_path(eye_tracking_data, text_positions)  # DTWで最適な対応を計算


# 修正後の視線データ（y座標のみを抽出）
corrected_y_positions = [text_positions[p[1]][1] for p in path]  # y座標のみ取得

# y座標を1行ずつ出力
for y in corrected_y_positions:
    print(y)