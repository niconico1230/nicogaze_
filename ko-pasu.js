//#検索するプログラム

fetch("word_index_min.json")
  .then(response => response.json())
  .then(wordIndex => {
    const word = "事";
    const pos = "名詞";
    const key = JSON.stringify([word, pos]); // Python側と対応させる！

    if (wordIndex.hasOwnProperty(key)) {
      const info = wordIndex[key];
      console.log(`🔍 単語: ${word}（品詞: ${pos}）`);
      console.log(`📊 出現頻度: ${info.frequency} 回`);
      console.log(`📈 PMW（百万語あたり）: ${info.pmw}`);
    } else {
      console.log(`❌ 単語「${word}」は見つかりませんでした。`);
    }
  });