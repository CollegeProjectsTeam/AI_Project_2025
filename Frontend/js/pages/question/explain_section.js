export function lockExplainSection({ dom }) {
  if (dom.btnExplain) dom.btnExplain.disabled = true;
  if (dom.explainPanel) dom.explainPanel.open = false;
  if (dom.explainOut) dom.explainOut.textContent = "";
}

export function unlockExplainSection({ dom }) {
  if (dom.btnExplain) dom.btnExplain.disabled = false;
}

function formatExplanation(data) {
  if (!data || typeof data !== "object") return "No explanation available.";

  if ("hits" in data || "missing" in data || "wrong" in data) {
    const lines = [];
    if (typeof data.correct === "boolean") lines.push(`Correct: ${data.correct ? "Yes" : "No"}`);
    if ("score" in data) lines.push(`Score: ${data.score}`);
    if ("hits" in data) lines.push(`Hits: ${data.hits}`);
    if ("missing" in data) lines.push(`Missing: ${data.missing}`);
    if ("wrong" in data) lines.push(`Wrong: ${data.wrong}`);
    return lines.join("\n");
  }

  if (data.type === "nqueens" || data.problem_name === "N-Queens") {
    const lines = [];
    if (typeof data.correct === "boolean") lines.push(`Correct: ${data.correct ? "Yes" : "No"}`);
    if ("score" in data) lines.push(`Score: ${data.score}`);
    if (data.fastest_algorithm) lines.push(`Fastest algorithm: ${data.fastest_algorithm}`);
    if (data.execution_times) lines.push(`Timing details available in Raw JSON.`);
    return lines.length ? lines.join("\n") : "N-Queens explanation is available in Raw JSON.";
  }

  const keys = Object.keys(data).slice(0, 12);
  return keys.map((k) => `${k}: ${String(data[k])}`).join("\n");
}

export function renderExplanation({ dom, data }) {
  if (!dom.explainOut) return;
  dom.explainOut.textContent = formatExplanation(data);
}

export function initExplainSection({ dom, state }) {
  if (!dom.btnExplain || !dom.explainPanel) {
    return;
  }

  dom.btnExplain.addEventListener("click", () => {
    if (!state?.hasChecked) return;
    dom.explainPanel.open = !dom.explainPanel.open;
  });

  lockExplainSection({ dom });
}