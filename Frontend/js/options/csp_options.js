function clampNum(v, lo, hi, fallback) {
  const x = Number(v);
  if (!Number.isFinite(x)) return fallback;
  return Math.max(lo, Math.min(hi, x));
}

export function renderCspOptions(root) {
  root.innerHTML = `
    <div class="optBox">
      <div class="optTitle">CSP (Backtracking)</div>

      <label class="field">
        Difficulty
        <select id="optCspDifficulty" class="select">
          <option value="easy">Easy</option>
          <option value="medium" selected>Medium</option>
          <option value="hard">Hard</option>
        </select>
      </label>

      <div class="row rowTight">
        <label class="field">
          Inference
          <select id="optCspInference" class="select">
            <option value="FC">FC</option>
            <option value="NONE">NONE</option>
          </select>
        </label>

        <label class="field">
          Consistency
          <select id="optCspConsistency" class="select">
            <option value="NONE">NONE</option>
            <option value="AC3">AC3</option>
          </select>
        </label>
      </div>

      <div class="row rowTight">
        <label class="field">
          Var heuristic
          <select id="optCspVarHeuristic" class="select">
            <option value="NONE">NONE</option>
            <option value="MRV">MRV</option>
          </select>
        </label>

        <label class="field">
          Value heuristic
          <select id="optCspValueHeuristic" class="select">
            <option value="LCV">LCV</option>
            <option value="NONE">NONE</option>
          </select>
        </label>
      </div>

      <div class="row rowTight">
        <label class="field">
          # Vars
          <input id="optCspNumVars" type="number" min="2" max="8" value="3" />
        </label>

        <label class="field">
          # Constraints
          <input id="optCspNumConstraints" type="number" min="1" max="20" value="3" />
        </label>
      </div>

      <div class="row rowTight">
        <label class="field">
          Domain min size
          <input id="optCspDomMin" type="number" min="1" max="10" value="2" />
        </label>

        <label class="field">
          Domain max size
          <input id="optCspDomMax" type="number" min="1" max="12" value="4" />
        </label>
      </div>
    </div>
  `;

  const diffEl = document.getElementById("optCspDifficulty");

  const inferenceEl = document.getElementById("optCspInference");
  const consistencyEl = document.getElementById("optCspConsistency");
  const varHEl = document.getElementById("optCspVarHeuristic");
  const valHEl = document.getElementById("optCspValueHeuristic");

  const varsEl = document.getElementById("optCspNumVars");
  const consEl = document.getElementById("optCspNumConstraints");
  const domMinEl = document.getElementById("optCspDomMin");
  const domMaxEl = document.getElementById("optCspDomMax");

  const rules = {
    easy: {
      vars: { min: 2, max: 4, def: 3 },
      constraints: { min: 1, max: 6, def: 3 },
      domMin: { min: 1, max: 4, def: 2 },
      domMax: { min: 1, max: 5, def: 4 },
    },
    medium: {
      vars: { min: 2, max: 6, def: 4 },
      constraints: { min: 1, max: 12, def: 6 },
      domMin: { min: 1, max: 8, def: 2 },
      domMax: { min: 1, max: 10, def: 5 },
    },
    hard: {
      vars: { min: 2, max: 8, def: 6 },
      constraints: { min: 1, max: 20, def: 12 },
      domMin: { min: 1, max: 10, def: 2 },
      domMax: { min: 1, max: 12, def: 6 },
    },
  };

  function applyNumericConstraints(diff) {
    const r = rules[diff] || rules.medium;

    if (varsEl) {
      varsEl.min = String(r.vars.min);
      varsEl.max = String(r.vars.max);
      varsEl.value = String(clampNum(varsEl.value, r.vars.min, r.vars.max, r.vars.def));
    }

    if (consEl) {
      consEl.min = String(r.constraints.min);
      consEl.max = String(r.constraints.max);
      consEl.value = String(clampNum(consEl.value, r.constraints.min, r.constraints.max, r.constraints.def));
    }

    if (domMinEl) {
      domMinEl.min = String(r.domMin.min);
      domMinEl.max = String(r.domMin.max);
      domMinEl.value = String(clampNum(domMinEl.value, r.domMin.min, r.domMin.max, r.domMin.def));
    }

    if (domMaxEl) {
      domMaxEl.min = String(r.domMax.min);
      domMaxEl.max = String(r.domMax.max);
      domMaxEl.value = String(clampNum(domMaxEl.value, r.domMax.min, r.domMax.max, r.domMax.def));
    }

    if (domMinEl && domMaxEl) {
      const a = Number(domMinEl.value);
      const b = Number(domMaxEl.value);
      if (Number.isFinite(a) && Number.isFinite(b) && a > b) {
        domMinEl.value = String(b);
      }
    }
  }

  function applyEasyLocks(diff) {
    const isEasy = diff === "easy";

    if (consistencyEl) {
      if (isEasy) {
        consistencyEl.value = "NONE";
        consistencyEl.disabled = true;
      } else {
        consistencyEl.disabled = false;
      }
    }

    if (valHEl) {
      if (isEasy) {
        valHEl.value = "NONE";
        valHEl.disabled = true;
      } else {
        valHEl.disabled = false;
      }
    }

    if (inferenceEl) {
      inferenceEl.disabled = false;
    }

    if (varHEl) {
      varHEl.disabled = false;
    }
  }

  function applyAll(diff) {
    applyNumericConstraints(diff);
    applyEasyLocks(diff);
  }

  applyAll(diffEl?.value || "medium");
  diffEl?.addEventListener("change", () => applyAll(diffEl.value));
}

export function collectCspOptions(isTestGeneration = false) {
  const diffEl = document.getElementById("optCspDifficulty");
  const inferenceEl = document.getElementById("optCspInference");
  const consistencyEl = document.getElementById("optCspConsistency");
  const varHEl = document.getElementById("optCspVarHeuristic");
  const valHEl = document.getElementById("optCspValueHeuristic");

  const varsEl = document.getElementById("optCspNumVars");
  const consEl = document.getElementById("optCspNumConstraints");
  const domMinEl = document.getElementById("optCspDomMin");
  const domMaxEl = document.getElementById("optCspDomMax");

  function randomChoice(options) {
    return options[Math.floor(Math.random() * options.length)];
  }

  return {
    difficulty: diffEl?.value || "medium",
    inference: isTestGeneration ? randomChoice(["FC", "NONE"]) : inferenceEl?.value || "NONE",
    consistency: isTestGeneration ? randomChoice(["NONE", "AC3"]) : consistencyEl?.value || "NONE",
    var_heuristic: isTestGeneration ? randomChoice(["NONE", "MRV"]) : varHEl?.value || "NONE",
    value_heuristic: isTestGeneration ? randomChoice(["LCV", "NONE"]) : valHEl?.value || "NONE",
    num_vars: clampNum(varsEl?.value, 2, 8, 3),
    num_constraints: clampNum(consEl?.value, 1, 20, 3),
    domain_min: clampNum(domMinEl?.value, 1, 10, 2),
    domain_max: clampNum(domMaxEl?.value, 1, 12, 4),
  };
}