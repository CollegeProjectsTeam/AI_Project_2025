import { postQuestion } from "../../api.js";
import { collectOptions } from "../../options.js";
import { formatJson } from "../../ui.js";
import { setLoading, showError, clearError, clearResult } from "./view.js";
import { renderAnswerOptions } from "./answer_options.js";
import { lockJsonSection } from "./json_section.js";
import { lockExplainSection } from "./explain_section.js";
import { renderGameTree } from "./tree_view.js";
import { renderCspQuestion } from "./csp_render.js";

export function initGenerateSection({ dom, state, catalogApi }) {
  function clearTree() {
    if (!dom.treePanel) return;
    dom.treePanel.innerHTML = "";
    dom.treePanel.classList.add("hidden");
  }

  function isCsp(q) {
    const t = String(q?.meta?.type || "").toLowerCase();
    if (t === "csp_backtracking" || t === "csp") return true;
    return Number(q?.chapter_number) === 3 && Number(q?.subchapter_number) === 1;
  }

  function renderQuestion(dom, q) {
    const renderRoot = dom.questionRender;
    const textRoot = dom.questionText;

    if (!renderRoot || !textRoot) return;

    if (isCsp(q)) {
      textRoot.classList.add("hidden");
      renderRoot.classList.remove("hidden");
      renderCspQuestion(renderRoot, q);
      return;
    }

    renderRoot.classList.add("hidden");
    textRoot.classList.remove("hidden");
    textRoot.textContent = q?.question_text || "";
  }

  async function onGenerate() {
    clearError(dom);
    clearResult(dom);
    clearTree();

    const sel = catalogApi.getSelection();
    if (!sel) {
      showError(dom, "Please select exactly one subchapter.");
      return;
    }

    const options = collectOptions(sel);

    setLoading(dom, true);
    try {
      const res = await postQuestion({
        chapter_number: sel.chapter_number,
        subchapter_number: sel.subchapter_number,
        options,
      });

      if (dom.out) dom.out.textContent = formatJson(res.data);

      if (!res.ok) {
        showError(dom, res.data?.error || `Request failed (${res.status})`);

        if (dom.questionText) dom.questionText.textContent = "";
        if (dom.questionRender) dom.questionRender.innerHTML = "";
        dom.questionRender?.classList.add("hidden");
        dom.questionText?.classList.remove("hidden");

        state.currentQuestionId = null;

        if (dom.btnCheck) dom.btnCheck.disabled = true;
        if (dom.answer) dom.answer.disabled = true;

        lockExplainSection({ dom });
        lockJsonSection({ dom });

        if (dom.answerOptionsWrap) dom.answerOptionsWrap.classList.add("hidden");
        clearTree();
        return;
      }

      const q = res.data?.question;
      state.currentQuestionId = q?.question_id || null;

      state.hasChecked = false;
      state.lastCheckData = null;

      renderQuestion(dom, q);

      if (dom.answer) {
        dom.answer.disabled = !state.currentQuestionId;
        dom.answer.value = "";
      }
      if (dom.btnCheck) dom.btnCheck.disabled = !state.currentQuestionId;

      lockExplainSection({ dom });
      lockJsonSection({ dom });

      const meta = q?.meta || {};
      renderAnswerOptions(dom, meta);

      const t = String(meta.type || "").toLowerCase();
      if ((t.includes("minmax") || t.includes("minimax") || t.includes("alpha")) && meta.tree) {
        renderGameTree(dom.treePanel, meta.tree, meta.root_player);
      } else {
        clearTree();
      }
    } catch (e) {
      console.error("Generate crashed:", e);
      showError(dom, "Request failed");
      clearTree();
    } finally {
      setLoading(dom, false);
    }
  }

  dom.btnGenerate?.addEventListener("click", onGenerate);

  return { onGenerate };
}