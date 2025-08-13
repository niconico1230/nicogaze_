from fugashi import Tagger

tagger = Tagger()
text = "これ"

for token in tagger(text):
    print(f"単語: {token.surface}")
    print("featureリスト:")
    for idx, feat in enumerate(token.feature):
        # [0]と[7]はコメントつきで明示
        if idx == 0:
            print(f"  [{idx}] : {feat}  ←品詞")
        elif idx == 7:
            print(f"  [{idx}] : {feat}  ←基本形")
        else:
            print(f"  [{idx}] : {feat}")
    print("-" * 30)