import { dom } from "./question_test/dom.js";
import { state } from "./question/state.js"; // reuse same state object shape
import { initCheckSection } from "./question/check_section.js";
import { initExplainSection, lockExplainSection } from "./question/explain_section.js";
import { initJsonSection, lockJsonSection } from "./question/json_section.js";
import { resetQuestionUI, showQuestionText, showQuestionRender, showError, clearError } from "./question/view.js";
import { renderAnswerOptions } from "./question/answer_options.js";
import { tryRenderSearchStrategies } from "./question/search_strategies_render.js";
import { renderCspQuestion } from "./question/csp_render.js";
import { renderGameTree } from "./question/tree_view.js";

function loadTest() {
  const s = sessionStorage.getItem("smar_last_test");
  if (!s) return null;
  try { return JSON.parse(s); } catch { return null; }
}

function normQuestion(raw) {
  const q = raw || {};
  const meta = q.meta || {};
  return {
    ...q,
    meta,
    question_id: q.question_id ?? q.qid ?? q.id ?? meta.qid ?? meta.question_id ?? null,
    question_text: q.question_text ?? q.text ?? q.prompt ?? ""
  };
}

function setProgress(i, n) {
  const el = document.getElementById("testProgress");
  if (el) el.textContent = `Question ${i + 1} / ${n}`;
}

function setNav(i, n) {
  const prev = document.getElementById("btnPrev");
  const next = document.getElementById("btnNext");
  if (prev) prev.disabled = i <= 0;
  if (next) next.disabled = i >= n - 1;
}

function renderSpecial(q) {
  const meta = q.meta || {};

  // Search strategies renderer
  if (tryRenderSearchStrategies(dom, q)) return true;

  // CSP renderer
  if (meta.group === "csp" || meta.type === "csp") {
    if (dom.questionRender) {
      dom.questionRender.classList.remove("hidden");
      renderCspQuestion(dom.questionRender, q);
      if (dom.questionText) dom.questionText.classList.add("hidden");
      return true;
    }
  }

  // MinMax tree (optional)
  const tree = meta.tree || meta.instance?.tree || q.tree || null;
  const rootPlayer = meta.root_player || meta.rootPlayer || "MAX";
  if (dom.treePanel) {
    if (tree) {
      dom.treePanel.classList.remove("hidden");
      renderGameTree(dom.treePanel, tree, rootPlayer);
    } else {
      dom.treePanel.classList.add("hidden");
      dom.treePanel.innerHTML = "";
    }
  }

  return false;
}

function main() {
  // init sections EXACT like question.js (minus catalog/generate)
  initCheckSection({ dom, state });

  try { initExplainSection({ dom, state }); } catch (e) { console.error(e); }
  try { initJsonSection({ dom, state }); } catch (e) { console.error(e); }

  const payload = loadTest();
  if (!payload || payload.ok !== true || !Array.isArray(payload.test)) {
    showError(dom, "No test data found. Generate a test first.");
    return;
  }

  const test = payload.test.map(normQuestion);
  let idx = 0;

  function render() {
    clearError(dom);
    resetQuestionUI(dom);

    lockExplainSection({ dom });
    lockJsonSection({ dom });

    if (dom.explainOut) dom.explainOut.textContent = "";
    if (dom.out) dom.out.textContent = "";
    if (dom.checkResult) dom.checkResult.classList.add("hidden");


    const q = test[idx];
    if (!q?.question_id) {
      showError(dom, "Question is missing question_id (cannot check).");
      return;
    }

    state.currentQuestionId = q.question_id;
    state.hasChecked = false;
    state.lastCheckData = null;

    // enable Check + answer input (same behavior as Question page after a question is loaded)
    if (dom.answer) dom.answer.disabled = false;
    if (dom.btnCheck) dom.btnCheck.disabled = false;

    // (optional) keep Explain/Raw JSON disabled until after checking
    if (dom.btnExplain) dom.btnExplain.disabled = true;
    if (dom.btnToggleJson) dom.btnToggleJson.disabled = true;


    const didSpecial = renderSpecial(q);
    if (!didSpecial) showQuestionText(dom, q.question_text || "");

    renderAnswerOptions(dom, q.meta);

    setProgress(idx, test.length);
    setNav(idx, test.length);
  }

  document.getElementById("btnPrev")?.addEventListener("click", () => {
    if (idx > 0) { idx--; render(); }
  });

  document.getElementById("btnNext")?.addEventListener("click", () => {
    if (idx < test.length - 1) { idx++; render(); }
  });

  render();
}

main();
