import { getCatalog } from "../../api.js";
import {
  renderCatalogRadio,
  collectSingleSelection,
  applyFilter,
  expandAll,
  clearSelection,
  getSelectedLabel,
} from "../../catalog_radio.js";
import { renderOptions } from "../../options.js";
import { debounce } from "../../ui.js";
import { syncSelectionChip, showError, clearError, resetQuestionUI } from "./view.js";

export function initCatalogSection({ dom, state }) {
  async function loadCatalog() {
    try {
      state.catalog = await getCatalog();
      renderCatalogRadio(dom.catalog, state.catalog.chapters || []);
      syncUI();
    } catch {
      showError(dom, "Failed to load catalog");
    }
  }

  function syncUI() {
    const sel = collectSingleSelection(dom.catalog);
    syncSelectionChip(dom, getSelectedLabel(sel, state.catalog.chapters || []));
    renderOptions(dom.options, sel);
    dom.btnGenerate.disabled = !sel;
    clearError(dom);
  }

  // events
  dom.catalog.addEventListener("change", () => {
    syncUI();
  });

  dom.search.addEventListener(
    "input",
    debounce(() => {
      applyFilter(dom.catalog, dom.search.value);
    }, 120)
  );

  dom.btnExpandAll.addEventListener("click", () => {
    state.expanded = !state.expanded;
    expandAll(dom.catalog, state.expanded);
    dom.btnExpandAll.textContent = state.expanded ? "Collapse all" : "Expand all";
  });

  dom.btnClear.addEventListener("click", () => {
    clearSelection(dom.catalog);
    dom.search.value = "";
    applyFilter(dom.catalog, "");

    state.currentQuestionId = null;
    resetQuestionUI(dom);

    dom.out.textContent = "";
    syncUI();
  });

  return {
    loadCatalog,
    getSelection: () => collectSingleSelection(dom.catalog),
    syncUI,
  };
}
