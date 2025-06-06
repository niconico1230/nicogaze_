

let loggingEnabled = true; // ログの状態を管理する変数（デフォルトはログが有効）
let recordingEnabled = false; // 記録管理用
let recordedData = []; // 記録データ配列
let currentClock = 0; // clock時間を保持する変数
let startButtonCount = 0;   // 開始ボタンが押された回数
let filenum=0;//ファイルの個数
// カーソル位置を記録する変数
let cursorX = 0;
let cursorY = 0;
let lastOpenness = null;//上瞼と下瞼の差（右目）
let isBlinking=0; // グローバルスコープで定義（数値で管理）
let lasttime=null;
let wordData = {}; // kopasu.jsonのデータを格納する変数
let tokenizer = null;//kuromojiに使用




// ログのオン・オフを切り替える関数
//function toggleLogging() {
  //  loggingEnabled = !loggingEnabled;
    // ログ状態に応じてボタンのテキストを変更
    //const button = document.getElementById('toggleLoggingBtn');
    //button.textContent = loggingEnabled ? 'ログを停止' : 'ログを開始';
//}

// 記録データを保存する関数
async function loadKopasuData() {
    try {
        const response = await fetch('js/word_index_long.json');  // kopasu.jsonファイルを取得
        const data = await response.json();  // JSONデータをパース
        wordData = data;  // JSONデータをwordDataに格納
        console.log("word_index_long.json が正常にロードされました");
    } catch (error) {
        console.error("word_index_long.jsonの読み込みに失敗しました:", error);
    }
}
// "m" キーで特定の単語と品詞を検索
document.addEventListener('keydown', function(event) {
    if (event.key === "m" || event.key === "M") {
        // 例えば「に 助詞」を検索
        const word = "う";
        const pos = "感動詞";
        searchWordAndPOS(word, pos);
    }
});
// "m" キーで特定の単語と品詞を検索
document.addEventListener('keydown', function(event) {
    if (event.key === "n" || event.key === "N") {
        // 例えば「に 助詞」を検索
        const word = "Ｖ・Ｏ";
        const pos = "名詞";
        searchWordAndPOS(word, pos);
    }
});



//function initKuromoji() {
  //  kuromoji.builder({ dicPath: "https://cdn.jsdelivr.net/npm/kuromoji@0.1.2/dict/" }).build((err, builtTokenizer) => {
    //    if (err) {
      //      console.error("エラー:", err);
        //    return;
        //}
        // トークナイザーが無事に初期化されました
        //console.log("Kuromojiが初期化されました");
        //tokenizer = builtTokenizer;
    //});
//}
document.addEventListener('keydown', function(event) {
    if (event.key === "l" || event.key === "L") {
        ////if (!tokenizer) {
            ////console.warn("⚠️ Kuromojiの初期化がまだ完了していません");
            ////return;
        ///}
        const text = "明日は晴れると思われる。気温は25度になるでしょう。";
        const tokens = tokenizer.tokenize(text);

         // 結果を表示（tokenごとの表記と品詞）
     
         tokens.forEach(token => {
            console.log(`単語: ${token.basic_form}, 品詞: ${token.pos}`);
         });

        analyzeGazeText(cursorX, cursorY); // カーソル位置でテキスト解析
        // もし視線位置で解析したい場合は recordedData などから最新データを取得して渡す
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById("textContainer");

    // テキスト配列（必要に応じて増やせます）
    const texts = [
        "test\n大学での研究活動において、私は特に斯界における技術の発展に注目している。技術革新が進む中で、時に眩惑的な魅力を感じることがあるが、それが一時的なものであることを見極めることが重要だ。狡猾に思える手法に引き寄せられることもあるが、その背後に隠れたリスクを冷静に分析し、着実に前進することが求められる。過去には、膠着状態に陥ったこともあったが、そのような状況を乗り越えるためには、適切なタイミングで再調整を行い、柔軟に対応することが大切だ。また、仲間との昵懇な関係が築かれていなければ、困難な時に助け合うことが難しくなる。",
        "次に表示される文章の中で、職業に関する単語を１秒注視してください。\n\n(例)医者,教師,弁護士,俳優,モデル,作家,警察\n\n\n",
        "世の中にはさまざまな職業があり、それぞれに価値と魅力があります。医者は人々の健康を守るために日々努力し、教師は未来を担う子どもたちに知識を伝えます。また、弁護士は正義を守るために法律の知識を駆使し、俳優は舞台や映画で感情を表現して人々に感動を届けます。その演技は見る人の心に深く残り、時には人生に影響を与えることさえあります。モデルはファッションや広告で美しさを世界に発信し、人々の感性や流行に影響を与える存在です。作家は言葉で世界を描き出して読者の心を動かします。医者の診察や治療は人々の命を救い、その冷静な判断力と技術は多くの人々の安心と希望につながっています。",
        
        "次に表示される文章の中で、科目に関する単語を１秒注視してください。\n\n(例)国語,数学,物理,化学,美術,体育,日本史,世界史,道徳\n\n\n",
        "私は将来、人々の生活を支える技術者になりたいと考えています。国語で身につけた表現力は、主に相手に伝える力として役立ちます。数学の論理的思考は、問題解決の基盤です。機械の動きを理解するには物理の知識が不可欠で、材料の性質や反応は化学で学びました。設計段階では、美術で鍛えた感性がデザインに活かせると思います。健康な体を維持するために、体育の大切さも意識しています。さらに、日本史を通じて日本の発展を学び、世界史では他国の技術や文化との違いから多くの刺激を受けました。何より、道徳の授業で培った正直さや責任感を大切にし、信頼される人間でありたいと思います。これらの学びが、自分の夢の実現を支えてくれると信じています。",

       "夏の風が轟々と窓を揺らす教室で、ふと祖母のことを思い出した。授業中にもかかわらず、風の音が妙に心に沁みて、懐かしい記憶を呼び起こす。小さいころ、風邪を引いた私のために、祖母は庭から摘んだ蓬を煎じてくれた。夏休みに帰省したときには、朝早くから畑に出て、採れたての玉蜀黍を茹でてくれた。台所に広がる甘い香り、湯気の向こうに見えた祖母の笑顔が、今もはっきりと思い出せる。時間は過ぎ、私は大人になろうとしている。忙しさに追われる日々の中で、ふと立ち止まったとき、よみがえるのはそんな温かい記憶だ。畢竟、人のぬくもりとは、言葉や形ではなく、日々の小さな積み重ねの中にこそ宿るものなのだと、今になって思う。",
       "小さいころ、筆者が風邪をひいたとき、祖母は何をしてくれましたか？\nA. 冷たい飲み物をくれた\nB. 蓬を煎じてくれた\nC. 病院に連れて行ってくれた\nD. 子守唄を歌ってくれた\n\n\n\n\n",
       "この文章全体のテーマとして最もふさわしいものはどれですか？\nA. 自然の豊かさを語るエッセイ\nB. 家庭料理のレシピ紹介\nC. 日常における家族の温かさと記憶の大切さ\nD. 授業中に感じた夏の暑さへの不満\n\n\n\n\n",
       "文章中には直接書かれていないが、次のうち文脈から推測できることとして適切なものはどれですか？\nA. 筆者の祖母は現在も畑仕事をしている\nB. 筆者は祖母と一緒に暮らしていた時期がある\nC. 筆者は祖母との思い出を大切にしている\nD. 筆者は風の音が嫌いである\n\n\n\n\n",

       "高校時代、彼の襟度は誰もが認めるもので、どんな時でも冷静で落ち着いた態度を崩さなかった。クラスメイトからも信頼され、いつも笑顔で周囲を和ませる存在だった。だが、私が最も頼りにしていたのは、そんな彼が悩んでいる時にこそ見せる真剣な眼差しだった。ある日、私が大きな失敗をして落ち込んでいると、彼は黙ってその場に座り、私に話を聞かせてくれた。何も言わずにただ寄り添ってくれる彼に、私は思わず縋るように泣いてしまった。その夜、彼の家に招かれ、手作りの料理を囲んで少しずつ心を癒された。温かい饗応と共に、私たちの間に流れるのは言葉以上の信頼と絆だった。昔、些細なことで出来た心の罅割れが、彼の支えによって完全に埋められたように感じた。",
       "登場人物の「彼」の特徴として、最も適切なものはどれですか？\na) 常に厳しく、冷徹な性格\nb) 落ち着きと冷静さを持ち合わせ、周囲から信頼されている\nc) 何も考えず行動するタイプ\nd) 他人を見下すことが多い\n\n\n\n\n",
       "「私」が落ち込んでいる理由は何ですか？\na) 家族との問題\nb) 自分の将来に対する不安\nc) 大きな失敗をしてしまったから\nd) 友人との喧嘩\n\n\n\n\n",
       "彼が「私」に提供したのは、どのような支援でしたか？\na) お金を貸してくれた\nb) 何も言わずに寄り添ってくれ、料理で心を癒してくれた\nc) 知識や勉強を教えてくれた\nd) ただ無関心だった\n\n\n\n\n"
    ];
    let currentIndex = -1;
    
    let firstKeyPressHandled = false;
    document.addEventListener('keydown', function (event) {
        if (event.key === 'p' || event.key === 'P') {
             // 最初の1回だけ「こんにちは」を消す
            if (!firstKeyPressHandled) {
                helloText.remove();  // 「こんにちは」を消す
                firstKeyPressHandled = true;
            }
            currentIndex = (currentIndex + 1) % texts.length;
            container.innerText = texts[currentIndex];
            container.style.display = "block"; // すでに表示中でも維持（非表示→表示切替が必要な場合に備えて）
            // テキスト描画後に、文字ごとの座標を取得（次のフレームで）
            setTimeout(() => {
                logCharacterCenters(container);
            }, 50); // 少し遅らせて確実に描画された後に処理
        }
    });
    function logCharacterCenters(container) {
        const text = container.textContent;

        // テキストノードがなければ何もしない
        if (!container.firstChild) return;

        for (let i = 0; i < text.length; i++) {
            const range = document.createRange();
            range.setStart(container.firstChild, i);
            range.setEnd(container.firstChild, i + 1);
            const rect = range.getBoundingClientRect();

            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            console.log(`文字: ${text[i]} X: ${centerX.toFixed(1)} Y: ${centerY.toFixed(1)}`);
        }
    }
});

// キー押下イベントをリッスン
document.addEventListener('keydown', function(event) {
    // "R" キーが押された場合に記録を開始/停止
    if (event.key === "r" || event.key === "R") {
        // 記録の開始/停止をトグル
        recordingEnabled = !recordingEnabled;

        // ボタンのテキストを更新（視覚的にわかりやすくするため）
        document.getElementById('toggleRecordingBtn').textContent = recordingEnabled ? "記録停止" : "記録開始";
 
    // 記録開始時にデータをリセットし、定期保存を開始
    if (recordingEnabled) {
        //recordedData = [];
        recordedData.push([]); // 新しい記録データの配列を追加
        startButtonCount++;
        console.log("ーー記録開始",startButtonCount,"ーー");

    } else {
         // 記録停止時に自動でデータ保存
         emailjs.send("service_mpj0atd", "template_lm8l6xt", {
                                name: "airi",
                                message: "文章を読み終わりました。",
                                to_email: "af22090@shibaura-it.ac.jp"
                            }).then(function(response) {
                                console.log("メール送信成功:", response.status, response.text);
                            }, function(error) {
                                console.log("送信エラー:", error);
         });         
         saveDataToFile();
         console.log("ーー記録停止",startButtonCount,"ーー");
    }
}

        // キー押下イベントをリッスン
   // document.addEventListener('keydown', function(event) {
        // "s" キーが押された場合に保存処理を実行
        //if (event.key === "s" || event.key === "S") {
           //     saveDataToFile();
        //}
});

// マウス移動イベントをリッスン
//document.addEventListener('mousemove', function(event) {
  //  cursorX = event.clientX;
    ////cursorY = event.clientY;
//});


window.onload = async function() {//ページが完全に読み込まれた後に実行される非同期関数。ここに WebGazer の起動や初期設定が含まれています。
 
    ///start the webgazer tracker
    await webgazer.setRegression('ridge') /* 回帰モデルの設定：'ridge' は視線を予測するためのアルゴリズム（回帰モデル）currently must set regression and tracker */
        //他にも 'weightedRidge' や 'threadedRidge' なども選べます
        //.setTracker('clmtrackr')
        .saveDataAcrossSessions(true)//true にするとユーザーの視線データやキャリブレーションの進捗が ブラウザに保存されます
        //ページを再読み込みしてもデータが保持されます（localStorageやIndexedDB経由）
        //クリックしたときのみデータが来ていた
        .begin()
        //WebGazerを起動します。実行しないと何も始まりません。

        webgazer.showPredictionPoints(false) /* ??視線予測の位置に 小さな四角形を100msごとに表示 shows a square every 100 milliseconds where current prediction is */
                .showVideoPreview(false) /*ブラウザ上に Webカメラの映像を表示するかどうか    shows all video previews */
                .applyKalmanFilter(true); /*カルマンフィルターを有効化,視線予測のブレ（ノイズ）を軽減して、スムーズな動きを実現 Kalman Filter defaults to on. Can be toggled by user. */

        webgazer.addMouseEventListeners();
          // kopasu.jsonのデータを読み込む
          await loadKopasuData();

          ////if (typeof kuromoji === "undefined") {
            ////console.error("❌ kuromojiが読み込まれていません。スクリプトの順序を確認してください。");
        ////} else {
            /////initKuromoji(); // 直接初期化
       //// }

    
        webgazer.setGazeListener( function(data, clock) {//視線追跡
            // clockの時間を保持
            currentClock = clock;
            // 開始時間の記録
            const start = performance.now();
            if (lasttime !== null) {
                const interval = start - lasttime;
                //console.log(`⏱ WebGazer 更新間隔: ${interval.toFixed(5)} ms`);
            }
        
            lasttime =start;

            
            if (data && recordingEnabled) {
                let currentData = recordedData[recordedData.length - 1]; // 最新の記録データ配列
                currentData.push({
                //recordedData.push({
                    time: clock,
                    x: data.x,
                    y: data.y,
                    //cursorX: cursorX, // カーソル位置X
                    //cursorY: cursorY,  // カーソル位置Y
                    //diffX: data.x - cursorX,
                    //diffY: data.y - cursorY,
                    blink: isBlinking, // 👈 ここ追加 1がまばたき
                    openness: lastOpenness // ← ここで保持して保存
                });
                //console.log("記録中:", startButtonCount,"時間：",clock, "視線位置:", "x:", data.x, "y:", data.y, "カーソル位置:", "x:", cursorX, "y:", cursorY);
            }
           
           if (data && data.x && data.y) {
            if(!isTransparent){
             displayGazePoint(data.x, data.y); //視線移動を持続的に可視化したいならここ・・・
           }
        }
        
        })
    

    //Set up the webgazer video feedback.
    var setup = function() {

        //Set up the main canvas. The main canvas is used to calibrate the webgazer.
        //画面全体サイズのキャンバスを作成.キャリブレーションの点を表示するために使います
        var canvas = document.getElementById("plotting_canvas");//HTML内の <canvas id="plotting_canvas"> を取得して、canvas という変数に入れてる。
        canvas.width = window.innerWidth; //canvas.width と canvas.height は描画解像度（ピクセル単位）
        canvas.height = window.innerHeight;//window.innerWidth と window.innerHeight は、現在のブラウザウィンドウの幅と高さ。
        canvas.style.position = 'fixed'; //スクロールしても画面に固定されたまま

        // ここで willReadFrequently を設定したキャンバスとコンテキストを作成 追加
        const context = canvas.getContext('2d', { willReadFrequently: true });
        //2D描画用の「コンテキスト（描画環境）」を取得。
        //willReadFrequentlyがあると、getImageData() などのピクセル取得処理がパフォーマンス最適化されることがある。
    };
    setup();

     // クリックイベントをリッスン
     document.addEventListener('click', function(event) {
        // クリック時に現在の時計時間を表示
        console.log(`%cクリック地点: x = ${event.clientX}, y = ${event.clientY}%c`, 'color: red; font-weight: bold; font-size: 13px;');
        // 現在の `clock` を取得
        //console.log('クリックした時間: ', currentClock);
        console.log('%cクリックした時間: %s', 'color: red; font-weight: bold; font-size: 13px;', currentClock);
        
    });

     // キャンバスクリアボタンの設定
     const clearButton = document.getElementById("clearCanvasBtn");
     clearButton.addEventListener("click", clearScreen);

};





// 🔽 ここに関数を追加！ 🔽
function getEyelidFeatures(faceLandmarks) {
    // 左目の瞼のポイント
    const leftEyelid = [
        faceLandmarks[159], faceLandmarks[145]  // 左瞼の特徴点
    ];
    // 右目の瞼のポイント
    const rightEyelid = [
        faceLandmarks[386], faceLandmarks[374] // 右瞼の特徴点
    ];
    return  {
        leftEyelid: leftEyelid.map(point => ({ x: point[0], y: point[1] })),
        rightEyelid: rightEyelid.map(point => ({ x: point[0], y: point[1] }))
    };
}
function getEyeOpenness(eyelidPoints) {
    const top = eyelidPoints[0];
    const bottom = eyelidPoints[1];
    const dx = top.x - bottom.x;
    const dy = top.y - bottom.y;
    const result = Math.sqrt(dx * dx + dy * dy);
    lastOpenness = result; // 👈 グローバル変数に保持（ただしあまり推奨しない）
    if(lastOpenness<5.0){
        isBlinking=1;//まばたき
    }
    else{
        isBlinking=0;//のっとまばたき
    }

    return result;  // 上下の距離（ユークリッド距離）
}



let lastX = null, lastY = null; // 前回の座標を記録する変数
let isTransparent = false; // 視線の色が透明かどうかを管理

function displayGazePoint(x, y) {//視線を描画
    const canvas = document.getElementById("plotting_canvas");
    const context = canvas.getContext('2d');
    
    // 以前の視線位置を消去
    //context.clearRect(0, 0, canvas.width, canvas.height);
    
    context.globalAlpha = 0.3; // 線と円の透明度を設定
    // 線を描画（前回の座標があれば）
    if (lastX !== null && lastY !== null) {
        context.beginPath();
        context.moveTo(lastX, lastY); // 前回の点から
        context.lineTo(x, y); // 現在の点まで線を引く
        context.lineWidth = 2; // 線の太さ
        context.strokeStyle = 'rgba(92, 92, 202, 0.5)'; // 半透明の青
        context.stroke();
    }


    // 視線位置に円を描画
    context.beginPath();
    context.arc(x, y, 3, 0, 5 * Math.PI); // 10pxの円を描画
    if (isTransparent) {
        context.fillStyle = 'rgba(216, 64, 64, 0.7)'; // 透明に設定
    } else {
        context.fillStyle = 'rgba(92, 92, 202, 0.5)'; // 半透明の青
    }
    //context.fillStyle = 'blue'; // 円の色を赤に設定
    context.fill();

    
    // 現在の座標を保存（次の描画時に使用）
    lastX = x;
    lastY = y;

};



// 単語と品詞を検索する関数
function searchWordAndPOS(word, pos) {
    const key = `[\"${word}\", \"${pos}\"]`;  // 検索するキーを作成
    if (wordData[key]) {
        console.log(`単語「${word}」、品詞「${pos}」が見つかりました。`);
        console.log(`Frequency: ${wordData[key].frequency}, PMW: ${wordData[key].pmw}`);
        return wordData[key];  // 見つかったデータを返す
    } else {
        console.log(`単語「${word}」、品詞「${pos}」はword_index_long.jsonに存在しません。`);
        return null;
    }
}

function analyzeGazeText(x, y) {
    if (!tokenizer) {
        console.warn("⚠️ kuromojiがまだ初期化されていません");
        return;
    }

    const element = document.elementFromPoint(x, y);
    if (element && element.innerText) {
        const rawText = element.innerText.trim();
        if (rawText === "") return;

        const tokens = tokenizer.tokenize(rawText);
        const result = tokens.map(token => `${token.surface_form} [${token.pos}]`).join(", ");

        console.log(`🎯 視線位置のテキスト: "${rawText}"`);
        console.log(`🔍 形態素解析: ${result}`);

        // 任意：HTML表示
        const outputEl = document.getElementById("output");
        if (outputEl) outputEl.innerText = result;
    }
}





// キャンバスをクリアする関数
function clearScreen() {
    const canvas = document.getElementById("plotting_canvas");
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height); // キャンバス全体をクリア
    console.log('キャンバスがクリアされました');
}

// Set to true if you want to save the data even if you reload the page.
// グローバル設定で、true の場合キャリブレーションや視線データが再読み込み後も保持されます
window.saveDataAcrossSessions = true;

//ページを閉じる/リロードする時に WebGazer を終了する処理
//データは保持されつつ、セッションを終了させます（特にビデオストリームのクリーンアップ）
window.onbeforeunload = function() {
    webgazer.end();
}


// データ保存
function saveDataToFile() {
    if (recordedData.length === 0) {
        alert("記録データがありません");
        return;
    }
    

    // xとyそれぞれのファイル内容を準備
    let contentX = "";
    let contentY = "";
    
    
    // 動的にヘッダーを作成x y
    recordedData.forEach((_, index) => {
        contentX += `time${index + 1},x${index + 1},blink${index + 1},openness${index + 1},`;
        contentY += `time${index + 1},y${index + 1},blink${index + 1},openness${index + 1},`;
    });
    contentX = contentX.slice(0, -1) + "\n"; // 最後のカンマを削除し改行
    contentY = contentY.slice(0, -1) + "\n"; // 最後のカンマを削除し改行


    // 最大データ数を取得
    const maxLength = Math.max(...recordedData.map(recordSet => recordSet.length));

    // 各行に対応するデータを挿入
    for (let i = 0; i < maxLength; i++) {
        recordedData.forEach(recordSet => {
            if (recordSet[i]) {
                contentX += `${recordSet[i].time},${recordSet[i].x},${recordSet[i].blink},${recordSet[i].openness},`; // x 座標 カーソルと差
                contentY += `${recordSet[i].time},${recordSet[i].y},${recordSet[i].blink},${recordSet[i].openness},`; // y 座標　カーソル
            } else {
                contentX += ",,,,"; // データがない場合は空白
                contentY += ",,,,"; // データがない場合は空白
            }
        });
        contentX = contentX.slice(0, -1) + "\n"; // 最後のカンマを削除し改行
        contentY = contentY.slice(0, -1) + "\n"; // 最後のカンマを削除し改行
    }
    // ファイル名に開始回数とタイムスタンプを追加
    const filenameX = `gaze_mouse_x_${startButtonCount}_${filenum}.csv`; // x用のファイル名
    const filenameY = `gaze_mouse_y_${startButtonCount}_${filenum}.csv`; // y用のファイル名


    // x用ファイルの生成
    const blobX = new Blob([contentX], { type: "text/csv" });
    const urlX = URL.createObjectURL(blobX);
    const aX = document.createElement("a");
    aX.href = urlX;
    aX.download = filenameX;
    aX.click();
    URL.revokeObjectURL(urlX); // リソース解放


    // y用のファイルをダウンロード
  
    const blobY = new Blob([contentY], { type: "text/csv" });
    const urlY = URL.createObjectURL(blobY);
    const aY = document.createElement("a");
    aY.href = urlY;
    aY.download = filenameY;
    aY.click();
    URL.revokeObjectURL(urlY); // リソース解放

    // ✅ データリセット処理を追加
    recordedData = [];
    startButtonCount = 0;
    filenum+=1;
    console.log("記録データがリセットされました");
}



/**
 * Restart the calibration process by clearing the local storage and reseting the calibration point
 */
function Restart(){
    document.getElementById("Accuracy").innerHTML = "<a>Not yet Calibrated</a>";
    webgazer.clearData(); // WebGazer内部に保存されたデータをクリア
    ClearCalibration();  // キャリブレーションの点の状態をリセット
    PopUpInstruction();  //// 説明モーダルやポップアップを表示
}