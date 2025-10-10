import cv2
import mediapipe as mp
import numpy as np
import time
from sklearn.neural_network import MLPRegressor
import csv
import os
from PIL import Image, ImageDraw, ImageFont
import ctypes
import math
import sys # 👈 **これを追加**
from datetime import datetime

def get_system_dpi():
    # Windowsの場合
    if sys.platform.startswith('win'):
        # 1. 物理的なDPI（設定されているスケーリングに関わらず）を取得
        # ctypes.windll.user32.GetDpiForWindow(window_handle) などが必要だが、
        # 簡単のためにシステムの論理DPIを使う
        # GetDC(0)はスクリーン全体
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        hdc = user32.GetDC(0)
        # LOGPIXELSX (水平DPI) は 88
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) 
        user32.ReleaseDC(0, hdc)
        return dpi
    # macOS/Linuxの場合は、環境変数や設定ファイルから読み取る必要があり複雑
    # 簡単のため、標準的な96 DPIを返す
    return 96 

# 取得したDPI
ACTUAL_DPI = get_system_dpi()
# --- 補正サイズ計算の追加 ---
TARGET_PT_SIZE = 16
PIL_BASE_DPI = 72.0 
# PILに渡すべき補正済みのサイズを計算し、定数として定義
CORRECTED_SIZE = TARGET_PT_SIZE * (ACTUAL_DPI / PIL_BASE_DPI)
print(f"🖥️ システムDPI: {ACTUAL_DPI}。補正されたフォントサイズ: {CORRECTED_SIZE:.2f}")


# MediaPipe初期化
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# 瞬きしきい値
BLINK_THRESHOLD = 3

def detect_blink(landmarks, w, h, threshold=5):
    left_top = landmarks[159].y * h
    left_bottom = landmarks[145].y * h
    right_top = landmarks[386].y * h
    right_bottom = landmarks[374].y * h
    left_dist = abs(left_top - left_bottom)
    right_dist = abs(right_top - right_bottom)
    blink = int((left_dist < threshold) and (right_dist < threshold))
    return blink, left_dist

def extract_iris_vector(landmarks, w, h):
    left_center = np.mean([[landmarks[33].x * w, landmarks[33].y * h],
                           [landmarks[133].x * w, landmarks[133].y * h]], axis=0)
    left_iris = [landmarks[468].x * w, landmarks[468].y * h]
    left_vec = np.subtract(left_iris, left_center)

    right_center = np.mean([[landmarks[362].x * w, landmarks[362].y * h],
                            [landmarks[263].x * w, landmarks[263].y * h]], axis=0)
    right_iris = [landmarks[473].x * w, landmarks[473].y * h]
    right_vec = np.subtract(right_iris, right_center)

    nose_tip = np.array([landmarks[1].x * w, landmarks[1].y * h])
    chin = np.array([landmarks[152].x * w, landmarks[152].y * h])
    head_vec = chin - nose_tip
    head_vec = head_vec / np.linalg.norm(head_vec)

    return np.concatenate([left_vec, right_vec, head_vec])

def put_text_pil(image, text, position,font_size):
    font_path = "C:\\Windows\\Fonts\\msmincho.ttc"
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=(255, 255, 255))
    try:
        font = ImageFont.truetype(font_path, int(font_size)) # 👈 **int()で丸める**
    except Exception:
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=(255, 255, 255))
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


clicked = False

def mouse_callback(event, x, y, flags, param):
    global clicked,last_mouse_x, last_mouse_y, clicked_buttons_in_predict, state
    # ★ グローバル変数の追加
    global last_clicked_button_label, last_clicked_time 
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = True
        last_mouse_x = x
        last_mouse_y = y
        print(f"🖱️ クリック座標: ({x}, {y})")

        # ★ predictフェーズでのボタンクリック判定
        if state == "predict":
            for label, (bx, by) in BUTTON_POSITIONS.items():
                if bx <= x <= bx + BUTTON_WIDTH and by <= y <= by + BUTTON_HEIGHT:
                    # ボタン領域内をクリック

                    # ★ 視覚フィードバック用の変数を更新
                    last_clicked_button_label = label
                    last_clicked_time = time.time()

                    t_ms = time.time() * 1000
                    t_ms_str = f"{t_ms:.2f}"
                    int_part, dec_part = t_ms_str.split('.')
                    last6 = int_part[-6:]
                    formatted_time = f"{last6}.{dec_part}"
                    
                    clicked_buttons_in_predict.append({
                        "index": len(clicked_buttons_in_predict) + 1,
                        "time": formatted_time,
                        "button": label,
                        "mouse_x": x,
                        "mouse_y": y,
                        "text_index": text_index # どのテキストでのクリックかを記録
                    })
                    print(f"🎯 ボタンクリック記録: {label} (text_index: {text_index})")
                    # ボタンクリックは通常の「キャリブ点クリック」とは別処理なので、
                    # clickedをFalseに戻さず、通常のクリック処理（predictでの座標記録）も続行させてOK


#width, height = 1280, 720
# 修正後の推奨値（フルHD）
width, height = 1920, 1080 
rows, cols = 5, 5
scale_x = 0.9
# 新しい垂直方向の縮小率 (例: 0.8 で 20% 詰める)
scale_y_squeeze = 0.82
# 1. 元の均等な間隔（基準となる間隔）を計算
#    Top_Y は r=0 の点の位置であり、一番上の点と画面上端の余白でもある
base_spacing = height / (rows + 1)
Top_Y = base_spacing 

# 2. 詰めた後の点間の間隔を計算
squeezed_spacing = base_spacing * scale_y_squeeze

# 3. y座標の決定（r=0の点は固定、r>0の点は詰める）
points = []
for r in range(rows):
    if r == 0:
        # r=0 (一番上の点) の y座標は元の位置に固定
        y = int(Top_Y) 
    else:
        # r > 0 の点
        # y = 固定された Top_Y + r * 詰めた間隔
        y = int(Top_Y + r * squeezed_spacing) 

    for c in range(cols):
        # x座標の計算はそのまま（均等配置の式を scale_x で調整）
        x = int((width*(c+1)/(cols+1) - width/2)*scale_x + width/2)
        points.append((x, y))


cap = cv2.VideoCapture(0)
model_x = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
model_y = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
X, y = [], []

calibration_rounds = 0 #キャリブレーション回数指定
total_calibration_points = len(points) * calibration_rounds
state = "calibration"
index = 0





# --- 新しい定数: ボタンの設定 ---
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 80
BUTTON_MARGIN_X = 50
BUTTON_MARGIN_Y = 20

# ボタンの位置情報 (テキスト表示領域の右上に設定)
# テキストの開始座標 start_x, start_y = 420, 220 を参考に、右側に配置する
BUTTON_START_X = width - (BUTTON_WIDTH + BUTTON_MARGIN_X) # 画面右側
BUTTON_START_Y = 220 + 50 # テキストの行の高さに合わせて微調整

BUTTON_POSITIONS = {
    "A": (BUTTON_START_X, BUTTON_START_Y),
    "B": (BUTTON_START_X, BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_MARGIN_Y) * 1),
    "C": (BUTTON_START_X, BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_MARGIN_Y) * 2),
    "D": (BUTTON_START_X, BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_MARGIN_Y) * 3),
}

# 記録用リスト
clicked_buttons_in_predict = []
# ★ 新規追加: 視覚フィードバック用の変数
# 最後にクリックされたボタンのラベルと、クリックされた時刻を記録
last_clicked_button_label = None 
last_clicked_time = 0.0
FEEDBACK_DURATION = 0.2 # フィードバック表示時間 (秒)




class KalmanFilter:
    def __init__(self):
        self.state = np.zeros(4)
        self.F = np.array([[1, 0, 1, 0],
                           [0, 1, 0, 1],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])
        self.P = np.eye(4) * 1000
        self.R = np.eye(2) * 1
        self.Q = np.eye(4) * 0.1
        self.K = np.zeros((4, 2))

    def predict(self):
        self.state = np.dot(self.F, self.state)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

    def update(self, measurement):
        y = measurement - np.dot(self.H, self.state)
        self.K = np.dot(np.dot(self.P, self.H.T),
                        np.linalg.inv(np.dot(np.dot(self.H, self.P), self.H.T) + self.R))
        self.state = self.state + np.dot(self.K, y)
        self.P = np.dot(np.eye(4) - np.dot(self.K, self.H), self.P)

kf = KalmanFilter()
char_data = None
message_image = None
recording = False
recording_log = []
record_count = 1
text_index = 0 #文章の入っている配列番号

predict_start_time = None  # 視線推定開始時刻を記録する変数

cv2.namedWindow("Gaze Estimation", cv2.WINDOW_NORMAL)
#cv2.namedWindow("Gaze Estimation", cv2.WINDOW_AUTOSIZE) 
cv2.setWindowProperty("Gaze Estimation", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Gaze Estimation", mouse_callback)

print(f"▶ キャリブレーション：{calibration_rounds}周。点を見てクリックしてください")

program_start_time = time.time()#顔画像の表示時間を測る

# ファイルの先頭、または定数定義のセクションに以下の定数を追加
# クリックの許容誤差（ピクセル）。この値の範囲内でクリックされたら有効とみなす
CLICK_TOLERANCE = 15

while True:
    ret, cam = cap.read()
    if not ret:
        break

    canvas = np.zeros((height, width, 3), dtype=np.uint8)
   # canvas = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    if time.time() - program_start_time <= 2:
        face_small = cv2.resize(cam, (160, 120))
        canvas[0:120, 0:160] = face_small

    rgb = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark
        h, w = cam.shape[:2]
        features = extract_iris_vector(landmarks, w, h)
        blink_flag, left_dist = detect_blink(landmarks, w, h)

        if state == "calibration":
            current_point = points[index % len(points)]
            round_num = index // len(points) + 1
            cx, cy = current_point
            cv2.circle(canvas, (cx, cy), 15, (0, 255, 0), -1)
            cv2.putText(canvas, f"Round {round_num}/{calibration_rounds} - ({index%25+1}/25)",
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 2)

            if clicked:
                clicked = False
                # クリック座標とキャリブレーション点の距離を計算
                distance = math.sqrt((last_mouse_x - cx)**2 + (last_mouse_y - cy)**2)
                
                if distance <= CLICK_TOLERANCE:
                    # 許容範囲内の場合、データを記録し、次の点へ進む
                    X.append(features)
                    y.append([cx, cy])
                    index += 1
                    print(f"  ✅ 記録 {index}/{total_calibration_points}")
                    if index >= total_calibration_points:
                        print("▶ 学習中...")
                        X_np = np.array(X)
                        y_np = np.array(y)
                        model_x.fit(X_np, y_np[:, 0])
                        model_y.fit(X_np, y_np[:, 1])
                        print("✅ 学習完了。視線推定を開始します")
                        state = "predict"
                        predict_start_time = time.time()  # ← 追加

        elif state == "predict":
            px = model_x.predict(np.array(features).reshape(1, -1))[0]
            py = model_y.predict(np.array(features).reshape(1, -1))[0]
            kf.predict()
            kf.update(np.array([px, py]))
            px, py = kf.state[0], kf.state[1]

            if recording:
                t_ms = time.time() * 1000
                t_ms_str = f"{t_ms:.2f}"  # 小数第2位まで
                int_part, dec_part = t_ms_str.split('.')
                last6 = int_part[-6:]
                formatted_time = f"{last6}.{dec_part}"

                recording_log.append({
                    "time": formatted_time,
                    "x": px,
                    "y": py,
                    "blinking": blink_flag,
                    "left_dist": left_dist
                })
            
            if time.time() - predict_start_time <= 60:
                #canvas = np.zeros((height, width, 3), dtype=np.uint8)
                cv2.circle(canvas, (int(px), int(py)), 20, (255, 0, 0), -1)
                cv2.putText(canvas, "Smoothed Gaze", (int(px)+10, int(py)+10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            #canvas = np.zeros((height, width, 3), dtype=np.uint8)
            #cv2.putText(canvas, f"Blinking: {blink_flag}", (30, 90),
                           # cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)#瞬きのリアルタイム表示
            

            # ★ 修正: ボタンの描画と視覚フィードバック
            current_time = time.time()

            # ★ ボタンの描画を追加 A~Dの解答ボタン
            for label, (bx, by) in BUTTON_POSITIONS.items():
                is_clicked = (label == last_clicked_button_label and 
                              current_time - last_clicked_time < FEEDBACK_DURATION)
                # 色の選択: クリックされたら黄色、通常は青
                if is_clicked:
                    bg_color = (255, 255, 0) # 黄色 (BGR)
                    border_thickness = 5
                    scale_factor = 0.95 # 縮小率
                    
                    # 縮小後のサイズと位置を計算 (中央寄せを維持)
                    bw = int(BUTTON_WIDTH * scale_factor)
                    bh = int(BUTTON_HEIGHT * scale_factor)
                    bx_c = bx + (BUTTON_WIDTH - bw) // 2
                    by_c = by + (BUTTON_HEIGHT - bh) // 2
                else:
                    bg_color = (255, 100, 50) # 青色 (BGR)
                    border_thickness = 3
                    bw, bh = BUTTON_WIDTH, BUTTON_HEIGHT
                    bx_c, by_c = bx, by
                    
                
                # ボタンの背景 (青色)
                cv2.rectangle(canvas, (bx_c, by_c), (bx_c + bw, by_c + bh), bg_color, -1)
                # ボタンの枠線
                cv2.rectangle(canvas, (bx_c, by_c), (bx_c + bw, by_c + bh), (255, 255, 255), border_thickness)
                # ボタンの文字 (白色) - 文字の位置は元のボタンサイズ (bx, by) を基準に中央寄せ
                text_w, text_h = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 3)[0]
                text_x = bx + (BUTTON_WIDTH - text_w) // 2
                text_y = by + (BUTTON_HEIGHT + text_h) // 2
                cv2.putText(canvas, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)



            if char_data is None:
                texts = [
                    "頭を動かさず、指示をお待ちください",

                    "D",
                    "町のカフェで、新人スタッフが操作を誤り、マシンの圧力が暴発した。激流のようにフォームがあふれ出し、厨房は一瞬騒然となる。先輩は反切した手順書をめくりながら、壁際の小さな玉櫛笥へ駆け寄り、慣れた手つきで工具を取り出した。マシンのゆるんだ部分をしっかり締め直すと、圧力は元に戻り、泡の噴き出しも収まった。空木のカウンター越しに聞こえた騒音は客席に筒抜けだったが、特待のマネージャーは憐憫の笑みを浮かべ、落ち着いた口調で状況を収めた。入り口の七竈は、店主の故地から届いたものだった。思い出に守られるように、カフェは再び静けさを取り戻した。",
                    "問題1：マシンのトラブルが発生した直接の原因は何か？　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　A. 客の操作ミスによるもの　　　　　　　　　　　　　　　B. 新人スタッフが操作を誤ったため　　　　　　　　　　　C. 工具の整備不良のため　　　　　　　　　　　　　　　　D. マシンの老朽化によるもの",
                    "問題2：「玉櫛笥（たまくしげ）」は文章の中でどのような用途で登場するか？　　　　　　　　　　　　　　　　　　　　　　A. マシンの泡を拭き取るための道具　　　　　　　　　　　B. 修理用の工具が収められている場所　　　　　　　　　　C. お客の私物を保管する棚　　　　　　　　　　　　　　　D. 七竈の飾りをしまっておく箱",
                    "問題3：このカフェの「七竈（ななかまど）」について正しく説明しているのはどれか？　　　　　　　　　　　　　　　　　　A. 店主が趣味で育てた鉢植えである　　　　　　　　　　　B. 新人スタッフが飾った花である　　　　　　　　　　　　C. 店主の故郷から届いたものである　　　　　　　　　　　D. 特待のマネージャーが開業祝いに贈ったもの",


                    "C",
                    "私は紺屋を家業とする古巣を飛び出し、伝統のしがらみを振り払う勢いで就活に挑んだ。行き詰まりを感じていたある日、気晴らしに放鷹を見に林床を歩いていると、黄埴を練っている術者のような老女に出会った。やがて大棗が添えられ、静かに儀式のような所作が始まり、手元からは微かな輻射が立ち上った。足を止めて驚く私に、老女は全てを知っているかのような口調で穏やかに語りかけた。「誰もが有理に生きる必要はないよ。自分の色を持っていればいい」。その言葉は深く胸に響き、まるで円弁のように迷いを解きほぐしていった。そのとき、必ずしも他人の隊伍に加わることだけが正解ではないと私は気づいた。",
                    "問題1：筆者が就職活動に挑む際の姿勢として最も適切なのはどれか？　　　　　　　　　　　　　　　　　　　　　　　　　　A. 家業を継ぐための準備として就活を始めた　　　　　　　B. 新たな挑戦のため、伝統から離れようとした　　　　　　C. 放鷹の技術を活かした職を探していた　　　　　　　　　D. 老女に出会うことを目的に林床を訪れた",
                    "問題2：筆者が「放鷹を見に林床を歩いている」場面の描写から読み取れる筆者の心理として最も適切なのはどれか？　　　　　A. 林業に関する情報収集のために訪れた　　　　　　　　　B. 気晴らしに自然へ身を置こうとしていた　　　　　　　　C. 放鷹師に弟子入りする決意を固めていた　　　　　　　　D. 林床に迷い込んでしまった偶然の場面",
                    "問題3：この物語のテーマとして最もふさわしいものはどれか？　　　　　　　　　　　　　　　　　　　　　　　　　　　　　A. 家族との確執と和解の物語　　　　　　　　　　　　　　B. 日本の伝統文化の魅力再発見　　　　　　　　　　　　　C. 自己決定と独自性の重要性　　　　　　　　　　　　　　D. 年長者の知恵を活かす現代の知見",


                    "A",
                    "僕の日課は、畑中をお散歩することだ。畑には縞目のように野菜が並び、薄原の心地よい香りがする。ある日、防炎シートをかぶった小屋のそばで、お母さんが「今日は炊き立てご飯よ」と呼ぶ声がした。僕はうれしくて走っていく途中、怪しい影を見つけたんだ。どうやら畑を荒らすイタチなどの間者らしい。僕はワンワン吠えて追い払ってやった！家に帰ると、ご近所さんたちが連辞となって、畑を守るための情報を伝え合っている。僕もその輪に加わって、畑中を見守るのが自慢だ。パトロール中は皮籠を持ったおばあさんや、石のそばの銭苔、草むらに残る花殻など、いろんな風景に出会う。今日も僕は畑の平和を守っている！",

                    "問題1：この文章の主人公（「僕」）はどのような役割を持っていますか？　　　　　　　　　　　　　　　　　　　　　　　　A. 畑の野菜を育てる人　　　　　　　　　　　　　　　　　B. 畑を見守り、守る存在　　　　　　　　　　　　　　　　C. 畑で遊ぶ子ども　　　　　　　　　　　　　　　　　　　D. 畑で働くお母さん",
                    "問題2:畑の近くで「僕」が見つけた怪しい影は何でしたか？　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　A. カラス　　　　　　　　　　　　　　　　　　　　　　　B. 猫　　　　　　　　　　　　　　　　　　　　　　　　　C. イタチなどの間者　　　　　　　　　　　　　　　　　　D. おばあさん",
                    "問題3:ご近所さんたちは畑を守るために何をしていますか？　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　A. 一緒にパトロールをしている　　　　　　　　　　　　　B. 看板を立てて注意を呼びかけている　　　　　　　　　　C. 毎日イベントを開いている　　　　　　　　　　　　　　D. 情報を伝え合って協力している",

                    "B",
                    "新規デベロッパーによる都市開発が進む中、架設されたばかりの橋の開通式に招かれ、祝辞を述べることになった。式典は虚礼に終始せず、地域の未来を見据えた具体的な構想や計画が共有された。現地には花々が咲き、ふと足元に珍しい雄花が咲いているのを見つけ、思わず心が和んだ。近くには小さな廟所もあり、土地の歴史を感じた。しかし突然、来賓の一人が昏倒し、会場は一時騒然となった。その対応に追われる中、古代の陶棺が発掘された話題が広がり、会場に新たなざわめきが生まれた。此処彼処で生まれる新しい出会いと歴史の継承を感じながら、横着な考えを捨てて誠実に関わる大切さを改めて認識した一日だった。",
                    "問題1：なぜ式典は「虚礼に終始せず」と描写されているのでしょうか？ 　　　　　　　　　　　　　　　　　　　　　　　　A. 参加者の態度が悪かったから　　　　　　　　　　　　　B. 具体的な将来像や地域計画が共有されたから　　　　　　C. 予定されていた挨拶が省略されたから　　　　　　　　　D. 式典の開催が中止されたから",
                    "問題2:主人公が「心が和んだ」と感じたきっかけは何ですか？　　　　　　　　　　　　　　　　　　　　　　　　　　　　　A. 足元に珍しい雄花を見つけたから　　　　　　　　　　　B. 参加者のスピーチを聞いたから　　　　　　　　　　　　C. 式典が予定より早く終わったから　　　　　　　　　　　D. 会場に人が少なかったから",
                    "問題3:文章の中で「会場が一時騒然となった」理由は何ですか？　　　　　　　　　　　　　　　　　　　　　　　　　　　　A. 雄花がなくなったから　　　　　　　　　　　　　　　　B. 新しい橋が崩れたから　　　　　　　　　　　　　　　　C. 来賓の一人が倒れたから　　　　　　　　　　　　　　　D. 陶棺が見つかったから"
                ]
                
                

                char_data = []
                text = texts[text_index]
                start_x, start_y = 420, 220
                char_x = start_x
                char_y = start_y
                max_width = 1500
                line_height = CORRECTED_SIZE*1.5

                for i, char in enumerate(text):
                    char_w = CORRECTED_SIZE+2#読みやすい値に変えていい
                    center_x = char_x + char_w // 2
                    #center_x += 6
                    center_y = char_y + line_height  // 2
                    center_y=center_y-5
                    print(f"文字: '{char}' の中心座標 → ({center_x}, {center_y})")
                    char_data.append({
                        "char": char,
                        "pos": (char_x, char_y),
                        "size": (char_w, line_height )
                    })
                    char_x += char_w
                    if char_x + char_w > max_width:
                        char_x = start_x
                        char_y += line_height

            if message_image is None:
                #message_image = np.ones_like(canvas) * 255
                message_image = np.zeros_like(canvas)
                for ch in char_data:
                    x, y = ch["pos"]
                    message_image = put_text_pil(message_image, ch["char"], (x, y), CORRECTED_SIZE) 

            canvas = cv2.addWeighted(canvas, 1.0, message_image, 1.0, 0)


    cv2.imshow("Gaze Estimation", canvas)
  
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('z') or key == ord('r'):
        recording = not recording
        if recording:
            print("▶ 記録開始")
            recording_log = []
        else:
            filename = f"gazedataF_{record_count}.csv"
            while os.path.exists(filename):
                record_count += 1
                filename = f"gazedataF_{record_count}.csv"
            with open(filename, "w", newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["time", "x", "y", "blinking", "left_dist"])
                writer.writeheader()
                writer.writerows(recording_log)
            print(f"✅ 記録停止。{filename} に保存しました")
    
    elif key == ord('n'):  # nキーで次のテキストへ
        text_index = (text_index + 1) % len(texts)
        char_data = None
        message_image = None
        print(f"▶ テキストを切り替えました（{text_index + 1}/{len(texts)}）")

cap.release()
cv2.destroyAllWindows()

# 現在時刻を取得してファイル名に埋め込む
now = datetime.now()
timestamp = now.strftime("%d日%H時%M分%S秒")
filename_btn = f"button_clicks_nyan{timestamp}.csv"

with open(filename_btn, "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["index", "time", "button", "mouse_x", "mouse_y", "text_index"])
    writer.writeheader()
    writer.writerows(clicked_buttons_in_predict)
print(f"📝 ボタンクリック座標を {filename_btn} に保存しました")