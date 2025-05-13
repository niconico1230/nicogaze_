# 配列サイズの定義
SIZE = 10
numbers = []  # 空のリストを定義

print("10個の浮動小数点数を入力してください：")

# ユーザーからの入力
for i in range(SIZE):
    num = float(input(f"{i + 1}番目の数値: "))  # 入力をfloat型に変換
    numbers.append(num)  # リストに追加

# 比較用の数値を入力
target_value = float(input("\n比較用の数値を入力してください: "))

# 符号を考慮した誤差を計算
differences = [num - target_value for num in numbers]
average_error = sum(differences) / len(differences)

# 絶対値の差を求めて平均化
absolute_diffs = [abs(target_value - num) for num in numbers]
average_diff = sum(absolute_diffs) / len(absolute_diffs)



print(average_error)#符号を考慮した平均誤差
print(target_value-average_error)
print("\n")
print(average_diff)#符号を考慮した平均誤差
print(target_value+average_error)
print(target_value-average_error)