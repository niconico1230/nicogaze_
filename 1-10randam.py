import random

# 1〜10の中からランダムに1つ選ぶ
for i in range(0,10):
    num = random.randint(1, 10)
    print(i,":")
    print("選ばれた数字:", num)
