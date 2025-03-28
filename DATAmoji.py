nummoji= """
翠
黛
の
山
々
が
連
な
り
、
湖
面
に
は
翡
翠
の
よ
う
な
"""
numbers_list = [char.strip() for char in nummoji.splitlines() if char.strip()]




numx = """
399.421875
427.807312
453.9843855
480.1614685
508.546875
534.963562
561.380249
588.026042
610.895834
631.473999
655.828125
684.213562
709.958374
733.963542
760.609375
788.994812
815.171916
838.395874
859.75
882.317729
"""

numbers_list1 = [float(num) for num in numx.splitlines() if num]

numy = """
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
229.1979218
"""

numbers_list2 = [float(num) for num in numy.splitlines() if num]

mojilist = list(zip(numbers_list, numbers_list1,numbers_list2))

# 結果を表示
#print(mojilist)