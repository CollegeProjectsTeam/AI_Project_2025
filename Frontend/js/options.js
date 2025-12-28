export function renderOptions(root, selection) {
  root.innerHTML = "";

  if (!selection) {
    root.innerHTML = `<div class="mutedSmall">Select a subchapter to see its options.</div>`;
    return;
  }

  const ch = selection.chapter_number;
  const sc = selection.subchapter_number;

  if (ch === 1 && sc === 1) {
    root.innerHTML = `
      <div class="optBox">
        <div class="optTitle">N-Queens</div>
        <label class="field">
          N
          <input id="optNQueensN" type="number" min="4" value="4" />
        </label>
      </div>
    `;
    return;
  }

  if (ch === 2 && sc === 1) {
    root.innerHTML = `
      <div class="optBox">
        <div class="optTitle">Nash (Pure)</div>
        <div class="row rowTight">
          <label class="field">
            m
            <input id="optNashM" type="number" min="2" max="5" value="2" />
          </label>
          <label class="field">
            n
            <input id="optNashN" type="number" min="2" max="5" value="2" />
          </label>
        </div>
      </div>
    `;
    return;
  }

  if (ch === 2 && (sc === 2 || sc === 3)) {
    const title = sc === 2 ? "Nash (Mixed)" : "Nash (Combined)";
    root.innerHTML = `
      <div class="optBox">
        <div class="optTitle">${title}</div>
        <label class="field">
          Size
          <select id="optNashSize" class="select">
            <option value="2">2×2</option>
            <option value="3">3×3</option>
          </select>
        </label>
      </div>
    `;
    return;
  }

  root.innerHTML = `<div class="mutedSmall">No options available for this subchapter yet.</div>`;
}

export function collectOptions(selection) {
  if (!selection) return {};

  const ch = selection.chapter_number;
  const sc = selection.subchapter_number;

  if (ch === 1 && sc === 1) {
    const el = document.getElementById("optNQueensN");
    return { n: Number(el?.value || 4) };
  }

  if (ch === 2 && sc === 1) {
    const m = Number(document.getElementById("optNashM")?.value || 2);
    const n = Number(document.getElementById("optNashN")?.value || 2);
    return { m, n };
  }

  if (ch === 2 && (sc === 2 || sc === 3)) {
    const size = Number(document.getElementById("optNashSize")?.value || 2);
    return { size };
  }

  return {};
}
