import numpy as np
from dtaidistance import dtw
from D_gyou2 import gyou_list2
#DTWで距離も求めている

# 仮の視線データ（y座標）
#eye_tracking_data = np.array([10, 12, 14, 18, 20, 30, 32, 35, 40])

# 仮の文字位置（y座標）
text_positions = np.array([170.0, 210.0, 250.0, 290.0, 330.0, 370.0, 410.0, 450.0, 490.0, 530.0])

# DTW による距離計算とマッチング
path = dtw.warping_path(np.array(gyou_list2) , text_positions)

# 修正後の視線データ
corrected_eye_tracking = np.array([text_positions[p[1]] for p in path])

#print("補正前の視線データ:", numbers_list2)
#print("補正後の視線データ:", corrected_eye_tracking)
# ✅ ファイルに出力
with open("output.txt", "w", encoding="utf-8") as f:
    for value in corrected_eye_tracking:
        f.write(f"{value}\n")

#for value in corrected_eye_tracking:
 #   print(value)