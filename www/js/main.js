

let loggingEnabled = true; // ログの状態を管理する変数（デフォルトはログが有効）

// ログのオン・オフを切り替える関数
function toggleLogging() {
    loggingEnabled = !loggingEnabled;
    // ログ状態に応じてボタンのテキストを変更
    const button = document.getElementById('toggleLoggingBtn');
    button.textContent = loggingEnabled ? 'ログを停止' : 'ログを開始';
}

let currentClock = 0; // clock時間を保持する変数

window.onload = async function() {//ページが完全に読み込まれた後に実行される非同期関数。ここに WebGazer の起動や初期設定が含まれています。
 
     // 全ての<span>タグを取得
     const spans = document.querySelectorAll('#textContainer span');

     spans.forEach(span => {
         // 各<span>タグの位置とサイズを取得
         const rect = span.getBoundingClientRect();
 
         // 中心位置を計算 (x, y)
         const centerX = rect.left + rect.width / 2;
         const centerY = rect.top + rect.height / 2;
 
         // 結果をコンソールに表示
         console.log(`中心位置 of ${span.textContent}: x = ${centerX}, y = ${centerY}`);
     });

    //start the webgazer tracker
    await webgazer.setRegression('ridge') /* 回帰モデルの設定：'ridge' は視線を予測するためのアルゴリズム（回帰モデル）currently must set regression and tracker */
        //他にも 'weightedRidge' や 'threadedRidge' なども選べます
        //.setTracker('clmtrackr')
        .setGazeListener(function(data, clock) {//視線追跡

            // clockの時間を保持
            currentClock = clock;

           // ログが有効な場合のみログを表示
           if (data &&loggingEnabled) {
            console.log("視線位置:","x  " ,data.x,"y  ", data.y);
            console.log("経過時間(ms):", clock);
            //data には {x, y} 座標（視線の位置）が入ってる 下のコメントアウトを外せばログをとったり描画できる
           //  console.log(data); /* data is an object containing an x and y key which are the x and y prediction coordinates (no bounds limiting) */
          //clock は WebGazer 開始からの経過時間（ミリ秒）
            //console.log(clock); /* elapsed time in milliseconds since webgazer.begin() was called */
           }
        })
        .saveDataAcrossSessions(true)//true にするとユーザーの視線データやキャリブレーションの進捗が ブラウザに保存されます
        //ページを再読み込みしてもデータが保持されます（localStorageやIndexedDB経由）
        //クリックしたときのみデータが来ていた
        .begin()
        //WebGazerを起動します。実行しないと何も始まりません。

        webgazer.showVideoPreview(true) /*ブラウザ上に Webカメラの映像を表示するかどうか    shows all video previews */
            .showPredictionPoints(true) /* ??視線予測の位置に 小さな四角形を100msごとに表示 shows a square every 100 milliseconds where current prediction is */
            .applyKalmanFilter(true); /*カルマンフィルターを有効化,視線予測のブレ（ノイズ）を軽減して、スムーズな動きを実現 Kalman Filter defaults to on. Can be toggled by user. */

    //Set up the webgazer video feedback.
    var setup = function() {

        //Set up the main canvas. The main canvas is used to calibrate the webgazer.
        //画面全体サイズのキャンバスを作成.キャリブレーションの点を表示するために使います
        var canvas = document.getElementById("plotting_canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        canvas.style.position = 'fixed';

        // ここで willReadFrequently を設定したキャンバスとコンテキストを作成 追加
        //const context = canvas.getContext('2d', { willReadFrequently: true });
    };
    setup();

     // クリックイベントをリッスン
     document.addEventListener('click', function(event) {
        // クリック時に現在の時計時間を表示
        console.log(`クリック地点: x = ${event.clientX}, y = ${event.clientY}`);
        // 現在の `clock` を取得
        console.log('クリックした時間: ', currentClock);
    });

};

// Set to true if you want to save the data even if you reload the page.
// グローバル設定で、true の場合キャリブレーションや視線データが再読み込み後も保持されます
window.saveDataAcrossSessions = true;//？？どこにクリア処理があるかわからない

//ページを閉じる/リロードする時に WebGazer を終了する処理
//データは保持されつつ、セッションを終了させます（特にビデオストリームのクリーンアップ）
window.onbeforeunload = function() {
    webgazer.end();
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

