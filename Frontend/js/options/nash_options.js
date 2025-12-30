export function renderNashOptions(root) {
  root.innerHTML = `
    <div class="optBox">
      <div class="optTitle">Nash Equilibrium</div>

      <label class="field">
        Difficulty
        <select id="optNashDifficulty" class="select">
          <option value="easy">Easy (Pure)</option>
          <option value="medium" selected>Medium (Mixed)</option>
          <option value="hard">Hard (Combined)</option>
        </select>
      </label>

      <div id="optNashExtra"></div>
    </div>
  `;

  const diffEl = document.getElementById("optNashDifficulty");
  const extra = document.getElementById("optNashExtra");

  function renderExtra(diff) {
    if (!extra) return;

    if (diff === "easy") {
      extra.innerHTML = `
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
      `;
      return;
    }

    extra.innerHTML = `
      <label class="field">
        Size
        <select id="optNashSize" class="select">
          <option value="2">2×2</option>
          <option value="3">3×3</option>
        </select>
      </label>
    `;
  }

  renderExtra(diffEl?.value || "medium");
  diffEl?.addEventListener("change", () => renderExtra(diffEl.value));
}

export function collectNashOptions() {
  const difficulty = String(document.getElementById("optNashDifficulty")?.value || "medium");

  if (difficulty === "easy") {
    const m = Number(document.getElementById("optNashM")?.value || 2);
    const n = Number(document.getElementById("optNashN")?.value || 2);
    return { difficulty, m, n };
  }

  const size = Number(document.getElementById("optNashSize")?.value || 2);
  return { difficulty, size };
}
