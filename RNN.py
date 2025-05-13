import torch
import torch.nn as nn
import torch.optim as optim
from D_time import time_list
from D_x import x_list
from D_y import y_list
from D_gyou import gyou_list

from D_time2 import time_list2
from D_x2 import x_list2
from D_y2 import y_list2
from D_gyou2 import gyou_list2

# 特徴量: x, y, fixation_time（x座標, y座標, 注視時間）
data_list = list(zip(x_list, y_list, time_list))  # [(x, y, t), ...]
data_tensor = torch.tensor(data_list, dtype=torch.float32).unsqueeze(1)  # (サンプル数, 時間ステップ数=1, 特徴量数=3)

labels = torch.tensor(gyou_list, dtype=torch.float32)


# RNNモデルの定義
class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleRNN, self).__init__()
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(1, x.size(0), hidden_size)  # 初期の隠れ状態
        out, _ = self.rnn(x, h0)  # RNNの出力と隠れ状態
        out = self.fc(out[:, -1, :])  # 最後の時間ステップを使用
        return out

# モデルのパラメータ
input_size = 3  # 特徴量の数# x, y, fixation_time
hidden_size = 10  # 隠れ状態の次元数
output_size = 1  # 出力次元（改行タイミング: 0または1）

# モデルの初期化
model = SimpleRNN(input_size, hidden_size, output_size)

# 損失関数と最適化手法
criterion = nn.BCEWithLogitsLoss()  # 2値分類用の損失関数
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 訓練ループ
epochs = 100
for epoch in range(epochs):
    # 順伝播
    outputs = model(data_tensor)
    loss = criterion(outputs.squeeze(), labels)

    # 逆伝播と重みの更新
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')





# 特徴量 (x, y, time) を組み合わせてリストにする
new_data_list = list(zip(x_list2, y_list2, time_list2))  # [(x, y, t), ...]
# テンソルに変換 → RNNが受け取れる形に reshape
new_data_tensor = torch.tensor(new_data_list, dtype=torch.float32).unsqueeze(1)  # shape: (N, 1, 3)

# 予測（確率を取得）
with torch.no_grad():
    logits = model(new_data_tensor)             # 出力（logits）
    probs = torch.sigmoid(logits).squeeze()     # sigmoid で確率に変換
    predictions = (probs > 0.5).int()            # 0 or 1 に変換

print("予測された改行タイミング:", predictions.tolist())  # リストで出力

labels_tensor = torch.tensor(gyou_list2, dtype=torch.int)

correct = (predictions == labels_tensor).sum().item()
accuracy = correct / len(labels_tensor)

print(f"正解数: {correct}/{len(labels_tensor)}")
print(f"正解率: {accuracy:.2%}")
