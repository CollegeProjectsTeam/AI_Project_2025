import { postGenerateTest } from "../api.js";

// DOM
const form = document.getElementById("generate-test-form");
const subchapterContainer = document.getElementById("subchapter-container");

async function loadSubchapters() {
  const r = await fetch("/api/subchapters");
  const data = await r.json();

  if (!r.ok || data?.ok !== true) {
    console.error("subchapters failed", { status: r.status, data });
    alert(data?.error || `Failed to load subchapters (${r.status})`);
    return;
  }

  subchapterContainer.innerHTML = "";

  for (const sc of data.subchapters || []) {
    const value = `${sc.chapter_number}:${sc.subchapter_number}`;

    const label = document.createElement("label");
    label.className = "checkbox-label";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "subchapters";
    checkbox.value = value;

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(` ${sc.name}`));

    subchapterContainer.appendChild(label);
  }
}

async function onSubmit(e) {
  e.preventDefault();

  const fd = new FormData(form);

  const payload = {
    num_questions: fd.get("num_questions"),        // string ok (la tine e "5")
    difficulty: fd.get("difficulty"),              // "easy|medium|hard"
    subchapters: fd.getAll("subchapters"),         // ["1:1","2:1",...]
  };

  const res = await postGenerateTest(payload);

  // redirect + store
  if (res.ok && res.data?.ok === true) {
    sessionStorage.setItem("smar_last_test", JSON.stringify(res.data));
    window.location.href = "/question_test";
    return;
  }

  console.error("generate-test failed", res);
  alert(res.data?.error || `Failed to generate test (${res.status})`);
}

document.addEventListener("DOMContentLoaded", loadSubchapters);
form?.addEventListener("submit", onSubmit);
