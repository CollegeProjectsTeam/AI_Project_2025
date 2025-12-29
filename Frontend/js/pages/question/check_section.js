import { postCheck } from "../../api.js";
import { formatJson } from "../../ui.js";
import { showError, clearError, setResult } from "./view.js";
import { unlockJsonSection } from "./json_section.js";
import { unlockExplainSection, renderExplanation } from "./explain_section.js";

export function initCheckSection({ dom, state }) {
  function lockAfterCheck() {
    if (dom.answer) dom.answer.disabled = true;
    if (dom.btnCheck) dom.btnCheck.disabled = true;
  }

  function setChecking(on) {
    if (dom.btnCheck) dom.btnCheck.disabled = !!on || !state.currentQuestionId || state.hasChecked;
  }

  async function onCheck() {
    clearError(dom);
    setResult(dom, "", true);

    if (!state.currentQuestionId) return;
    if (state.hasChecked) return;

    const ans = (dom.answer?.value || "").trim();
    if (!ans) {
      setResult(dom, "Type an answer first.", false);
      return;
    }

    setChecking(true);

    try {
      const res = await postCheck({
        question_id: state.currentQuestionId,
        answer: ans,
      });

      if (dom.out) dom.out.textContent = formatJson(res.data);

      if (!res.ok) {
        showError(dom, res.data?.error || `Check failed (${res.status})`);
        return;
      }

      state.hasChecked = true;
      state.lastCheckData = res.data;

      unlockExplainSection({ dom });
      unlockJsonSection({ dom });

      renderExplanation({ dom, data: res.data });

      lockAfterCheck();

      if (res.data.correct === true) {
        const score =
          typeof res.data.score === "number" ? ` (score: ${res.data.score}%)` : "";
        setResult(dom, `Correct${score}`, true);
        return;
      }

      if (res.data.correct === false) {
        const correct = res.data.correct_answer
          ? ` Correct answer: ${res.data.correct_answer}`
          : "";
        const score =
          typeof res.data.score === "number" ? ` (score: ${res.data.score}%)` : "";
        setResult(dom, `Incorrect${score}.${correct}`, false);
        return;
      }

      setResult(
        dom,
        res.data?.error || "Check not implemented for this question type yet.",
        false
      );
    } catch (e) {
      console.error("onCheck crashed:", e);
      showError(dom, e?.message ? `Check crashed: ${e.message}` : "Check request failed");
    } finally {
      if (!state.hasChecked) setChecking(false);
    }
  }

  dom.btnCheck?.addEventListener("click", onCheck);

  return { onCheck, lockAfterCheck };
}
