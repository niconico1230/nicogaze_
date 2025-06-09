import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from DATAmojix import x_list 
from DATAmojix import moji_list


# 日本語フォントを指定（例：Windows）
plt.rcParams['font.family'] = 'MS Gothic'  # Windows標準

def x_axis_projective_transform_rect_based(gaze_x_list, char_x_list):
    """
    射影変換によって gaze_x_list を char_x_list に合わせて補正する。
    x軸のみに特化し、y=0として2次元射影変換を行う。
    """

    if len(gaze_x_list) < 4 or len(char_x_list) < 4:
        raise ValueError("少なくとも4点ずつ必要です。")

    # gaze/charの最小値・最大値を取って矩形の両端とする
    gaze_min, gaze_max = min(gaze_x_list), max(gaze_x_list)
    char_min, char_max = min(char_x_list), max(char_x_list)

    # 4点：左端・右端、それぞれに固定y=±1を付けて仮想的な矩形を作成
    src_pts = np.array([
        [gaze_min, -1],
        [gaze_max, -1],
        [gaze_max,  1],
        [gaze_min,  1],
    ], dtype=np.float32)

    dst_pts = np.array([
        [char_min, -1],
        [char_max, -1],
        [char_max,  1],
        [char_min,  1],
    ], dtype=np.float32)

    # 射影変換行列の計算
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # 補正対象のgaze座標を (x, 0) にして変換
    gaze_pts = np.array([[x, 0] for x in gaze_x_list], dtype=np.float32).reshape(-1, 1, 2)
    transformed_pts = cv2.perspectiveTransform(gaze_pts, matrix)

    corrected_x = [pt[0][0] for pt in transformed_pts]
    return corrected_x

# ==== 使用例 ====
gaze_x = x_list
char_x = moji_list
transformed_x = x_axis_projective_transform_rect_based(gaze_x, char_x)



# === 修正前後のx座標の範囲を表示 ===
print("\n=== x座標の範囲比較 ===")
print(f"修正前: 最小値 = {min(gaze_x):.2f}, 最大値 = {max(gaze_x):.2f}")
print(f"修正後: 最小値 = {min(transformed_x):.2f}, 最大値 = {max(transformed_x):.2f}")
print(f"正解値: 最小値 = {min(char_x):.2f}, 最大値 = {max(char_x):.2f}")
print("\n補正後の視線x座標（transformed_x）:")
for i, val in enumerate(transformed_x):
    print(f"{val:.2f}")


# === 可視化 ===
plt.figure(figsize=(10, 3))
plt.scatter(char_x, np.zeros_like(char_x), c='blue', label='文字位置')
plt.scatter(gaze_x, np.ones_like(gaze_x), c='red', label='視線（補正前）')
plt.scatter(transformed_x, np.full_like(transformed_x, 2), c='green', label='視線（補正後）')
plt.yticks([])
plt.legend()
plt.title("x軸のみの射影変換（矩形範囲ベース）")
plt.grid(True)
plt.tight_layout()
plt.show()