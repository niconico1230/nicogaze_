/*
 * Sets store_points to true, so all the occuring prediction
 * points are stored
 * WebGazerの設定を変更して、視線予測点を記録する状態にします。
キャリブレーションの精度を出すときに使っている
*/
function store_points_variable(){
  webgazer.params.storingPoints = true;
}

/*
 * Sets store_points to false, so prediction points aren't
 * stored any more
 * 、WebGazerの設定を変更して、視線予測点を保存しない状態にします。
 */
function stop_storing_points_variable(){
  webgazer.params.storingPoints = false;
}
