import torch
import torch.nn as nn

# 気温のデータ
data = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]

# データをテンソルに変換 計算処理の効率や利便性が向上
data = torch.tensor(data)

class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()

        # LSTMセル
        self.lstm = nn.LSTM(input_size=1, hidden_size=10, num_layers=1)
        #nn.LSTM: LSTMセルを使って時系列の特徴を捉える
        #input_size=1: 各時点の入力は1次元（今回は1つの気温）
        #hidden_size=10: 隠れ状態の次元数。LSTMが内部で保持する情報のサイズ。
        #num_layers=1: LSTM層は1層だけ

        # 全結合層
        self.fc = nn.Linear(in_features=10, out_features=1)
        #nn.Linear: 最後にLSTM出力（10次元）を1次元の気温に変換するための全結合層

    def forward(self, x):#入力をLSTMに通し、その出力を全結合層に通して結果を返します
        # LSTMセルにデータを入力
        lstm_out, _ = self.lstm(x)

        # 全結合層で出力を計算
        out = self.fc(lstm_out)

        return out
    
# モデルのインスタンス化
model = LSTMModel()

# 損失関数の定義
loss_fn = nn.MSELoss()
#MSELoss：予測値と正解値の平均二乗誤差（回帰問題に使われる）

# オプティマイザの定義 Adamという最適化アルゴリズムが設定
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
#Adamオプティマイザ：勾配降下法の1つで、学習を効率的に進めるアルゴリズム

# エポック数の設定
epochs = 100 #訓練データを何回用いたかを表す数

# 学習ループ
for epoch in range(epochs):
    # モデルの予測
    outputs = model(data[:-1])

    # 損失の計算
    loss = loss_fn(outputs, data[1:])

    # パラメータの更新
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # 損失の出力
    print(f"epoch: {epoch+1}, loss: {loss.item()}")

# モデルの予測
outputs = model(data[:-1])
#学習後、data[:-1]（最初から最後の1個手前まで）を使って次の気温 data[1:] を予測します。

# 予測と実際の値の比較
print(f"予測: {outputs}")
print(f"実際の値: {data[1:]}")