

let loggingEnabled = true; // ログの状態を管理する変数（デフォルトはログが有効）
let recordingEnabled = false; // 記録管理用
let recordedData = []; // 記録データ配列
let currentClock = 0; // clock時間を保持する変数
let startButtonCount = 0;   // 開始ボタンが押された回数

// ログのオン・オフを切り替える関数
//function toggleLogging() {
  //  loggingEnabled = !loggingEnabled;
    // ログ状態に応じてボタンのテキストを変更
    //const button = document.getElementById('toggleLoggingBtn');
    //button.textContent = loggingEnabled ? 'ログを停止' : 'ログを開始';
//}


// 記録開始/停止ボタンの設定
document.addEventListener("DOMContentLoaded", () => {
document.getElementById('toggleRecordingBtn').addEventListener('click', () => {
    recordingEnabled = !recordingEnabled;
    document.getElementById('toggleRecordingBtn').textContent = recordingEnabled ? "記録停止" : "記録開始";

    // 記録開始時にデータをリセットし、定期保存を開始
    if (recordingEnabled) {
        recordedData = [];
    } else {
         // 記録停止時に自動でデータ保存
         saveDataToFile();
    }
});
});


window.onload = async function() {//ページが完全に読み込まれた後に実行される非同期関数。ここに WebGazer の起動や初期設定が含まれています。
 
    ///start the webgazer tracker
    await webgazer.setRegression('ridge') /* 回帰モデルの設定：'ridge' は視線を予測するためのアルゴリズム（回帰モデル）currently must set regression and tracker */
        //他にも 'weightedRidge' や 'threadedRidge' なども選べます
        //.setTracker('clmtrackr')
        .setGazeListener(function(data, clock) {//視線追跡
            
            // clockの時間を保持
            currentClock = clock;
            
            if (data && recordingEnabled) {
                recordedData.push({
                    time: clock,
                    x: data.x,
                    y: data.y
                });
                console.log("記録中 - 時間:", clock, " 視線位置:", "x:", data.x, "y:", data.y);
            }
           // ログが有効な場合のみログを表示
           //if (data &&loggingEnabled) {
            //console.log("経過時間(ms):", clock,"  視線位置:","x " ,data.x,"y ", data.y,);
            //console.log("経過時間(ms):", clock);
            //data には {x, y} 座標（視線の位置）が入ってる 下のコメントアウトを外せばログをとったり描画できる
           //  console.log(data); /* data is an object containing an x and y key which are the x and y prediction coordinates (no bounds limiting) */
          //clock は WebGazer 開始からの経過時間（ミリ秒）
            //console.log(clock); /* elapsed time in milliseconds since webgazer.begin() was called */
          // }
           if (data && data.x && data.y) {
             displayGazePoint(data.x, data.y); //視線移動を持続的に可視化したいならここ・・・

        }
        })
        .saveDataAcrossSessions(true)//true にするとユーザーの視線データやキャリブレーションの進捗が ブラウザに保存されます
        //ページを再読み込みしてもデータが保持されます（localStorageやIndexedDB経由）
        //クリックしたときのみデータが来ていた
        .begin()
        //WebGazerを起動します。実行しないと何も始まりません。

        webgazer.showVideoPreview(true) /*ブラウザ上に Webカメラの映像を表示するかどうか    shows all video previews */
                .showPredictionPoints(false) /* ??視線予測の位置に 小さな四角形を100msごとに表示 shows a square every 100 milliseconds where current prediction is */
                .applyKalmanFilter(true); /*カルマンフィルターを有効化,視線予測のブレ（ノイズ）を軽減して、スムーズな動きを実現 Kalman Filter defaults to on. Can be toggled by user. */

        webgazer.addMouseEventListeners();

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

let lastX = null, lastY = null; // 前回の座標を記録する変数
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
        context.strokeStyle = 'rgba(92, 92, 202, 0.5)'; // 半透明の青
        context.lineWidth = 2; // 線の太さ
        context.stroke();
    }


    // 視線位置に円を描画
    context.beginPath();
    context.arc(x, y, 3, 0, 2 * Math.PI); // 10pxの円を描画
    context.fillStyle = 'rgba(92, 92, 202, 0.5)'; // (R,G,B,透明度), 0.3で薄め
    //context.fillStyle = 'blue'; // 円の色を赤に設定
    context.fill();

    
    // 現在の座標を保存（次の描画時に使用）
    lastX = x;
    lastY = y;
};

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

    let content = "時間(ms), X座標, Y座標\n";
    recordedData.forEach(data => {
        content += `${data.time}, ${data.x}, ${data.y}\n`;
    });

     // ファイル名に開始回数とタイムスタンプを追加
     const filename = `gaze_data_${startButtonCount}.txt`;


    // テキストファイル生成
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    // ダウンロードリンク作成
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();

    URL.revokeObjectURL(url); // リソース解放

    console.log("データが自動保存されました");
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
