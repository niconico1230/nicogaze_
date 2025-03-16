/*
 * This function calculates a measurement for how precise 
 * the eye tracker currently is which is displayed to the user
 この関数は視線追跡の精度を計算し、ユーザーにその結果を表示する役割を担っています。
*/
function calculatePrecision(past50Array) { //past50Array: 直近の50回の視線予測データ。x50 と y50 に分かれており、それぞれ X 座標と Y 座標の予測値が含まれています。
  var windowHeight = window.innerHeight;
  var windowWidth = window.innerWidth;
  //、ユーザーの画面サイズを取得します。これを基に中央の位置を決定します。

  // Retrieve the last 50 gaze prediction points
  var x50 = past50Array[0];
  var y50 = past50Array[1];
  //過去50回の視線予測データを x50 と y50 に分けて格納します。

  // Calculate the position of the point the user is staring at
  var staringPointX = windowWidth / 2;
  var staringPointY = windowHeight / 2;
  //画面の中央（ユーザーが見つめるべき点）の座標を計算します。

  var precisionPercentages = new Array(50); //配列に視線予測精度を格納します。
  calculatePrecisionPercentages(precisionPercentages, windowHeight, x50, y50, staringPointX, staringPointY);
  //この関数を呼び出して、各予測点の精度を計算します。
  var precision = calculateAverage(precisionPercentages);
  //視線予測精度を全体で平均し、その結果を precision に格納します。
  

  // Return the precision measurement as a rounded percentage
  return Math.round(precision);//計算した精度を四捨五入して返します。
};

/*
 * Calculate percentage accuracy for each prediction based on distance of
 * the prediction point from the centre point (uses the window height as
 * lower threshold 0%)
 * 各視線予測点が中央の点からどれだけ離れているかを計算し、その距離を基に精度のパーセンテージを求めるもの
 */
//precisionPercentages 配列に各予測点の精度を格納します
//staringPointX と staringPointY は中央の点の座標です。
function calculatePrecisionPercentages(precisionPercentages, windowHeight, x50, y50, staringPointX, staringPointY) {
  for (x = 0; x < 50; x++) {//ループを使って、過去50回の予測データに対して精度を計算します。
    // Calculate distance between each prediction and staring point
    var xDiff = staringPointX - x50[x];
    var yDiff = staringPointY - y50[x];
    var distance = Math.sqrt((xDiff * xDiff) + (yDiff * yDiff));
    // 中央の点と予測点の座標差を使って、ユーザーの視線予測点が中央の点からどれだけ離れているか（距離）を計算します。

    // Calculate precision percentage
    var halfWindowHeight = windowHeight / 2;
    //画面の高さの半分を基準に、予測点が中央からどれだけ離れているかを基に精度を計算します。
    var precision = 0;
    if (distance <= halfWindowHeight && distance > -1) {
      //距離が中央から画面の高さの半分以内であれば、精度は 100 - (distance / halfWindowHeight * 100) と計算されます。
      precision = 100 - (distance / halfWindowHeight * 100);
    } else if (distance > halfWindowHeight) {
      precision = 0;
    } else if (distance > -1) {
      precision = 100;
    }

    // Store the precision
    precisionPercentages[x] = precision;
  }
}

/*
 * Calculates the average of all precision percentages calculated
50回分の精度パーセンテージの平均を計算するために使います。 
*/
function calculateAverage(precisionPercentages) {
  var precision = 0;
  for (x = 0; x < 50; x++) {
    precision += precisionPercentages[x];
  }
  precision = precision / 50;
  return precision;
}
