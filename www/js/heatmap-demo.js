// ページをリロードしてもデータを保存するか
window.saveDataAcrossSessions = true;

// heatmap configuration 半径,最大/最小の透明度,ぼかし具合
const config = {
  radius: 25,
  maxOpacity: .5,
  minOpacity: 0,
  blur: .75
};

// Global variables ヒートマップを管理するためのインスタンス
let heatmapInstance;

window.addEventListener('load', async function() {
  // Init webgazer
  if (!window.saveDataAcrossSessions) {
      var localstorageDataLabel = 'webgazerGlobalData';
      localforage.setItem(localstorageDataLabel, null);
      var localstorageSettingsLabel = 'webgazerGlobalSettings';
      localforage.setItem(localstorageSettingsLabel, null);
  }
  const webgazerInstance = await webgazer.setRegression('ridge') /* 回帰モデルcurrently must set regression and tracker */
    .setTracker('TFFacemesh')
    .saveDataAcrossSessions(true)//true にするとユーザーの視線データやキャリブレーションの進捗が ブラウザに保存されます
    .begin();
  
  // Turn off video
  webgazerInstance.showVideoPreview(true) /* ビデオプレビューを表示  */
    .showPredictionPoints(true); /* 予測ポイントを表示shows a square every 100 milliseconds where current prediction is */
  
    // Enable smoothing
  webgazerInstance.applyKalmanFilter(true); //カルマンフィルターを有効にして、視線追跡データのノイズを減らし、滑らかな追跡結果を提供
  
  // Set up heatmap parts
  setupHeatmap(); //ヒートマップの準備をするための関数を呼び出します
  webgazer.setGazeListener( eyeListener );//視線データが更新されるたびにeyeListener関数が呼び出されるよう設定します。
});

window.addEventListener('beforeunload', function() {//ページが閉じられる直前、またはリロードされる直前に実行される処理を設定します。
  if (window.saveDataAcrossSessions) {
      webgazer.end();//trueの場合: セッションデータを保持する必要があるため、WebGazerのセッションを終了（webgazer.end()）しますが、既存のデータは消去しません。
  } else {
      localforage.clear();//falseの場合: セッションデータを保持しないため、localforage.clear()を呼び出してすべての保存データを削除します。
  }
});

// Trimmed down version of webgazer's click listener since the built-in one isn't exported
// Needed so we can have just the click listener without the move listener
// (The move listener was creating a lot of drift)
async function clickListener(event) {//クリックイベントの処理
  webgazer.recordScreenPosition(event.clientX, event.clientY, 'click'); // eventType[0] === 'click'
}//マウスクリックの位置（clientXとclientY）を記録し、「クリックイベント」として扱います。
//クリックのみを追跡するように最適化され、マウス移動リスナーを使わない設計です。

function setupHeatmap() {//ヒートマップの初期化
  // Don't use mousemove listener
  webgazer.removeMouseEventListeners(); //マウス移動イベントリスナーの無効化: 不要なデータ取得を防ぎます。
  document.addEventListener('click', clickListener);//ユーザーのクリックを記録します。

  // Get the window size
  let height = window.innerHeight;
  let width = window.innerWidth;

  // Set up the container コンテナの大きさをウィンドウサイズに適応させます。
  let container = document.getElementById('heatmapContainer');
  container.style.height = `${height}px`;
  container.style.width = `${width}px`;
  config.container = container;

  // create heatmap
  heatmapInstance = h337.create(config);//追跡データをビジュアル化するためのヒートマップを生成します。
}

// Heatmap buffer
let lastTime;
let lastGaze;
let isLogging = true; //ログのオンオフを決める変数

async function eyeListener(data, clock) {
  // data is the gaze data, clock is the time since webgazer.begin()
  
  if (data && isLogging)  {//データをコンソールに表示
    console.log("視線位置:","x  " ,data.x,"y  ", data.y);
    console.log("経過時間(ms):", clock);
  }

  // Init if lastTime not set
  if(!lastTime) {
    lastTime = clock; //以前の視線データ（lastGaze）を記録。
  }

  // In this we want to track how long a point was being looked at,
  // so we need to buffer where the gaze moves to and then on next move
  // we calculate how long the gaze stayed there.
  if(!!lastGaze) {
    if(!!lastGaze.x && !!lastGaze.y) { //視線がどのポイントをどれだけの時間見ていたかを計算。
      let duration = clock-lastTime;
      let point = {
        x: Math.floor(lastGaze.x),//移動するたびに記録、一定の時間ではない
        y: Math.floor(lastGaze.y),
        value: duration//前回取得からの経過時間
      }
      heatmapInstance.addData(point); //視線の情報（x, y座標と視線時間）をヒートマップに反映。

      // 既存データを取得して、新しいデータを追加
      let storedData = await localforage.getItem('gazeDataList') || [];
      storedData.push(point);
      
      // 配列として保存
      await localforage.setItem('gazeDataList', storedData);
    }
  }

  lastGaze = data;
  lastTime = clock;
}
function toggleLogging() {
  isLogging = !isLogging;
  const btn = document.getElementById('toggleLoggingBtn');
  btn.textContent = isLogging ? "ログ停止" : "ログ開始";
}
