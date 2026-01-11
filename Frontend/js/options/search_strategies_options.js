function clampNum(v, lo, hi, fallback) {
  const x = Number(v);
  if (!Number.isFinite(x)) return fallback;
  return Math.max(lo, Math.min(hi, x));
}

const LABELS = {
  nqueens: "N (board size)",
  graph_coloring: "Nodes",
  knights_tour: "N (board size)",
  generalized_hanoi: "Disks",
};

const RULES = {
  easy: {
    nqueens: { min: 2, max: 5, def: 4 },
    graph_coloring: { min: 4, max: 9, def: 6 },
    knights_tour: { min: 5, max: 7, def: 5 },
    generalized_hanoi: { min: 3, max: 6, def: 4 },
  },
  medium: {
    nqueens: { min: 4, max: 8, def: 6 },
    graph_coloring: { min: 6, max: 14, def: 9 },
    knights_tour: { min: 5, max: 9, def: 6 },
    generalized_hanoi: { min: 3, max: 10, def: 5 }
  },
  hard: {
    nqueens: { min: 6, max: 10, def: 8 },
    graph_coloring: { min: 10, max: 18, def: 12 },
    knights_tour: { min: 7, max: 10, def: 8 },
    generalized_hanoi: { min: 6, max: 14, def: 8 },
  },
};

function getRule(diff, problem) {
  const d = RULES[diff] || RULES.medium;
  return d[problem] || d.nqueens;
}

function applySizeUI({ diff, problem, sizeEl, labelEl }) {
  const r = getRule(diff, problem);

  if (labelEl) {
    labelEl.textContent = LABELS[problem] || "Size";
  }

  if (sizeEl) {
    sizeEl.min = String(r.min);
    sizeEl.max = String(r.max);
    sizeEl.value = String(clampNum(sizeEl.value, r.min, r.max, r.def));
  }
}

export function renderSearchStrategiesOptions(root) {
  root.innerHTML = `
    <div class="optBox">
      <div class="optTitle">Search Strategies</div>

      <label class="field">
        Difficulty
        <select id="optSSDifficulty" class="select">
          <option value="easy">Easy</option>
          <option value="medium" selected>Medium</option>
          <option value="hard">Hard</option>
        </select>
      </label>

      <label class="field">
        Problem
        <select id="optSSProblem" class="select">
          <option value="nqueens" selected>N-Queens</option>
          <option value="graph_coloring">Graph Coloring</option>
          <option value="knights_tour">Knights Tour</option>
          <option value="generalized_hanoi">Generalized Hanoi</option>
        </select>
      </label>

      <label class="field">
        <span id="optSSSizeLabel">N (board size)</span>
        <input id="optSSSize" type="number" min="4" max="12" value="8" />
      </label>
    </div>
  `;

  const diffEl = document.getElementById("optSSDifficulty");
  const probEl = document.getElementById("optSSProblem");
  const sizeEl = document.getElementById("optSSSize");
  const labelEl = document.getElementById("optSSSizeLabel");

  function applyAll() {
    const diff = String(diffEl?.value || "medium");
    const problem = String(probEl?.value || "nqueens");
    applySizeUI({ diff, problem, sizeEl, labelEl });
  }

  applyAll();
  diffEl?.addEventListener("change", applyAll);
  probEl?.addEventListener("change", applyAll);
}

export function collectSearchStrategiesOptions() {
  const difficulty = String(document.getElementById("optSSDifficulty")?.value || "medium");
  const problem = String(document.getElementById("optSSProblem")?.value || "nqueens");

  const r = getRule(difficulty, problem);
  const sizeRaw = document.getElementById("optSSSize")?.value;
  const size = clampNum(sizeRaw, r.min, r.max, r.def);

  const out = { difficulty, problem, size };

  if (problem === "nqueens") out.n = size;
  if (problem === "graph_coloring") out.nodes = size;
  if (problem === "knights_tour") out.n = size;
  if (problem === "generalized_hanoi") out.disks = size;

  return out;
}

export function renderNQueensOptions(root) {
  return renderSearchStrategiesOptions(root);
}
export function collectNQueensOptions() {
  return collectSearchStrategiesOptions();
}