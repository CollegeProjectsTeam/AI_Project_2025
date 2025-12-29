import { postQuestion } from "../../api.js";
import { collectOptions } from "../../options.js";
import { formatJson } from "../../ui.js";
import { setLoading, showError, clearError, clearResult } from "./view.js";
import { renderAnswerOptions } from "./answer_options.js";
import { lockJsonSection } from "./json_section.js";
import { lockExplainSection } from "./explain_section.js";

export function initGenerateSection({ dom, state, catalogApi }) {
  async function onGenerate() {
    clearError(dom);
    clearResult(dom);

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
        state.currentQuestionId = null;

        if (dom.btnCheck) dom.btnCheck.disabled = true;
        if (dom.answer) dom.answer.disabled = true;

        lockExplainSection({ dom });
        lockJsonSection({ dom });

        if (dom.answerOptionsWrap) dom.answerOptionsWrap.classList.add("hidden");
        return;
      }

      const q = res.data?.question;
      state.currentQuestionId = q?.question_id || null;

      state.hasChecked = false;
      state.lastCheckData = null;

      if (dom.questionText) dom.questionText.textContent = q?.question_text || "";

      if (dom.answer) {
        dom.answer.disabled = !state.currentQuestionId;
        dom.answer.value = "";
      }
      if (dom.btnCheck) dom.btnCheck.disabled = !state.currentQuestionId;

      lockExplainSection({ dom });
      lockJsonSection({ dom });

      renderAnswerOptions(dom, q?.meta || {});
    } catch (e) {
      console.error("Generate crashed:", e);
      showError(dom, "Request failed");
    } finally {
      setLoading(dom, false);
    }
  }

  dom.btnGenerate?.addEventListener("click", onGenerate);

  return { onGenerate };
}