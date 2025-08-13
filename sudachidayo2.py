import fugashi
from fugashi import Tagger


tagger = fugashi.Tagger()

#text = "そのようだ"

#or token in tagger(text):
    #print(f"\n{token.surface}")
    #print("  全feature:", token.feature)
    #print("  要素数:", len(token.feature))
    #for i, value in enumerate(token.feature):
        #print(f"  [{i}] {value}")



#品詞も含めた検索
def search_word(word, expected_pos1, try_fallback=True):
    print(f"🔍 検索: 「{word}」 / 品詞: 「{expected_pos1}」")
    found = False

    for token in tagger(word):
        surface = token.surface
        pos1 = token.feature.pos1  # 形状詞など
        base = token.feature.lemma if token.feature.lemma != "*" else surface

        print(f"🔸語: {surface} / 品詞: {pos1} / 原形: {base}")
        if surface == word and pos1 == expected_pos1:
            print("✅ 表層形一致＋品詞一致")
            found = True
            break
        elif base == word and pos1 == expected_pos1:
            print("✅ 原形一致＋品詞一致")
            found = True
            break

    if not found and try_fallback:
        print(f"🔁 Fallbackで原形を用いた再検索を試みます...")
        # fallbackとして lemma（原形）で再帰的に検索（無限ループ防止のため try_fallback=False）
        for token in tagger(word):
            lemma = token.feature.lemma
            if lemma != "*" and lemma != word:
                return search_word(lemma, expected_pos1, try_fallback=False)

        print("❌ 該当なし")
        return False

    return found

search_word("よう", "形状詞")   