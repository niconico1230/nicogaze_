window.onload = async function() {//ページが完全に読み込まれた後に実行される非同期関数。ここに WebGazer の起動や初期設定が含まれています。

    //start the webgazer tracker
    await webgazer.setRegression('ridge') /* 回帰モデルの設定：'ridge' は視線を予測するためのアルゴリズム（回帰モデル）currently must set regression and tracker */
        //他にも 'weightedRidge' や 'threadedRidge' なども選べます
        //.setTracker('clmtrackr')
        .setGazeListener(function(data, clock) {
          //data には {x, y} 座標（視線の位置）が入ってる 下のコメントアウトを外せばログをとったり描画できる
          //   console.log(data); /* data is an object containing an x and y key which are the x and y prediction coordinates (no bounds limiting) */
          //clock は WebGazer 開始からの経過時間（ミリ秒）
          //   console.log(clock); /* elapsed time in milliseconds since webgazer.begin() was called */
        })
        .saveDataAcrossSessions(true)//true にするとユーザーの視線データやキャリブレーションの進捗が ブラウザに保存されます
        //ページを再読み込みしてもデータが保持されます（localStorageやIndexedDB経由）
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
    };
    setup();

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
