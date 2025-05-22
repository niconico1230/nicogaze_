var PointCalibrate = 0;//ユーザーがクリックしたキャリブレーションポイントの数をカウントする変数です。最初は 0 に設定されています。
var CalibrationPoints={};//それぞれのキャリブレーションポイント（画面上のクリック可能な場所）に対して、何回クリックしたかを格納するオブジェクト

// Find the help modal
var helpModal;//ヘルプモーダルを表示するための変数ですが、実際にモーダルを操作する際に初期化されます

let helloText = document.createElement('div');//文字出力

/**
 * Clear the canvas and the calibration button.
 * キャリブレーション用のボタンを非表示にし、キャンバス（plotting_canvas）をクリアする関数です。これによって、以前のキャリブレーション結果やデータが消去されます。
 */
function ClearCanvas(){ 
  document.querySelectorAll('.Calibration').forEach((i) => {
    i.style.setProperty('display', 'none');
  });
  var canvas = document.getElementById("plotting_canvas");
  canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
}

/**
 * Show the instruction of using calibration at the start up screen.
 * キャリブレーション開始のポップアップ表示
 * 指示が確認されたら、キャリブレーションのポイントが表示される関数 ShowCalibrationPoint() が呼ばれます。
 */
function PopUpInstruction(){
  ClearCanvas();
  swal({
    title:"キャリブレーション",
    text: "背景の下にあるバーが上に上がったらokを押し、キャリブレーションを開始してください。",
    buttons:{
      cancel: false,
      confirm: true
    }
  }).then(isConfirm => {
    ShowCalibrationPoint();
  });

}
/**
  * Show the help instructions right at the start.
  */
function helpModalShow() {
    if(!helpModal) {
        helpModal = new bootstrap.Modal(document.getElementById('helpModal'))
    }
    helpModal.show();
}

function calcAccuracy() {//精度計算のための関数
    // show modal
    // notification for the measurement process
    swal({
        title: "キャリブレーション精度の測定",
        text: "体勢を変えず、真ん中の点を5秒間見つめてください。",
        closeOnEsc: false,// ESCキーでモーダルを閉じられないように設定
        allowOutsideClick: false,// モーダルの外側をクリックして閉じられないように設定
        closeModal: true // モーダルが閉じる際に特別な処理が必要な場合（実行するかどうかのフラグ）
    }).then( () => {
        // makes the variables true for 5 seconds & plots the points
    
        store_points_variable(); // 視線データを一定時間保存する関数start storing the prediction points
    
        sleep(5000).then(() => {
                stop_storing_points_variable(); // 視線データを一定時間保存する関数stop storing the prediction points

                var past50 = webgazer.getStoredPoints(); // retrieve the stored points
                var precision_measurement = calculatePrecision(past50);//保存された50個のデータから精度を計算する関数です。
                var accuracyLabel = "<a>Accuracy | "+precision_measurement+"%</a>";
                document.getElementById("Accuracy").innerHTML = accuracyLabel; // Show the accuracy in the nav bar.
                swal({
                    title: "Your accuracy measure is " + precision_measurement + "%",
                    allowOutsideClick: false,
                    buttons: {
                        cancel: "Recalibrate",
                        confirm: true,
                    }
                }).then(isConfirm => {
                  const container = document.getElementById("textContainer");
                  //container.style.display = "block";  // テキストを表示

                      const text = container.textContent;
                    
                      for (let i = 0; i < text.length; i++) {
                    const range = document.createRange();
                      range.setStart(container.firstChild, i);
                       range.setEnd(container.firstChild, i + 1);
                        const rect = range.getBoundingClientRect();
                         中心座標を計算
                        const centerX = rect.left + rect.width / 2;
                        const centerY = rect.top + rect.height / 2;
                    
                        console.log(`文字: ${text[i]} X: ${centerX} Y: ${centerY}`);
                      }
                    //});

                        if (isConfirm){
                       // メール送信

                       
                            //clear the calibration & hide the last middle button
                            ClearCanvas();
                            webgazer.removeMouseEventListeners();//学習をなくす　追加した
                            isTransparent=true;

                            
                            helloText.className = 'custom-hello';
                            helloText.textContent = 'これから文章を読んでもらいます。\n頭を動かさず、指示をお待ちください';
                            document.body.appendChild(helloText);
                            
                            
                        } else {
                            //use restart function to restart the calibration
                            document.getElementById("Accuracy").innerHTML = "<a>Not yet Calibrated</a>";
                            webgazer.clearData();
                            ClearCalibration();
                            ClearCanvas();
                            ShowCalibrationPoint();
                        }
                });
        });
    });
}

function calPointClick(node) {//5回クリックされたらそのポイントが黄色に変わり、無効化されます。
    const id = node.id;

    if (!CalibrationPoints[id]){ // initialises if not done
        CalibrationPoints[id]=0;
    }
    CalibrationPoints[id]++; // increments values

    if (CalibrationPoints[id]==5){ //only turn to yellow after 5 clicks
        node.style.setProperty('background-color', 'yellow');
        node.setAttribute('disabled', 'disabled');
        PointCalibrate++;
    }else if (CalibrationPoints[id]<5){
        //Gradually increase the opacity of calibration points when click to give some indication to user.
        var opacity = 0.2*CalibrationPoints[id]+0.2;
        node.style.setProperty('opacity', opacity);
    }

    //Show the middle calibration point after all other points have been clicked.
    if (PointCalibrate == 1){//16
        document.getElementById('Pt5').style.removeProperty('display');
    }

    if (PointCalibrate >= 2){ //17 // last point is calibrated
        // grab every element in Calibration class and hide them except the middle point.
        document.querySelectorAll('.Calibration').forEach((i) => {
            i.style.setProperty('display', 'none');
        });
        //すべてのポイントがクリックされると、最後の中央ポイントを表示し、キャリブレーションが完了したことを確認します。
        document.getElementById('Pt5').style.removeProperty('display');

        // clears the canvas
        var canvas = document.getElementById("plotting_canvas");
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

        // Calculate the accuracy
        calcAccuracy();
    }
}

/**
 * Load this function when the index page starts.
* This function listens for button clicks on the html page
* checks that all buttons have been clicked 5 times each, and then goes on to measuring the precision
*/
//$(document).ready(function(){
function docLoad() { //ページが読み込まれると、docLoad 関数が実行され、キャリブレーションポイントのクリックイベントを設定します。
  ClearCanvas();
  helpModalShow();
    
    // click event on the calibration buttons
    document.querySelectorAll('.Calibration').forEach((i) => {
        i.addEventListener('click', () => {
            calPointClick(i);
        })
    })
};
window.addEventListener('load', docLoad);

/**
 * Show the Calibration Points
 */
function ShowCalibrationPoint() {//キャリブレーションポイントを表示する
  document.querySelectorAll('.Calibration').forEach((i) => {
    i.style.removeProperty('display');
  });
  // initially hides the middle button
  document.getElementById('Pt5').style.setProperty('display', 'none');//最初は中央ポイント（Pt5）は表示されません。
}

/**
* This function clears the calibration buttons memory
*/
function ClearCalibration(){//キャリブレーションをリセットするための関数です。すべてのキャリブレーションボタンの色を元に戻し、クリック数をリセットします。
  // Clear data from WebGazer

  document.querySelectorAll('.Calibration').forEach((i) => {
    i.style.setProperty('background-color', 'red');
    i.style.setProperty('opacity', '0.2');
    i.removeAttribute('disabled');
  });

  CalibrationPoints = {};
  PointCalibrate = 0;
}

// sleep function because java doesn't have one, sourced from http://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
//指定された時間だけ待機するためのスリープ関数です。sleep(5000) で5秒間の待機を行います
function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}


