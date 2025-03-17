import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# 視線データの前処理
def preprocess_gaze_data(raw_data):
    # 移動平均フィルタを適用
    smoothed_data = np.convolve(raw_data, np.ones(50)/50, mode='valid')
    return smoothed_data

# LSTMモデルの構築
def create_lstm_model(input_shape):
    model = Sequential([
        LSTM(64, input_shape=input_shape, return_sequences=True),
        LSTM(32, return_sequences=False),
        Dense(1, activation='sigmoid')  # バイナリ分類器
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# サンプルデータ
gaze_data = np.random.random((1000, 10, 2))  # 1000サンプル、10時刻、x/y座標
labels = np.random.randint(2, size=(1000,))  # バイナリラベル

# モデル構築・学習
model = create_lstm_model((10, 2))
model.fit(gaze_data, labels, epochs=10, batch_size=32)

# 評価
loss, accuracy = model.evaluate(gaze_data, labels)
print(f"Loss: {loss}, Accuracy: {accuracy}")