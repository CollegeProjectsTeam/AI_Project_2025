export function renderCatalogRadio(root, chapters) {
  root.classList.remove("skeleton");
  root.innerHTML = "";

  for (const ch of chapters) {
    const details = document.createElement("details");
    details.className = "chapter";
    details.open = true;

    const summary = document.createElement("summary");
    summary.className = "chapterSummary";

    const left = document.createElement("div");
    left.className = "chapterLeft";
    left.innerHTML = `
      <div class="chapterTitle">${ch.chapter_number}. ${ch.chapter_name}</div>
      <div class="chapterMeta">${(ch.subchapters || []).length} subchapters</div>
    `;

    summary.appendChild(left);
    details.appendChild(summary);

    const list = document.createElement("div");
    list.className = "sublist";

    for (const sc of (ch.subchapters || [])) {
      const id = `ch${ch.chapter_number}_sc${sc.subchapter_number}`;
      const row = document.createElement("label");
      row.className = "subitem";
      row.dataset.text = `${ch.chapter_name} ${sc.subchapter_name}`.toLowerCase();
      row.innerHTML = `
        <input type="radio"
               name="subchapterPick"
               data-chapter="${ch.chapter_number}"
               data-sub="${sc.subchapter_number}"
               id="${id}">
        <span class="subText">${sc.subchapter_number}. ${sc.subchapter_name}</span>
      `;
      list.appendChild(row);
    }

    details.appendChild(list);
    root.appendChild(details);
  }

  root.addEventListener("change", () => {
    syncSelectedStyles(root);
  });

  syncSelectedStyles(root);
}

export function collectSingleSelection(root) {
  const picked = root.querySelector('input[type="radio"][name="subchapterPick"]:checked');
  if (!picked) return null;
  return {
    chapter_number: Number(picked.dataset.chapter),
    subchapter_number: Number(picked.dataset.sub)
  };
}

export function applyFilter(root, text) {
  const q = (text || "").trim().toLowerCase();
  const chapters = root.querySelectorAll(".chapter");
  for (const ch of chapters) {
    const items = ch.querySelectorAll(".subitem");
    let anyVisible = false;

    for (const it of items) {
      const ok = !q || (it.dataset.text || "").includes(q);
      it.classList.toggle("hidden", !ok);
      if (ok) anyVisible = true;
    }

    ch.classList.toggle("hidden", !anyVisible);
  }
}

export function expandAll(root, open) {
  const chapters = root.querySelectorAll("details.chapter");
  for (const c of chapters) c.open = !!open;
}

export function clearSelection(root) {
  const picked = root.querySelector('input[type="radio"][name="subchapterPick"]:checked');
  if (picked) picked.checked = false;
  syncSelectedStyles(root);
}

export function getSelectedLabel(selection, chapters) {
  if (!selection) return "No selection";
  for (const ch of (chapters || [])) {
    if (Number(ch.chapter_number) !== Number(selection.chapter_number)) continue;
    for (const sc of (ch.subchapters || [])) {
      if (Number(sc.subchapter_number) !== Number(selection.subchapter_number)) continue;
      return `${ch.chapter_name} · ${sc.subchapter_name}`;
    }
  }
  return `${selection.chapter_number}:${selection.subchapter_number}`;
}

function syncSelectedStyles(root) {
  const items = root.querySelectorAll(".subitem");
  for (const it of items) {
    const cb = it.querySelector('input[type="radio"]');
    const on = cb && cb.checked;
    it.classList.toggle("selected", !!on);
  }
}
