import torch
import torch.nn as nn
import numpy as np

# 仮の視線データ [(timestamp, x, y)]
gaze_data = [
    (0.1, 100, 200),
    (0.2, 105, 202),
    (0.3, 300, 400),
    # ...
]

# 仮のテキスト上の単語位置 [(word, x, y)]
text_data = [
    ("apple", 100, 200),
    ("banana", 300, 400),
    # ...
]

# 空間的に近い gaze と文字を結びつける（例：距離が一定以下）
#threshold: 視線と単語位置の「近さ」を判定するための距離のしきい値
def match_gaze_to_text(gaze_data, text_data, threshold=50):
    matched = []#結果を保存するリストを初期化 「視線と対応する単語」をペアで追加していきます。
    for t, gx, gy in gaze_data: #視線データを1つずつ取り出す
        min_dist = float("inf") # 最小距離（最初は無限大にしておく）
        closest_word = None #最も近かった単語をここに保持する
        for word, tx, ty in text_data:#すべての単語の位置と比較するループ
            dist = np.sqrt((gx - tx)**2 + (gy - ty)**2)#視線との距離を計算（ユークリッド距離）
            if dist < threshold and dist < min_dist:
                min_dist = dist
                closest_word = (word, tx, ty)
        if closest_word: # 見つかった最も近い単語があれば
            matched.append(((t, gx, gy), closest_word))#その視線と単語をペアで追加
    return matched

matched_pairs = match_gaze_to_text(gaze_data, text_data)



# gaze入力: 時系列なので [seq_len, 3] -> (t, x, y)
gaze_seq = torch.tensor([[t, x, y] for (t, x, y), _ in matched_pairs], dtype=torch.float32)

# text位置: [seq_len, 2] -> (x, y)
text_seq = torch.tensor([[tx, ty] for (_, (word, tx, ty)) in matched_pairs], dtype=torch.float32)

# batch次元追加 → [1, seq_len, features]
gaze_seq = gaze_seq.unsqueeze(0)
text_seq = text_seq.unsqueeze(0)





class GazeTextEncoder(nn.Module):
    #hidden_dim は隠れ層の次元数で、両方のLSTMがこの次元の出力を生成します
    def __init__(self, input_dim_gaze=3, input_dim_text=2, hidden_dim=32):
        super().__init__()
        self.lstm_gaze = nn.LSTM(input_dim_gaze, hidden_dim, batch_first=True)
        self.lstm_text = nn.LSTM(input_dim_text, hidden_dim, batch_first=True)

    def forward(self, gaze_seq, text_seq):
        H_gaze, _ = self.lstm_gaze(gaze_seq)  # [1, seq_len, hidden_dim] 出力
        H_text, _ = self.lstm_text(text_seq)  # [1, seq_len, hidden_dim]
        return H_gaze, H_text
    #時系列特徴量 H_gaze（視線）と H_text（テキスト）を抽出。

encoder = GazeTextEncoder()#視線データとテキストデータをエンコードします。
H_gaze, H_text = encoder(gaze_seq, text_seq)




    # 掛け算の attention を計算（簡易版）
# gaze_seq_len = g_len, text_seq_len = t_len, hidden_dim = d
# H_gaze: [batch, g_len, d], H_text: [batch, t_len, d]
# transpose to: [batch, d, g_len] for multiplication

#attn = torch.bmm(H_text, H_gaze.transpose(1, 2))  # [batch, t_len, g_len]
#attn = torch.tanh(attn)  # 活性化関数 δ を適用