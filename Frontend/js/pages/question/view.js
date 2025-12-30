import { setError, setHidden } from "../../ui.js";

export function syncSelectionChip(dom, label) {
  dom.selChip.innerHTML = `<span class="chip">${label}</span>`;
}

export function setLoading(dom, on) {
  dom.btnGenerate.classList.toggle("loading", !!on);
  dom.btnGenerate.disabled = !!on;
}

export function clearError(dom) {
  setError(dom.err, "");
}

export function showError(dom, msg) {
  setError(dom.err, msg);
}

export function clearResult(dom) {
  dom.checkResult.textContent = "";
  dom.checkResult.classList.remove("ok", "bad");
  setHidden(dom.checkResult, true);
}

export function setResult(dom, msg, ok) {
  if (!msg) {
    clearResult(dom);
    return;
  }

  dom.checkResult.textContent = msg;
  dom.checkResult.classList.toggle("ok", !!ok);
  dom.checkResult.classList.toggle("bad", !ok);
  setHidden(dom.checkResult, false);
}

export function resetQuestionUI(dom) {
  dom.questionText.textContent = "";
  dom.answer.value = "";
  dom.btnCheck.disabled = true;
  clearResult(dom);

  if (dom.answerOptionsWrap) setHidden(dom.answerOptionsWrap, true);
}
