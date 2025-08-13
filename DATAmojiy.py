
numy = """
'り'
'戻'
'し'
'た'
'。'
"""



# 文字列を改行で分割し、浮動小数点数のリストに変換
char_list = [char.strip() for char in numy.splitlines() if char.strip()]

# 結果を表示
#print(x_list)



#mojilist = list(zip(x_list, y_list))
#formatted_list1 = list(map(list, mojilist))

#print(formatted_list1)





numx = """
263
290
317
344
371
"""

# 文字列を改行で分割し、浮動小数点数のリストに変換
moji_list = [float(num) for num in numx.splitlines() if num]

# 結果を表示
#print(numbers_list2)

