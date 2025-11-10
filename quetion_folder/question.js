let unknownWords = [];

function handleClick(event) {
  const clickedIndex = parseInt(event.target.dataset.index);

  // 事前にPythonから渡された単語位置リスト（JSON）
  // e.g., [{"word": "図書館", "start": 4, "end": 7}, ...]
  const wordPositions = window.tokenizedWords; // Python側から渡す想定

  const matched = wordPositions.find(w => clickedIndex >= w.start && clickedIndex < w.end);
  if (!matched) return;

  // すでに選ばれていれば取り消し（toggle）
  const isAlready = unknownWords.some(w => w.start === matched.start && w.end === matched.end);
  if (isAlready) {
    unknownWords = unknownWords.filter(w => w.start !== matched.start || w.end !== matched.end);
  } else {
    unknownWords.push(matched);
  }

  // 色付けを更新
  updateHighlight();
}

function updateHighlight() {
  document.querySelectorAll('#text-container span').forEach(span => {
    const idx = parseInt(span.dataset.index);
    const isSelected = unknownWords.some(w => idx >= w.start && idx < w.end);
    span.style.backgroundColor = isSelected ? 'yellow' : '';
  });
}

