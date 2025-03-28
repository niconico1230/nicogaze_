import torch
import torch.nn as nn
import numpy as np
from DATAeye import eyelist  # 視線データ (時刻, x, y)
from DATAmoji import mojilist  # 文章の単語データ (文字, x, y)

# 視線と単語のマッチング（距離 threshold 以内の単語を対応付ける）
def match_gaze_to_text(eyelist, mojilist, threshold=50):
    matched = []  
    for t, gx, gy in eyelist:
        min_dist = float("inf")
        closest_word = None
        for word, tx, ty in mojilist:
            dist = np.sqrt((gx - tx) ** 2 + (gy - ty) ** 2)
            if dist < threshold and dist < min_dist:
                min_dist = dist
                closest_word = (word, tx, ty)
        if closest_word:
            matched.append(((t, gx, gy), closest_word))
    return matched

# 視線と単語の対応付け
matched_pairs = match_gaze_to_text(eyelist, mojilist)

# 視線データ (t, gx, gy) を NumPy 配列に変換
gaze_data = np.array([[t, gx, gy] for (t, gx, gy), _ in matched_pairs])

# 平均0・標準偏差1に正規化
time_mean = np.mean(gaze_data[:, 0])  # 時間 (t) の平均
time_std = np.std(gaze_data[:, 0])  # 時間 (t) の標準偏差
gaze_data[:, 0] = (gaze_data[:, 0] - time_mean) / time_std  # 時間 t の正規化

# **データのテンソル化**
gaze_seq = torch.tensor([[t, x, y] for (t, x, y), _ in matched_pairs], dtype=torch.float32)
text_seq = torch.tensor([[tx, ty] for (_, (word, tx, ty)) in matched_pairs], dtype=torch.float32)

# 文字ごとの理想的な視線滞在時間
importance = {"毀": 1.0, "嗤": 1.0}  # 重要な文字には1.0、それ以外はデフォルト0.3
#target_times = torch.tensor([[importance.get(word, 0.3)] for (_, (word, _, _)) in matched_pairs], dtype=torch.float32)
target_times = [importance.get(word, 0.3) for (_, (word, _, _)) in matched_pairs]
target_times = torch.tensor(target_times, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)  # [1, seq_len, 1]


# バッチ次元を追加
gaze_seq = gaze_seq.unsqueeze(0)  # shape: [1, seq_len, 3]
text_seq = text_seq.unsqueeze(0)  # shape: [1, seq_len, 2]
#target_times = target_times.unsqueeze(0)  # shape: [1, seq_len, 1]

# **モデルの定義**
class GazeTextEncoder(nn.Module):
    def __init__(self, hidden_dim=32):
        super().__init__()
        self.lstm_gaze = nn.LSTM(3, hidden_dim, batch_first=True)
        self.lstm_text = nn.LSTM(2, hidden_dim, batch_first=True)
        self.output_layer = nn.Linear(hidden_dim, 1)  

    def forward(self, gaze_seq, text_seq):
        H_gaze, _ = self.lstm_gaze(gaze_seq)  # [1, seq_len, hidden_dim]
        H_text, _ = self.lstm_text(text_seq)  # [1, seq_len, hidden_dim]

        # アテンション計算
        H_gaze_t = H_gaze.transpose(1, 2)  # 転置
        attn_scores = torch.bmm(H_text, H_gaze_t)  # [1, seq_len, seq_len]
        attn_weights = torch.softmax(torch.tanh(attn_scores), dim=-1)
        context = torch.bmm(attn_weights, H_gaze)  # [1, seq_len, hidden_dim]
        print(H_gaze)
        # 視線滞在時間の予測
        predicted_times = self.output_layer(context)  # [1, seq_len, 1]
        return predicted_times

# **学習の準備**
model = GazeTextEncoder()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
loss_fn = nn.MSELoss()

# **学習ループ**
for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    outputs = model(gaze_seq, text_seq)
    loss = loss_fn(outputs, target_times)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss = {loss.item():.4f}")

# **予測の表示（文章順に並び替え）**
model.eval()
with torch.no_grad():
    predicted = model(gaze_seq, text_seq)
    #print(predicted)

# 単語ごとの予測値を辞書に格納
pred_dict = {word: value.item() for (_, (word, _, _)), value in zip(matched_pairs, predicted[0])}


# 文章の文字順で出力
print("\n📊 Predicted gaze times (per character in sentence order):")
for word, _, _ in mojilist:  # 文章の順番で出力
    predicted_time = pred_dict.get(word, 0.0)  # 視線がマッチしなかった文字は 0.0
    print(f"{word}: {predicted_time:.3f}")