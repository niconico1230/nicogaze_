import pandas as pd
from dtaidistance import dtw
import numpy as np
import cv2
import csv
import sys
from fugashi import Tagger
import matplotlib.pyplot as plt
import pickle

#facemeshで得られたファイルからｘ、ｙの座標を取り出し、４ピクセルずつに分けた番号を配列に振る
#→同じ番号のペアで足していき、最終的にそれと重なる文字が未知語

def extract_gaze_coordinates(file_path,file_path2,yoko,tate):
    """
    指定されたCSVファイルからx座標とy座標を抽出して返します。

    Args:
        file_path (str): 処理するCSVファイルへのパス

    Returns:
        tuple: (x座標のリスト, y座標のリスト)
               ファイルが見つからない場合はNone
    """
    try:
        # pandasを使ってCSVファイルを読み込みます
        df = pd.read_csv(file_path)#視線と時刻などが入っている

        # 2次元配列を初期化
        coords_2d = []

        # 必要な列 'x' と 'y' を選択します
        time=df['time'].tolist()
        x_coords_before= df['x'].tolist() #射影変換前データ
        y_coords_before = df['y'].tolist() #ｄｔｗ前のデータ
        left_dist=df['left_dist'].tolist()

        #瞬き検出に使う材料を取り出す
        left_dist_array = df['left_dist'].values
        time_array = df['time'].values
        #差分の計算
        delta_left_dist = np.diff(left_dist_array)
        delta_time = np.diff(time_array)

        epsilon = 1e-9
        with np.errstate(divide='ignore', invalid='ignore'):
            dist_speed_before = np.divide(delta_left_dist, delta_time, 
                                    out=np.zeros_like(delta_left_dist, dtype=float), 
                                    where=np.abs(delta_time) > epsilon)
            
        dist_speed_before_sec = dist_speed_before * 1000.0    
            
        dist_speed = np.insert(dist_speed_before_sec, 0, 0.0)
        #speedはしっかりできてそう


        df2 = pd.read_csv(file_path2)#文字が入っているファイル
        moji=df2['moji'].tolist()
        restored_text = "".join(moji)#文章に戻したもの
        x_moji = df2['x'].tolist()
        y_moji= df2['y'].tolist()
        true_flag =df2['flag'].tolist()      # 3列目（正解ラベル 0/1）


        th_range = list(range(250, 1001, 10))#滞留時間閾値の範囲
        widthmax=1280
        heightmax=720
        width=320 #4pxで分けた時、0~319番まである。
        height=180

        F1_mat = np.zeros((1, len(th_range)))
        #F1_mat = np.zeros((len(th_range)))
        ACC_mat = np.zeros_like(F1_mat)
        PREC_mat = np.zeros_like(F1_mat)    # ←ここ追加
        RECALL_mat = np.zeros_like(F1_mat)  # ←ここ追加



      # --- 単語辞書読み込み ---
        with open("word_index_short.pkl", "rb") as f:
            word_index_short = pickle.load(f)

        tagger = Tagger()



    #===dtw===#
        print("dtwで補正をしています")
        # 文字位置（y座標）
        text_positions = np.array([165, 205, 245, 285, 325, 365, 405, 445, 485, 525])
        # DTW による距離計算とマッチング
        path = dtw.warping_path(np.array(y_coords_before) , text_positions)

        # 修正後の視線データ
        y_coords = np.array([text_positions[p[1]] for p in path])
    #===dtw===#


    #===1行ごとの視線数を数える。　４個以下の時もある====#
        eye_num=[] #行番号とその行の視線数　[1, 1, 284, ] dtw後だからばらつき有り
        gyounum=0 #1行の視線数　同じ行にある視線数を数える 
        roopnum=0 #ループの回数=行番号 1から
   
        for i in y_coords:
            if i==text_positions[roopnum]:
                gyounum+=1
            else :
                roopnum+=1
                eye_num.append(gyounum)
                gyounum=1
        eye_num.append(gyounum)
    #===1行ごとの視線数を数える====#  



    #===x視線の行ごとのリストを作る=====#
        startpoji=0 #x行目が始まる位置
        x_coords_second=[]
    
        for i in eye_num:
            finishpoji=i+startpoji
            new_list = x_coords_before[startpoji : finishpoji]#finishpojiの１つ前まで動作する
            x_coords_second.append(new_list) #[[256.90626593501], [260.608245138611], [261.89953893247, 263.726659441695, 258.70175640937, 
            startpoji=finishpoji

    # ===x視線の行ごとのリストを作る======#  



    #===文字を１行ごとに分ける、リストを作る===#
        ynum=0#行番号　配列番号
        sumy=0#１行に何文字あるか
        y_mojinum=[]#１行ごとの文字数のみを足していく
        for y in y_moji:
            if y==text_positions[ynum]:
                sumy+=1
            else :
                ynum+=1
                y_mojinum.append(sumy)
                sumy=1
        y_mojinum.append(sumy)
   

        startpoji=0
        x_moji_second=[]#文字のｘ座標を行ごとに配列へ分けていく
        for i in y_mojinum:
            finishpoji=i+startpoji
            new_list2 = x_moji[startpoji : finishpoji]#finishpojiの１つ前まで動作する
            x_moji_second.append(new_list2) #[[あいうえ],[おかきく]...] ok
    #===文字を１行ごとに分ける===#



    #===射影変換=一行ずつ===#
        x_coords=[] #行ごとのｘの視線リストを１つにする
    # x_coords_second 視線の配列
    # x_moji_second 文字の配列 
        for i in range(len(x_moji_second)):     #iでループ数を数える  
            if len(x_coords_second[i]) < 4 or len(x_moji_second[i]) < 4:
                x_coords=x_coords+ x_coords_second[i]
                print("視線情報が４点以下のため飛ばします。")
                continue

            # gaze/charの最小値・最大値を取って矩形の両端とする
            gaze_min, gaze_max = min(x_coords_second[i]), max(x_coords_second[i])
            char_min, char_max = min(x_moji_second[i]), max(x_moji_second[i])

            # 4点：左端・右端、それぞれに固定y=±1を付けて仮想的な矩形を作成
            src_pts = np.array([
                [gaze_min, -1],
                [gaze_max, -1],
                [gaze_max,  1],
                [gaze_min,  1],
            ], dtype=np.float32)

            dst_pts = np.array([
                [char_min, -1],
                [char_max, -1],
                [char_max,  1],
                [char_min,  1],
            ], dtype=np.float32)

            # 射影変換行列の計算
            matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

            # 補正対象のgaze座標を (x, 0) にして変換
            gaze_pts = np.array([[x, 0] for x in x_coords_second[i]], dtype=np.float32).reshape(-1, 1, 2)
            transformed_pts = cv2.perspectiveTransform(gaze_pts, matrix)

            corrected_x = [pt[0][0] for pt in transformed_pts]      #射影変換後の視線ｘ座標ok

            x_coords=x_coords+ corrected_x #１つのｘの視線座標にしている。要素数は合っていることを確認した。

    #===射影変換====#


    #######ヒートマップ作成開始#################
       
        # 空の2次元配列を準備 集計用
        array_2d = []
        

        #⑴ 
        print("4pxごとの配列を作成しています。")
        #widthmax=1280
        #heightmax=720
        for a in range(width):
            for b in range(height):
                # a, b, 0を1次元リストにまとめる  3つ目の０はそのマスに視線が止まった時間を足していくもの
                row = [a, b, 0]

                # そのリストを2次元配列に追加 [[0, 1, 0], [0, 2, 0], [1, 1, 0]]ok
                array_2d.append(row)


        #⑵
        FLAG_DURATION = 325.3  # ms　瞬きの継続時間
        bring=0 #瞬きしているかのフラグ
        bring_array=[]
        latest_flag_interval = None # latest_flag_intervalをNoneで初期化
        print("視線を4pxごとに分けています。")
        for i in range(len(x_coords) - 1):#実際の視線を４ピクセルずつに分けている.i+1がないため、-1で止めている
            xnum=int(x_coords[i]/4)
            ynum=int(y_coords[i]/4)

            # もし直前までに区間が宣言されていて、今のデータがその区間内ならフラグ
            if latest_flag_interval is not None:
                start, end = latest_flag_interval
                if start <=time[i] <= end:
                   bring=1 #瞬き中のフラグ


            # speed/left_dist条件を満たしたら、新しい区間で上書き
            if ((dist_speed[i] >= 40) or (dist_speed[i] <= -40)) and (left_dist[i] <= 7):
                start = time[i]
                end = time[i] + FLAG_DURATION
                latest_flag_interval = (start, end)  # ← 最新の区間で上書き
                bring=1 #瞬き中のフラグ

            if(bring==0):
                dur=time[i+1]-time[i]#視線の滞在時間。次までの差を前の視線に追加
            if(bring==1):
                dur=0

            
            bring_array.append(bring) #確認で出力するための瞬きフラグ
            bring=0#フラグをリセット
            
            # xnumとynumを要素とする一時的なリストを作成
            temp_list = [xnum, ynum,dur]
            
            # この一時的なリストを2次元配列に追加　 [[2, 1,33.4], [3, 2,54.3], [4, 3.43.3]] ok
            coords_2d.append(temp_list)
        
        
        

        #⑶
        print("滞留時間を4pxごとに9つの配列に配当しています。")
        # array1の各要素を順番に取り出す
        for item2 in coords_2d: #3要素
            for x in [-1, 0, 1]:#前後の数字で回す
                if (item2[0]+x)<0 or (item2[0]+x)>width:#ｘが画面の外に出たら次のループへ
                    continue

                for y in [-1, 0, 1]:
                    if(item2[1]+y)<0 or (item2[1]+y)>height:
                        continue

                    # array2の各要素を順番に取り出す
                    for item1 in array_2d:#3要素
                        # 配列1の前の2つの要素と、配列2の要素を比較
                        if item1[0] == (item2[0]+x) and item1[1] == (item2[1]+y):
                            # 一致した場合、array1の3つ目の要素に1を加算
                            item1[2] +=item2[2]#滞在時間を追加
                            break #for item1のループを抜ける。for yからまた始める
                        #array_2dは[[1, 1, 33.5], [1, 12, 120.2], [1, 3, 0]]のようになる maybeok
        

        #(3.5)
        print("4~140pxでヒートマップを変化させています。")
        #4~140ピクセルで変化させる 秒数をまとめる
        #for mass in range(1, 36, 2):#マスの１辺の長さ（４ｐｘ＝１）
        for mass in range(1, 4, 2):#マスの１辺の長さ（４ｐｘ＝１）
            result_array = [] #ｘピクセルごとの視線滞在時間を格納する
            wid=int(widthmax/(4*mass))
            hei=int(heightmax/(4*mass))
            for a in range(wid):
                for b in range(hei):
                    # a, b, 0を1次元リストにまとめる  3つ目の０はそのマスに視線が止まった時間を足していくもの
                    row = [a, b, 0]
                    # そのリストを2次元配列に追加 [[0, 1, 0], [0, 2, 0], [1, 1, 0]]ok
                    result_array.append(row)
                    
            if mass!=1:
                for i in array_2d:
                    a=int((i[0]*4)/(4*mass))#元の座標に戻し、適切なピクセルで割る
                    b=int((i[1]*4)/(4*mass))

                    for result_row in result_array:
                    # result_row[0]がa、result_row[1]がbと一致するか確認
                        if result_row[0] == a and result_row[1] == b:
                            # 一致した場合、result_row[2]にi[2]の秒数を加算
                            result_row[2] += i[2]  #result_arrayに秒数が追加されていくはず
                            break # 見つかったのでループを抜ける（効率化）

            else:#ピクセル数が増えないとき
                result_array=array_2d   
          


            #(4) ピクセルを変化させるループの中に入れる 3.5の中に入っている
            print("視線を4~140の大きさに変更しています。")
            pix=4*mass #正方形の１辺のピクセル数
            moji_2d = []#文字とそれが重なる４ｐｘの場所を入れる。文字は数分複製
            for i in range(len(moji)):
                x1=int((x_moji[i]-yoko)/pix)
                x2=int((x_moji[i]+yoko)/pix)
                y1=int((y_moji[i]-tate)/pix)
                y2=int((y_moji[i]+tate)/pix)
                for j in range(x2-x1+1):
                    for k in range(y2-y1+1):
                        moji_list = [x1+j, y1+k,moji[i],0] 
                        moji_2d.append(moji_list)  #[[1,1,'あ',0],[1,2,'あ',0]...]の様になっていく。最後は時間を入れる予定 ok
                


            #(5)実験値と文字を対応づける
            print("文字の位置に滞留時間をいれています。")
            for num1 in result_array:#実験値 xピクセルごとになっている
                if num1[2]==0: #もし滞留時間の合計が０ならばスキップ
                    continue

                for num2 in moji_2d:#文字の位置
                    if num1[0]==num2[0] and num1[1]==num2[1]:#もし位置が一致したら
                        num2[3]+=num1[2]#文字の横に滞在時間を追加 #[[1,1,'あ',56.3],[1,2,'あ',21.4]...] ok
                #massが広がり、複数の文字が同じ四角に存在する可能性が増えるため、forを回し続ける

            if(mass==1):
                            # 保存先のファイル名
                file_name = 'output先行研究.csv'
                # CSVファイルに書き込み
                # 'w' モード（書き込み）でファイルを開き、newline='' を指定します。
                # newline='' は、CSVファイル書き込み時に余分な空行が入るのを防ぐためのおまじないです。
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    # csv.writer オブジェクトを作成
                    writer = csv.writer(csvfile)

                    # writerow() で1d行ずつ書き込むか、writerows() で全てのデータを一度に書き込みます。
                    writer.writerows(moji_2d)

                print(f"'{file_name}' にデータを保存しました。")
          


            
            #(6)文字ごとに閾値を超えているか確認する
            print("文字ごとに滞留時間が閾値を超えているか確認しています。")
            #min_threshold
            #max_threshold
            threshold=0
            roop=0#初期ループを見分けるための変数
            know=0#単語を知っていると判断すれば１を入れる
            mojisec_2d=[]#文字ごとに最大の滞在時間と未知検知のフラグを入れる[['あ',230,1],['い',0,0]...]
            #(6)文字ごとにまとめる
            for text in moji_2d:
                if roop==0:#最初のループ時のみ通過
                    now=text[2] #現在処理している文字
                    sec=text[3]
                    roop=1
                    continue
                if roop==1:
                    if now==text[2] :#もしまだ同じ文字なら
                        if text[3]>sec:#もし新しい秒数が最大となるなら
                            sec=text[3] #置き換える
                    else :#文字が変わるなら
                        if threshold<=sec:#未知
                            know=0
                        else:#既知
                            know=1
                        now_list=[now,sec,know]#[["あ",234.33,0],["い",32.43,1]]
                        mojisec_2d.append(now_list) #それまでの文字と滞留時間の最大値、未知フラグを配列に追加
                        now=text[2]#新しい文字に置き換える
                        sec=text[3]#時刻も置き換える

            now_list=[now,sec,know]#[["あ",234.33,0],["い",32.43,1]]   
            mojisec_2d.append(now_list) #それまでの文字と滞留時間の最大値、未知フラグを配列に追加





            #(7)単語ごとに滞留時間を分ける
            if(len(restored_text)!=len(mojisec_2d)):#文章とリストの文字数を確認
                print("文章とリストの文字数が違います。プログラムを終了します。")
                print(len(restored_text),"と",len(mojisec_2d))
                print("restored_text",restored_text)
                print("new_list",mojisec_2d)
                # 終了コード 1 を指定してプログラムを異常終了させる
                sys.exit(1)

            else:#文字数が合えば         
            # 単語情報のもとリスト作成（これを都度再構築することで前ループのpred/trueが残らないようにする）
                words = []
                char_pos = 0
                for token in tagger(restored_text):
                    surface = token.surface
                    length = len(surface)
                    start = char_pos
                    end = char_pos + length - 1
                    raw_lemma = token.feature[7] if len(token.feature) > 7 else surface #feature に7番目の要素（原形）がある場合 → token.feature[7](原型) を使う。ない場合 → その形態素の表層形 surface を使う
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


                # ループ
                for j, th in enumerate(th_range):
                        # predラベル付与
                        for w in words:
                            check_start = max(0, w["start"] )
                            check_end = min(len(mojisec_2d) - 1, w["end"] ) #<=の意味だから-1
                            char_indices = range(check_start, check_end + 1)
                            flagged = False
                            for idx in char_indices:
                                if mojisec_2d[idx][1] > th:
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

                        """
                        print("\n【正解を不正解と判定した単語（偽陰性/FN）一覧】")
                        for w in words:
                            if w["true"] == 1 and w["pred"] == 0:
                                print(f'{w["word"]} （位置 {w["start"]}-{w["end"]}）')

                        print("\n【不正解を正解と判定した単語一覧】")
                        for w in words:
                            if w["true"] == 0 and w["pred"] == 1:
                                print(f'{w["word"]} （位置 {w["start"]}-{w["end"]}）')

                        print("\n\n")
                        """
                    

                        

            #(8)精度を計算

        return mojisec_2d  ###★★このreturnをどこに書くか
        

                    

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {file_path}")
        return None, None
    except KeyError:
        print(f"エラー: 必要な列 ('x'または'y')がファイル {file_path} に存在しません")
        return None, None
    except KeyError as e:
        print(f"Error: Column {e} not found in the CSV file.")
        return None
    





        

if __name__ == '__main__':
    # ここに処理したいファイル名を直接書きます★★
    file_name = 'gazedataF_sample.csv'  #いつもの出力の視線ファイル
    file_name2 = 'mojixy.csv' #文字とｘ、ｙ座標のファイル
    yoko=13.5#文字幅27/2
    tate=20#高さ20/2
    #ほかに変える部分


    print(f"--- ファイル: {file_name} を処理中 ---")
    mojisec_2d = extract_gaze_coordinates(file_name,file_name2,yoko,tate)

    if mojisec_2d is not None :
        # 抽出したデータを表示します
        print("finish")
        #print("x座標のリスト:", mojisec_2d)

#出力ファイルに入れたいもの　bring_array、dist_speed






