import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('yourdata.csv')


# 外れ値判定したいカラム名を指定
col = 'your_column'

# 四分位範囲（IQR）で外れ値を判定
Q1 = df[col].quantile(0.25)
Q3 = df[col].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

# 外れ値だけ抽出
outliers = df[(df[col] < lower) | (df[col] > upper)]

# 外れ値の個数と全体の個数
outlier_count = len(outliers)
total_count = len(df)

# 割合（パーセント）で出力
outlier_ratio = outlier_count / total_count * 100
print(f"外れ値の割合: {outlier_ratio:.2f}% ({outlier_count} / {total_count})")


plt.boxplot(df['your_column'])
plt.show()