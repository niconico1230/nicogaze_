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
th_range = list(range(50, 1001, 50))
freq_range = list(range(10, 121, 10))
F1_mat = np.zeros((len(freq_range), len(th_range)))
ACC_mat = np.zeros_like(F1_mat)
PREC_mat = np.zeros_like(F1_mat)    # ←ここ追加
RECALL_mat = np.zeros_like(F1_mat)  # ←ここ追加
F1_list  = []                            # 閾値ごとの F1 を 1 次元で保持


# 例のテキストとgazeデータ
line_text ="新商品の企画会議は白熱した。だが、市場競争において、他社とのパリティーを保つだけでは生き残れない。革新的なアイデアこそが、此処許から次の一手を打つための鍵となる。我々のチームは、課題に対してのべつに議論を重ね、その根底に通底する解決の糸口を探り続けた。一度見つけた突破口は、囲碁における掛粘のように、その後の展開を確実に有利にするための布石となる。失敗を恐れず仲間と共に挑戦し、常に先を見据える姿勢が重要だ。その確固たる連携と絶え間ない努力が、最終的な成功へと導くのだ。我々の道のりは始まったばかりであり、真の成功はまだその野末に隠されている。都市の景観と環境の質を向上させることは、まちづくりにおいて大切な仕事であり、都市計画の現場では、街路の修景や緑地の整備が日常的に行われている。ある日、暗合する設計案を巡って議論が交わされたが、リケッチアのような微細な問題点が指摘され、計画は再考を余儀なくされた。しかし、担当者はその指摘を殊勝と受け止め、より良い解決策を模索する姿勢を見せた。かつて逓信局が置かれていた場所の活用提案も検討され、錚々たる専門家が意見を寄せた。工事現場には塵芥が散乱していたものの、適切な処理方法を導入することで安全性が確保された。こうして、多様な要素を調整しながら街の魅力を高める取り組みが続けられている。新商品の企画会議は白熱した。だが、市場競争において、他社とのパリティーを保つだけでは生き残れない。革新的なアイデアこそが、此処許から次の一手を打つための鍵となる。我々のチームは、課題に対してのべつに議論を重ね、その根底に通底する解決の糸口を探り続けた。一度見つけた突破口は、囲碁における掛粘のように、その後の展開を確実に有利にするための布石となる。失敗を恐れず仲間と共に挑戦し、常に先を見据える姿勢が重要だ。その確固たる連携と絶え間ない努力が、最終的な成功へと導くのだ。我々の道のりは始まったばかりであり、真の成功はまだその野末に隠されている。都市の景観と環境の質を向上させることは、まちづくりにおいて大切な仕事であり、都市計画の現場では、街路の修景や緑地の整備が日常的に行われている。ある日、暗合する設計案を巡って議論が交わされたが、リケッチアのような微細な問題点が指摘され、計画は再考を余儀なくされた。しかし、担当者はその指摘を殊勝と受け止め、より良い解決策を模索する姿勢を見せた。かつて逓信局が置かれていた場所の活用提案も検討され、錚々たる専門家が意見を寄せた。工事現場には塵芥が散乱していたものの、適切な処理方法を導入することで安全性が確保された。こうして、多様な要素を調整しながら街の魅力を高める取り組みが続けられている。かつて注目を集め、寵児と称された人物が、今ではインターネット上で懲治のように批判されることもある。人の評価とは、仰ぎ見る空模様のように、日々変化するものだ。英英とした雲が広がる日もあれば、干害に苦しむような厳しい現実に直面する日もある。そうした中で、日々の生活の片隅に鳴る半鐘のように、小さな課題や不備が生活の質に影響を及ぼしている。例えば、アレルギー対策が適切に施されていない表記や、見直されるべき前納制度など、改善すべき課題は身近にある。そのような困難に向き合う人を支える存在は、かつての銃後のような役割を果たしているのかもしれない。その日、被害者が姿を消したのは花曇りの午後だった。発見現場の池には水鳥が一羽浮かび、岩燕がかすかに横切る静けさが漂っていた。ほどなくして遺体が発見され、検視で首筋に熱傷が確認された。捜査上で浮かんだのは、被害者の同輩で、かつて蛮行で送検された男だった。男は事件当日、持病の悪化で寝込んでいたと主張するが、足取りには遁走を思わせる空白があった。家宰として彼に職を与えていた老人は「彼の作り話に惑わされるな」と刑事たちを睥睨しながら断言した。この事件を概論的に整理すれば、金が絡む単純な犯行に見える。表面上は筋が通っているが、刑事の目はそこに違和感を覚えた。"


# ファイルパスを指定
df = pd.read_csv("ヒートマップの結果.csv", header=None)  # header=Noneでインデックス無視

# (1) tupleのリストに変換: [(1, 0), (2, 273.35), ...]
gaze_list = list(df.itertuples(index=False, name=None))

# (2) 2列目だけのリスト（滞留時間のみ）: [0, 273.35, ...]
gaze_duration = df[1].tolist()
true_flag = df[2].tolist()      # 3列目（正解ラベル 0/1）
gyou_info=df[3].tolist() #行番号を載せる。前後の番号が違えばいい


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

            # 単語の行番号を取得
            current_line_start = gyou_info[w["start"]]
            current_line_end = gyou_info[w["end"]]
            """
            ###＋－2の時####

            #-2の処理
            if w["start"] - 2 >= 0 and gyou_info[w["start"]-2]==current_line_start  :#もし２つ前も同じ行なら
                check_start=w["start"] - 2
            elif w["start"] - 1 >= 0 and gyou_info[w["start"]-1]==current_line_start:#もし１つ前までが同じ行なら
                check_start=w["start"] - 1
            elif  w["start"] >= 0:#もしこの単語が行の端っこだったら
                check_start=w["start"] 

            #+2の処理
            if w["end"] + 2 < len(gaze_duration) and gyou_info[w["end"]+2]==current_line_end  :#もし２つ前も同じ行なら
                check_end=w["end"] + 2
            elif w["end"] + 1 < len(gaze_duration) and gyou_info[w["end"]+1]==current_line_end:#もし１つ前までが同じ行なら
                check_end=w["end"] + 1
            elif w["end"]  < len(gaze_duration):#もしこの単語が行の端っこだったら
                check_end=w["end"] 

            ###＋－2の時####
            

            """
            ###＋－1の時####

            
            if w["start"] - 1 >= 0 and gyou_info[w["start"]-1]==current_line_start  :#もし1つ後も同じ行なら
                check_start=w["start"] - 1
            elif  w["start"] >= 0:#もしこの単語が行の端っこだったら
                check_start=w["start"] 

            if w["end"] + 1 < len(gaze_duration) and gyou_info[w["end"]+1]==current_line_end  :#もし1つ後も同じ行なら
                check_end=w["end"] + 1
            elif w["end"]  < len(gaze_duration):#もしこの単語が行の端っこだったら
                check_end=w["end"] 
            

            ###＋－1の時####
                       

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


# F1スコアの最大値を取得
max_f1_value = np.max(F1_mat[0, :])

# F1スコアの最大値を持つインデックスを取得
max_f1_indices = np.where(F1_mat[0, :] == max_f1_value)[0]
# 結果を出力
print(f"最大F1 = {max_f1_value:.3f}（滞留時間の閾値: ", end="")
print(*(f"{th_range[idx]} ms" for idx in max_f1_indices), sep=", ", end="")
print("）")
