import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
from DATAeye import eyelist
from DATAmoji import mojilist


# 文字位置データをマッピング
char_dict = {char: (x, y) for char, x, y in mojilist}

# 視線データの前処理
gaze_data = np.array(eyelist)
times = gaze_data[:, 0]
gaze_x = gaze_data[:, 1]
gaze_y = gaze_data[:, 2]

# 正規化（視線座標を0~1にスケーリング）
scaler_x = MinMaxScaler()
scaler_y = MinMaxScaler()
gaze_x_scaled = scaler_x.fit_transform(gaze_x.reshape(-1, 1))
gaze_y_scaled = scaler_y.fit_transform(gaze_y.reshape(-1, 1))

# LSTMの入力に合わせるため、視線データを時間ステップごとに切り出す
sequence_length = 3  # 例えば3つのタイムステップで予測する
X, y = [], []
for i in range(len(gaze_data) - sequence_length):
    X.append(np.column_stack((gaze_x_scaled[i:i+sequence_length], gaze_y_scaled[i:i+sequence_length])))
    # 各文字に対して視線滞在時間を予測するため、文字の位置に対する滞在時間を計算
    #y.append([1 if (char_x-20 <= gaze_x[i] <= char_x+20) and (char_y-50 <= gaze_y[i] <= char_y+50) else 0 for _, char_x, char_y in mojilist])
    # ユークリッド距離を計算して最も近い文字を見たとする
    gaze_point = np.array([gaze_x[i], gaze_y[i]])  # 現在の視線位置
    min_distance = float('inf')
    closest_char_idx = -1

    for idx, (_, char_x, char_y) in enumerate(mojilist):
        char_point = np.array([char_x, char_y])
        distance = np.linalg.norm(gaze_point - char_point)  # ユークリッド距離

        if distance < min_distance:
            min_distance = distance
            closest_char_idx = idx  # 最も近い文字のインデックスを更新

    # ラベルを作成（すべて0、最も近い文字だけ1）
    label = [0] * len(mojilist)
    label[closest_char_idx] = 1
    y.append(label)

    
X = np.array(X)
print(X)
y = np.array(y)
print("y",y)

# PyTorchのテンソルに変換
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)

# データローダーを作成
dataset = TensorDataset(X_tensor, y_tensor)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# LSTMモデルの定義
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, (hn, cn) = self.lstm(x)
        out = self.fc(hn[-1])  # 最後の隠れ状態を使って予測
        return out

# モデルのインスタンス化
input_size = 2  # x, yの2次元座標
hidden_size = 50  # LSTMの隠れ状態のユニット数
output_size = len(mojilist)  # 文字数分の出力

model = LSTMModel(input_size, hidden_size, output_size)

# 損失関数と最適化手法
criterion = nn.BCEWithLogitsLoss()  # 複数のクラスに対する二項交差エントロピー損失
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# モデルの学習
epochs = 10
for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in dataloader:
        optimizer.zero_grad()

        # フォワードパス
        outputs = model(inputs)

        # 損失の計算
        loss = criterion(outputs, labels)
        
        # バックプロパゲーションと最適化
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()

    print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(dataloader):.4f}")

# 予測
model.eval()
with torch.no_grad():
    for inputs, labels in dataloader:
        
        outputs = model(inputs)
        _, predicted = torch.max(outputs, 1)
        print(f"Predicted: {predicted.numpy()}")