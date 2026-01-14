import { formatJson } from "../ui.js";

import { dom } from "./question_test/dom.js";
import { state } from "./question/state.js"; // reuse same state object shape
import { initCheckSection } from "./question/check_section.js";

import {
  initExplainSection,
  lockExplainSection,
  unlockExplainSection,
  renderExplanation
} from "./question/explain_section.js";

import {
  initJsonSection,
  lockJsonSection,
  unlockJsonSection
} from "./question/json_section.js";

import { resetQuestionUI, showQuestionText, showError, clearError } from "./question/view.js";
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

function setCheckResultFromData(data) {
  if (!dom.checkResult) return;

  const ok = data?.correct === true;
  const score = typeof data?.score === "number" ? ` (score: ${data.score}%)` : "";

  dom.checkResult.classList.remove("hidden", "ok", "bad");

  if (ok) {
    dom.checkResult.textContent = `Correct${score}`;
    dom.checkResult.classList.add("ok");
    return;
  }

  if (data?.correct === false) {
    const correctText =
      (typeof data.correct_answer_text === "string" && data.correct_answer_text.trim())
        ? data.correct_answer_text.trim()
        : (data.correct_answer != null ? JSON.stringify(data.correct_answer) : "");

    const correct = correctText ? ` Correct answer: ${correctText}` : "";
    dom.checkResult.textContent = `Incorrect${score}.${correct}`;
    dom.checkResult.classList.add("bad");
    return;
  }

  dom.checkResult.textContent = data?.error || "Check not implemented for this question type yet.";
  dom.checkResult.classList.add("bad");
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

  // ✅ cache per întrebare
  const byQid = {}; // { [qid]: { answer: string, hasChecked: boolean, lastCheckData: any } }

  function qKey(i) {
    return test[i]?.question_id || `idx_${i}`;
  }

  function persistCurrent() {
    const key = qKey(idx);
    byQid[key] = byQid[key] || { answer: "", hasChecked: false, lastCheckData: null };
    byQid[key].answer = dom.answer?.value || "";
    byQid[key].hasChecked = !!state.hasChecked;
    byQid[key].lastCheckData = state.lastCheckData || null;
  }

  function render() {
    clearError(dom);
    resetQuestionUI(dom);

    const q = test[idx];
    if (!q?.question_id) {
      showError(dom, "Question is missing question_id (cannot check).");
      return;
    }

    const key = qKey(idx);
    const saved = byQid[key] || { answer: "", hasChecked: false, lastCheckData: null };
    byQid[key] = saved;

    // bind state pt check_section
    state.currentQuestionId = q.question_id;
    state.hasChecked = !!saved.hasChecked;
    state.lastCheckData = saved.lastCheckData;

    // restore answer
    if (dom.answer) dom.answer.value = saved.answer || "";

    // render question
    const didSpecial = renderSpecial(q);
    if (!didSpecial) showQuestionText(dom, q.question_text || "");

    renderAnswerOptions(dom, q.meta);

    // ✅ dacă NU e checked: ascunde + golește explain/json
    if (!state.hasChecked) {
      lockExplainSection({ dom });
      lockJsonSection({ dom });
      if (dom.explainOut) dom.explainOut.textContent = "";
      if (dom.out) dom.out.textContent = "";
      if (dom.checkResult) dom.checkResult.classList.add("hidden");

      if (dom.answer) dom.answer.disabled = false;
      if (dom.btnCheck) dom.btnCheck.disabled = !state.currentQuestionId;
    } else {
      // ✅ dacă e checked: reaplică explain/json + blochează input-ul
      unlockExplainSection({ dom });
      unlockJsonSection({ dom });

      if (state.lastCheckData) {
        renderExplanation({ dom, data: state.lastCheckData });
        if (dom.out) dom.out.textContent = formatJson(state.lastCheckData);
        setCheckResultFromData(state.lastCheckData);
      }

      if (dom.answer) dom.answer.disabled = true;
      if (dom.btnCheck) dom.btnCheck.disabled = true;
    }

    setProgress(idx, test.length);
    setNav(idx, test.length);
  }

  // ✅ păstrează ce tastezi per întrebare
  dom.answer?.addEventListener("input", () => {
    const key = qKey(idx);
    byQid[key] = byQid[key] || { answer: "", hasChecked: false, lastCheckData: null };
    byQid[key].answer = dom.answer.value || "";

    // enable check doar dacă e întrebare validă și nu e checked
    if (dom.btnCheck) dom.btnCheck.disabled = !state.currentQuestionId || state.hasChecked;
  });

  document.getElementById("btnPrev")?.addEventListener("click", () => {
    persistCurrent();
    if (idx > 0) { idx--; render(); }
  });

  document.getElementById("btnNext")?.addEventListener("click", () => {
    persistCurrent();
    if (idx < test.length - 1) { idx++; render(); }
  });

  render();
}

main();
