numx = """
287.2757958
295.178499
319.4069506
366.0376277
425.7379197
492.6457453
564.094499
604.5183368
"""

# 文字列を改行で分割し、浮動小数点数のリストに変換
x_list = [float(num) for num in numx.splitlines() if num]



#mojilist = list(zip(x_list, y_list))
#formatted_list = list(map(list, mojilist))

#print(formatted_list)

