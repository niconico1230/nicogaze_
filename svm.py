import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from D_time import time_list
from D_x import x_list
from D_y import y_list
from D_gyou import gyou_list

# 辞書としてデータを作成
data = {
    'x_coord': x_list,
    'y_coord': y_list,
    'fixation_time': time_list,
    'break_timing': gyou_list
}
df = pd.DataFrame(data)
# データフレームを表示
print(df)

# 特徴量（X）とラベル（Y）を分離
X = df[['x_coord', 'y_coord', 'fixation_time']]
y = df['break_timing']

# データを訓練用とテスト用に分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# SVMモデルを定義
model = SVC(kernel='linear')

# モデルを訓練
model.fit(X_train, y_train)

# テストデータで予測
y_pred = model.predict(X_test)

# 精度を計算
accuracy = accuracy_score(y_test, y_pred)
print(f"モデルの精度: {accuracy * 100:.2f}%")

# 新しい視線データで改行タイミングを予測
new_data = np.array([[1000, 500, 1.2]])  # 例として視線データ
predicted_break = model.predict(new_data)
print(f"予測された改行タイミング: {predicted_break[0]}")
