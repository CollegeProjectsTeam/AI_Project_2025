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

  if (typeof data.explanation === "string" && data.explanation.trim()) {
    return data.explanation.trim();
  }

  if (Array.isArray(data.explanation_lines) && data.explanation_lines.length) {
    return data.explanation_lines.join("\n");
  }

  if (typeof data.explanation_lines === "string" && data.explanation_lines.trim()) {
    return data.explanation_lines.trim();
  }

  if ("hits" in data || "missing" in data || "wrong" in data) {
    const lines = [];
    if (typeof data.correct === "boolean")
      lines.push(`Correct: ${data.correct ? "Yes" : "No"}`);
    if ("score" in data) lines.push(`Score: ${data.score}`);
    if ("hits" in data) lines.push(`Hits: ${data.hits}`);
    if ("missing" in data) lines.push(`Missing: ${data.missing}`);
    if ("wrong" in data) lines.push(`Wrong: ${data.wrong}`);
    return lines.join("\n");
  }

  if (typeof data.message === "string" && data.message.trim()) {
    return data.message.trim();
  }

  return "No explanation available.";
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