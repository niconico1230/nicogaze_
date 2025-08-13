from fugashi import Tagger
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import matplotlib
import numpy as np1
import sys
import numpy as np


plt.rcParams['font.family'] = 'MS Gothic'   # または 'Meiryo', 'Yu Gothic'

# 結果保存用
th_range = list(range(250, 1001, 100))
freq_range = list(range(10, 121, 10))
F1_mat = np.zeros((len(freq_range), len(th_range)))
ACC_mat = np.zeros_like(F1_mat)
PREC_mat = np.zeros_like(F1_mat)    # ←ここ追加
RECALL_mat = np.zeros_like(F1_mat)  # ←ここ追加
F1_list  = []                            # 閾値ごとの F1 を 1 次元で保持


# 例のテキストとgazeデータ
line_text = "私は紺屋を家業とする古巣を飛び出し、伝統のしがらみを振り払う勢いで就活に挑んだ。行き詰まりを感じていたある日、気晴らしに放鷹を見に林床を歩いていると、黄埴を練っている術者のような老女に出会った。やがて大棗が添えられ、静かに儀式のような所作が始まり、手元からは微かな輻射が立ち上った。足を止めて驚く私に、老女は全てを知っているかのような口調で穏やかに語りかけた。「誰もが有理に生きる必要はないよ。自分の色を持っていればいい」。その言葉は深く胸に響き、まるで円弁のように迷いを解きほぐしていった。そのとき、必ずしも他人の隊伍に加わることだけが正解ではないと私は気づいた。町のカフェで、新人スタッフが操作を誤り、マシンの圧力が暴発した。激流のようにフォームがあふれ出し、厨房は一瞬騒然となる。先輩は反切した手順書をめくりながら、壁際の小さな玉櫛笥へ駆け寄り、慣れた手つきで工具を取り出した。マシンのゆるんだ部分をしっかり締め直すと、圧力は元に戻り、泡の噴き出しも収まった。空木のカウンター越しに聞こえた騒音は客席に筒抜けだったが、特待のマネージャーは憐憫の笑みを浮かべ、落ち着いた口調で状況を収めた。入り口の七竈は、店主の故地から届いたものだった。思い出に守られるように、カフェは再び静けさを取り戻した。僕の日課は、畑中をお散歩することだ。畑には縞目のように野菜が並び、薄原の心地よい香りがする。ある日、防炎シートをかぶった小屋のそばで、お母さんが「今日は炊き立てご飯よ」と呼ぶ声がした。僕はうれしくて走っていく途中、怪しい影を見つけたんだ。どうやら畑を荒らすイタチなどの間者らしい。僕はワンワン吠えて追い払ってやった！家に帰ると、ご近所さんたちが連辞となって、畑を守るための情報を伝え合っている。僕もその輪に加わって、畑中を見守るのが自慢だ。パトロール中は皮籠を持ったおばあさんや、石のそばの銭苔、草むらに残る花殻など、いろんな風景に出会う。今日も僕は畑の平和を守っている！新規デベロッパーによる都市開発が進む中、架設されたばかりの橋の開通式に招かれ、祝辞を述べることになった。式典は虚礼に終始せず、地域の未来を見据えた具体的な構想や計画が共有された。現地には花々が咲き、ふと足元に珍しい雄花が咲いているのを見つけ、思わず心が和んだ。近くには小さな廟所もあり、土地の歴史を感じた。しかし突然、来賓の一人が昏倒し、会場は一時騒然となった。その対応に追われる中、古代の陶棺が発掘された話題が広がり、会場に新たなざわめきが生まれた。此処彼処で生まれる新しい出会いと歴史の継承を感じながら、横着な考えを捨てて誠実に関わる大切さを改めて認識した一日だった。私は紺屋を家業とする古巣を飛び出し、伝統のしがらみを振り払う勢いで就活に挑んだ。行き詰まりを感じていたある日、気晴らしに放鷹を見に林床を歩いていると、黄埴を練っている術者のような老女に出会った。やがて大棗が添えられ、静かに儀式のような所作が始まり、手元からは微かな輻射が立ち上った。足を止めて驚く私に、老女は全てを知っているかのような口調で穏やかに語りかけた。「誰もが有理に生きる必要はないよ。自分の色を持っていればいい」。その言葉は深く胸に響き、まるで円弁のように迷いを解きほぐしていった。そのとき、必ずしも他人の隊伍に加わることだけが正解ではないと私は気づいた。町のカフェで、新人スタッフが操作を誤り、マシンの圧力が暴発した。激流のようにフォームがあふれ出し、厨房は一瞬騒然となる。先輩は反切した手順書をめくりながら、壁際の小さな玉櫛笥へ駆け寄り、慣れた手つきで工具を取り出した。マシンのゆるんだ部分をしっかり締め直すと、圧力は元に戻り、泡の噴き出しも収まった。空木のカウンター越しに聞こえた騒音は客席に筒抜けだったが、特待のマネージャーは憐憫の笑みを浮かべ、落ち着いた口調で状況を収めた。入り口の七竈は、店主の故地から届いたものだった。思い出に守られるように、カフェは再び静けさを取り戻した。"


# ファイルパスを指定
df = pd.read_csv("ヒートマップの結果.csv", header=None)  # header=Noneでインデックス無視

# (1) tupleのリストに変換: [(1, 0), (2, 273.35), ...]
gaze_list = list(df.itertuples(index=False, name=None))

# (2) 2列目だけのリスト（滞留時間のみ）: [0, 273.35, ...]
gaze_duration = df[1].tolist()
true_flag = df[2].tolist()      # 3列目（正解ラベル 0/1）


# --- ここで文字数チェック ---
if len(gaze_duration) != len(line_text) or len(true_flag) != len(line_text):
    print(f"エラー: CSVのデータ数（{len(gaze_duration)}行, {len(true_flag)}行）とline_textの文字数（{len(line_text)}文字）が一致しません。")
    sys.exit(1)
# ---------------------------



# --- 単語辞書読み込み ---
with open("word_index_short.pkl", "rb") as f:
    word_index_short = pickle.load(f)


tagger = Tagger()

# 単語情報のもとリスト作成（これを都度再構築することで前ループのpred/trueが残らないようにする）
def make_words():
    words = []
    char_pos = 0
    for token in tagger(line_text):
        surface = token.surface
        length = len(surface)
        start = char_pos
        end = char_pos + length - 1
        raw_lemma = token.feature[7] if len(token.feature) > 7 else surface
        base = raw_lemma.split("-")[0]
        if base == "*" or base == "":
            base = surface
        pos = token.feature[0]
        words.append({
            "word": surface,
            "base": base,
            "pos": pos,
            "start": start,
            "end": end
        })
        char_pos += length
    # 正解ラベル付与
    for w in words:
        char_indices = range(w["start"], w["end"]+1)
        true = 0
        for idx in char_indices:
            if idx < len(true_flag) and true_flag[idx] == 1:
                true = 1
                break
        w["true"] = true
    return words

# 2重ループ
for j, th in enumerate(th_range):
        words = make_words()

        # predラベル付与
        for w in words:
            #check_start = max(0, w["start"] - 2)
            #check_end = min(len(gaze_duration) - 1, w["end"] + 2)
            check_start = max(0, w["start"] )
            check_end = min(len(gaze_duration) - 1, w["end"] )
            char_indices = range(check_start, check_end + 1)
            flagged = False
            for idx in char_indices:
                if gaze_duration[idx] > th:
                    flagged = True
                    break
            w["pred"] = 1 if flagged else 0
        

        # 混同行列
        TP = FP = TN = FN = 0
        for w in words:
            pred = w["pred"]
            true = w["true"]
            if pred == 1 and true == 1:
                TP += 1
            elif pred == 1 and true == 0:
                FP += 1
            elif pred == 0 and true == 0:
                TN += 1
            elif pred == 0 and true == 1:
                FN += 1

        accuracy = (TP + TN) / (TP + FP + TN + FN) if (TP+FP+TN+FN) > 0 else 0
        precision = TP / (TP + FP) if (TP+FP) > 0 else 0
        recall = TP / (TP + FN) if (TP+FN) > 0 else 0
        specificity = TN / (TN + FP) if (TN+FP) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision+recall) > 0 else 0
        fnr = FN / (TP + FN) if (TP + FN) > 0 else 0   # ★ココ追加
        fpr = FP / (FP + TN) if (FP + TN) > 0 else 0

        # ここで保存！ (i, j)に対して
        # 保存
        F1_mat[0, j] = f1
        ACC_mat[0, j] = accuracy
        PREC_mat[0, j] = precision
        RECALL_mat[0, j] = recall


        print(f"正解（1）を正解（1）と判定（TP率/Recall）      : {recall:.3f}")
        print(f"正解（1）を不正解（0）と判定（FN率/FN/TP+FN）  : {fnr:.3f}")
        print(f"不正解（0）を不正解（0）と判定（TN率/Specificity）: {specificity:.3f}")
        print(f"不正解（0）を正解（1）と判定（FP率/FP/FP+TN）    : {fpr:.3f}")
        print(f"適合率（Precision）                               : {precision:.3f}")
        print(f"F1スコア                                        : {f1:.3f}")
        print(f"全体精度（Accuracy）                             : {accuracy:.3f}")


        print("\n【正解を不正解と判定した単語（偽陰性/FN）一覧】")
        for w in words:
            if w["true"] == 1 and w["pred"] == 0:
                print(f'{w["word"]} （位置 {w["start"]}-{w["end"]}）')

        print("\n【不正解を正解と判定した単語一覧】")
        for w in words:
            if w["true"] == 0 and w["pred"] == 1:
                print(f'{w["word"]} （位置 {w["start"]}-{w["end"]}）')

        print("\n\n")
    



# 出力例
#print("\n【文全体の正解と予測】")
#for w in words:
#    freq_str = f' (頻度補正)' if w.get("freq_override") else ""
#    print(f'{w["word"]} pred:{w["pred"]} true:{w["true"]}{freq_str}')


# 必要なら最適組み合わせも出力
best_idx = np.unravel_index(F1_mat.argmax(), F1_mat.shape)
print(f"最大F1={F1_mat[best_idx]:.3f}（秒数閾値: {th_range[best_idx[1]]}, 頻度閾値: {freq_range[best_idx[0]]}）")




# --- Precisionグラフ ---
plt.figure(figsize=(10, 6))
plt.plot(th_range, PREC_mat[0, :], marker='o')
plt.xlabel('滞在時間の閾値（ms）')
plt.ylabel('Precision（適合率）')
plt.title('滞在時間閾値ごとのPrecision（適合率）')
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Recallグラフ ---
plt.figure(figsize=(10, 6))
plt.plot(th_range, RECALL_mat[0, :], marker='o')
plt.xlabel('滞在時間の閾値（ms）')
plt.ylabel('Recall（再現率）')
plt.title('滞在時間閾値ごとのRecall（再現率）')
plt.grid(True)
plt.tight_layout()
plt.show()



plt.figure(figsize=(10, 6))
plt.plot(th_range, F1_mat[0, :], marker='o')
plt.xlabel('滞在時間の閾値（ms）')
plt.ylabel('F1スコア')
plt.title('滞在時間閾値ごとの未知語検出F1スコア')
plt.grid(True)
plt.tight_layout()
plt.show()



max_f1 = max(F1_list)
indices = [i for i, f1 in enumerate(F1_list) if f1 == max_f1]

for idx in indices:
    print(f"最大F1 = {max_f1:.3f}（滞留時間の閾値: {th_range[idx]} ms）")