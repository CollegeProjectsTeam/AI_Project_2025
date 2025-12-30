function clampNum(v, lo, hi, fallback) {
  const x = Number(v);
  if (!Number.isFinite(x)) return fallback;
  return Math.max(lo, Math.min(hi, x));
}

export function renderMinMaxOptions(root) {
  root.innerHTML = `
    <div class="optBox">
      <div class="optTitle">MinMax (Alpha-Beta)</div>

      <label class="field">
        Difficulty
        <select id="optMinMaxDifficulty" class="select">
          <option value="easy">Easy</option>
          <option value="medium" selected>Medium</option>
          <option value="hard">Hard</option>
        </select>
      </label>

      <div class="row rowTight">
        <label class="field">
          Depth
          <input id="optMinMaxDepth" type="number" min="1" max="6" value="3" />
        </label>
        <label class="field">
          Branching
          <input id="optMinMaxBranching" type="number" min="2" max="4" value="2" />
        </label>
      </div>

      <label class="field">
        Root player
        <select id="optMinMaxRootPlayer" class="select">
          <option value="MAX">MAX</option>
          <option value="MIN">MIN</option>
        </select>
      </label>
    </div>
  `;

  const diffEl = document.getElementById("optMinMaxDifficulty");
  const depthEl = document.getElementById("optMinMaxDepth");
  const brEl = document.getElementById("optMinMaxBranching");
  const rootEl = document.getElementById("optMinMaxRootPlayer");

  const rules = {
    easy: {
      depth: { min: 1, max: 3, def: 2 },
      branching: { min: 2, max: 3, def: 2 },
    },
    medium: {
      depth: { min: 1, max: 5, def: 3 },
      branching: { min: 2, max: 4, def: 2 },
    },
    hard: {
      depth: { min: 1, max: 6, def: 4 },
      branching: { min: 2, max: 4, def: 3 },
    },
  };

  function applyNumericConstraints(diff) {
    const r = rules[diff] || rules.medium;

    if (depthEl) {
      depthEl.min = String(r.depth.min);
      depthEl.max = String(r.depth.max);
      depthEl.value = String(clampNum(depthEl.value, r.depth.min, r.depth.max, r.depth.def));
    }

    if (brEl) {
      brEl.min = String(r.branching.min);
      brEl.max = String(r.branching.max);
      brEl.value = String(clampNum(brEl.value, r.branching.min, r.branching.max, r.branching.def));
    }
  }

  function applyEasyLock(diff) {
    const isEasy = diff === "easy";
    if (!rootEl) return;

    if (isEasy) {
      rootEl.value = "MAX";
      rootEl.disabled = true;
    } else {
      rootEl.disabled = false;
    }
  }

  function applyAll(diff) {
    applyNumericConstraints(diff);
    applyEasyLock(diff);
  }

  applyAll(diffEl?.value || "medium");
  diffEl?.addEventListener("change", () => applyAll(diffEl.value));
}

export function collectMinMaxOptions() {
  const difficulty = String(document.getElementById("optMinMaxDifficulty")?.value || "medium");
  const depth = Number(document.getElementById("optMinMaxDepth")?.value || 3);
  const branching = Number(document.getElementById("optMinMaxBranching")?.value || 2);

  let root_player = String(document.getElementById("optMinMaxRootPlayer")?.value || "MAX");

  if (difficulty === "easy") {
    root_player = "MAX";
  }

  return { difficulty, depth, branching, root_player };
}