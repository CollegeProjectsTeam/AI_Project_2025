export function renderNQueensOptions(root) {
  root.innerHTML = `
    <div class="optBox">
      <div class="optTitle">N-Queens</div>
      <label class="field">
        N
        <input id="optNQueensN" type="number" min="4" value="4" />
      </label>
    </div>
  `;
}

export function collectNQueensOptions() {
  const el = document.getElementById("optNQueensN");
  return { n: Number(el?.value || 4) };
}
