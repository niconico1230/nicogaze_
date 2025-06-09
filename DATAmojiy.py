numx = """
303.3
330
356.7
383.3
407.4
429.4
454.2
480.8
505.3
529.8
554
572.9
594.2
618.4
641.2
663
683.7
703.6
721.5
740.3
762.1
784.1
806
828.7
852.9
879.6
903
926.3
953
976.7
"""

# 文字列を改行で分割し、浮動小数点数のリストに変換
moji_list = [float(num) for num in numx.splitlines() if num]

# 結果を表示
#print(numbers_list2)


numy = """
製
造
現
場
で
は
職
掌
が
細
か
く
分
か
れ
て
お
り
、
そ
れ
ぞ
れ
の
役
割
を
正
確
に
"""




# 文字列を改行で分割し、浮動小数点数のリストに変換
char_list = [char.strip() for char in numy.splitlines() if char.strip()]

# 結果を表示
#print(x_list)



#mojilist = list(zip(x_list, y_list))
#formatted_list1 = list(map(list, mojilist))

#print(formatted_list1)
