import { setHidden } from "../../ui.js";

function ensureAnswerOptionsUI(dom) {
  if (dom.answerOptionsWrap && dom.answerOptions) return;

  const parent = dom.questionText?.parentElement;
  if (!parent) return;

  const wrap = document.createElement("div");
  wrap.id = "answerOptionsWrap";
  wrap.className = "hidden";

  const divider = document.createElement("div");
  divider.className = "divider";

  const title = document.createElement("h2");
  title.className = "sectionTitle";
  title.textContent = "Answer options";

  const chips = document.createElement("div");
  chips.id = "answerOptions";
  chips.className = "chips";

  wrap.appendChild(divider);
  wrap.appendChild(title);
  wrap.appendChild(chips);

  parent.insertBefore(wrap, dom.questionText.nextSibling);

  dom.answerOptionsWrap = wrap;
  dom.answerOptions = chips;
}

export function renderAnswerOptions(dom, meta) {
  ensureAnswerOptionsUI(dom);

  if (!dom.answerOptionsWrap || !dom.answerOptions) return;

  dom.answerOptions.innerHTML = "";
  setHidden(dom.answerOptionsWrap, true);

  const labels = meta?.answer_options;
  let keys = meta?.answer_option_keys;

  if (!Array.isArray(labels) || labels.length === 0) return;

  if (!Array.isArray(keys) || keys.length !== labels.length) {
    keys = labels;
  }

  setHidden(dom.answerOptionsWrap, false);

  labels.forEach((label, i) => {
    const key = keys[i];
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip";
    btn.textContent = `${i + 1}. ${label}`;
    btn.title = String(key ?? "");

    btn.addEventListener("click", () => {
      if (!dom.answer) return;
      dom.answer.value = String(key ?? "");
      dom.answer.focus();
    });

    dom.answerOptions.appendChild(btn);
  });
}