import torch
import torch.nn as nn
import numpy as np
from DATAeye import eyelist
from DATAmoji import mojilist


# 空間的に近い gaze と文字を結びつける（例：距離が一定以下）
# threshold: 視線と単語位置の「近さ」を判定するための距離のしきい値
def match_gaze_to_text(eyelist, mojilist, threshold=50):
    matched = []  # 結果を保存するリストを初期化 「視線と対応する単語」をペアで追加していきます。
    for t, gx, gy in eyelist:  # 視線データを1つずつ取り出す
        min_dist = float("inf")  # 最小距離（最初は無限大にしておく）
        closest_word = None  # 最も近かった単語をここに保持する
        for word, tx, ty in mojilist:  # すべての単語の位置と比較するループ
            dist = np.sqrt((gx - tx)**2 + (gy - ty)**2)  # 視線との距離を計算（ユークリッド距離）
            if dist < threshold and dist < min_dist:
                min_dist = dist
                closest_word = (word, tx, ty)
        if closest_word:  # 見つかった最も近い単語があれば
            matched.append(((t, gx, gy), closest_word))  # その視線と単語をペアで追加
    return matched

matched_pairs = match_gaze_to_text(eyelist, mojilist)

# gaze入力: 時系列なので [seq_len, 3] -> (t, x, y) 3次元
gaze_seq = torch.tensor([[t, x, y] for (t, x, y), _ in matched_pairs], dtype=torch.float32)

# text位置: [seq_len, 2] -> (x, y) 2次元
text_seq = torch.tensor([[tx, ty] for (_, (word, tx, ty)) in matched_pairs], dtype=torch.float32)

# 例: 文字ごとの視線の理想滞在時間（擬似的でもOK）
importance = {
    "毀": 1.0,
    "嗤": 1.0,
}
target_times = []
for (_, (word, _, _)) in matched_pairs:
    value = importance.get(word, 0.3)  # なければ 1.0
    target_times.append([value])

target_times = torch.tensor(target_times, dtype=torch.float32).unsqueeze(0)  # shape: [1, seq_len, 1]

# batch次元追加 → [1, seq_len, features] PyTorch のテンソルに新しい次元を追加する
gaze_seq = gaze_seq.unsqueeze(0)
text_seq = text_seq.unsqueeze(0)

class GazeTextEncoder(nn.Module):
    def __init__(self, hidden_dim=32):
        super().__init__()
        self.lstm_gaze = nn.LSTM(3, hidden_dim, batch_first=True)
        self.lstm_text = nn.LSTM(2, hidden_dim, batch_first=True)
        self.output_layer = nn.Linear(hidden_dim, 1)  # 視線追跡時間を予測するための出力層
        
    def forward(self, gaze_seq, text_seq):
        H_gaze, _ = self.lstm_gaze(gaze_seq)  # [1, seq_len, hidden_dim] 出力
        H_text, _ = self.lstm_text(text_seq)  # [1, seq_len, hidden_dim]

        
        # アテンション計算のために H_gaze を転置
       # H_gaze_transposed = H_gaze.transpose(1, 2)  # [batch_size, hidden_dim, g_len]
        
         # アテンション計算
        H_gaze_t = H_gaze.transpose(1, 2)  # [1, hidden_dim, seq_len]
        attn_scores = torch.bmm(H_text, H_gaze_t)  # [1, seq_len, seq_len]
        attn_weights = torch.softmax(torch.tanh(attn_scores), dim=-1)
        #attn_weights = torch.softmax(attn_scores, dim=-1)
        context = torch.bmm(attn_weights, H_gaze)  # [1, seq_len, hidden_dim]
        
        

        # 視線追跡時間の予測
        predicted_times = self.output_layer(context)  # [batch_size, t_len, 1]
        
        return predicted_times
    

# Step 5: モデル学習の準備
model = GazeTextEncoder()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
loss_fn = nn.MSELoss()


# Step 6: 学習ループ（例: 100 エポック）
for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    outputs = model(gaze_seq, text_seq)
    loss = loss_fn(outputs, target_times)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss = {loss.item():.4f}")


# Step 7: 最終的な予測の表示
model.eval()
with torch.no_grad():
    predicted = model(gaze_seq, text_seq)
    print("\n📊 Predicted gaze times (per character):")
    for i, ((_, (word, _, _)), value) in enumerate(zip(matched_pairs, predicted[0])):
        print(f"{word}: {value.item():.3f}")
    print("attn_weights:", matched_pairs)