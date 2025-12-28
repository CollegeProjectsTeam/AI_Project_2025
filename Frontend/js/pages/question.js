import { getCatalog, postQuestion, postCheck } from "../api.js";
import { renderCatalogRadio, collectSingleSelection, applyFilter, expandAll, clearSelection, getSelectedLabel } from "../catalog_radio.js";
import { renderOptions, collectOptions } from "../options.js";
import { setError, setHidden, formatJson, debounce } from "../ui.js";

const elCatalog = document.getElementById("catalog");
const elErr = document.getElementById("err");
const elSearch = document.getElementById("search");
const elExpandAll = document.getElementById("btnExpandAll");
const elClear = document.getElementById("btnClear");
const elChip = document.getElementById("selChip");
const elOptions = document.getElementById("options");

const elBtnGenerate = document.getElementById("btnGenerate");
const elQuestionText = document.getElementById("questionText");
const elJsonOut = document.getElementById("out");
const elJsonPanel = document.getElementById("jsonPanel");
const elToggleJson = document.getElementById("btnToggleJson");

const elAnswer = document.getElementById("answer");
const elBtnCheck = document.getElementById("btnCheck");
const elCheckResult = document.getElementById("checkResult");

let catalog = { chapters: [] };
let expanded = true;
let currentQuestionId = null;

async function init() {
  try {
    catalog = await getCatalog();
    renderCatalogRadio(elCatalog, catalog.chapters || []);
    syncUI();
  } catch {
    setError(elErr, "Failed to load catalog");
  }
}

function syncUI() {
  const sel = collectSingleSelection(elCatalog);
  elChip.innerHTML = `<span class="chip">${getSelectedLabel(sel, catalog.chapters || [])}</span>`;
  renderOptions(elOptions, sel);
  elBtnGenerate.disabled = !sel;
  setError(elErr, "");
}

function setLoading(on) {
  elBtnGenerate.classList.toggle("loading", !!on);
  elBtnGenerate.disabled = !!on;
}

function setResult(msg, ok) {
  if (!msg) {
    elCheckResult.textContent = "";
    setHidden(elCheckResult, true);
    return;
  }
  elCheckResult.textContent = msg;
  elCheckResult.classList.toggle("ok", !!ok);
  elCheckResult.classList.toggle("bad", !ok);
  setHidden(elCheckResult, false);
}

async function onGenerate() {
  setError(elErr, "");
  setResult("", true);

  const sel = collectSingleSelection(elCatalog);
  if (!sel) {
    setError(elErr, "Please select exactly one subchapter.");
    return;
  }

  const options = collectOptions(sel);

  setLoading(true);

  try {
    const res = await postQuestion({
      chapter_number: sel.chapter_number,
      subchapter_number: sel.subchapter_number,
      options
    });

    elJsonOut.textContent = formatJson(res.data);

    if (!res.ok) {
      setError(elErr, res.data?.error || `Request failed (${res.status})`);
      elQuestionText.textContent = "";
      currentQuestionId = null;
      elBtnCheck.disabled = true;
      return;
    }

    const q = res.data?.question;
    currentQuestionId = q?.question_id || null;
    elQuestionText.textContent = q?.question_text || "";
    elBtnCheck.disabled = !currentQuestionId;
    elAnswer.value = "";
  } catch {
    setError(elErr, "Request failed");
  } finally {
    setLoading(false);
  }
}

async function onCheck() {
  setError(elErr, "");
  setResult("", true);

  if (!currentQuestionId) return;

  const ans = (elAnswer.value || "").trim();
  if (!ans) {
    setResult("Type an answer first.", false);
    return;
  }

  try {
    const res = await postCheck({
      question_id: currentQuestionId,
      answer: ans
    });

    elJsonOut.textContent = formatJson(res.data);

    if (!res.ok) {
      setError(elErr, res.data?.error || `Check failed (${res.status})`);
      return;
    }

    if (res.data.correct === true) {
      const score = typeof res.data.score === "number" ? ` (score: ${res.data.score}%)` : "";
      setResult(`Correct${score}`, true);
      return;
    }

    if (res.data.correct === false) {
      const correct = res.data.correct_answer ? ` Correct answer: ${res.data.correct_answer}` : "";
      const score = typeof res.data.score === "number" ? ` (score: ${res.data.score}%)` : "";
      setResult(`Incorrect${score}.${correct}`, false);
      return;
    }

    setResult(res.data?.error || "Check not implemented for this question type yet.", false);
  } catch {
    setError(elErr, "Check request failed");
  }
}

elCatalog.addEventListener("change", syncUI);

elSearch.addEventListener("input", debounce(() => {
  applyFilter(elCatalog, elSearch.value);
}, 120));

elExpandAll.addEventListener("click", () => {
  expanded = !expanded;
  expandAll(elCatalog, expanded);
  elExpandAll.textContent = expanded ? "Collapse all" : "Expand all";
});

elClear.addEventListener("click", () => {
  clearSelection(elCatalog);
  elSearch.value = "";
  applyFilter(elCatalog, "");
  elQuestionText.textContent = "";
  elJsonOut.textContent = "";
  currentQuestionId = null;
  elBtnCheck.disabled = true;
  elAnswer.value = "";
  setResult("", true);
  syncUI();
});

elBtnGenerate.addEventListener("click", onGenerate);
elBtnCheck.addEventListener("click", onCheck);

elToggleJson.addEventListener("click", () => {
  elJsonPanel.open = !elJsonPanel.open;
});

init();
