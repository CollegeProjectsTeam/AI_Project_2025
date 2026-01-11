import { renderSearchStrategiesOptions,collectSearchStrategiesOptions } from "./options/search_strategies_options.js";
import { renderNashOptions, collectNashOptions } from "./options/nash_options.js";
import { renderMinMaxOptions, collectMinMaxOptions } from "./options/minmax_options.js";
import { renderCspOptions, collectCspOptions } from "./options/csp_options.js";

export function renderOptions(root, selection) {
  root.innerHTML = "";

  if (!selection) {
    root.innerHTML = `<div class="mutedSmall">Select a subchapter to see its options.</div>`;
    return;
  }

  const ch = selection.chapter_number;
  const sc = selection.subchapter_number;

    // Chapter 1
    if (ch === 1 && sc === 1) {
      renderSearchStrategiesOptions(root);
      return;
    }

  // Chapter 2
  if (ch === 2 && sc === 1) {
    renderNashOptions(root);
    return;
  }

  if (ch === 2 && sc === 2) {
    renderMinMaxOptions(root);
    return;
  }

  // Chapter 3
  if (ch === 3 && sc === 1) {
    renderCspOptions(root);
    return;
  }

  root.innerHTML = `<div class="mutedSmall">No options available for this subchapter yet.</div>`;
}

export function collectOptions(selection) {
  if (!selection) return {};

  const ch = selection.chapter_number;
  const sc = selection.subchapter_number;

  // Chapter 1
  if (ch === 1 && sc === 1) return collectSearchStrategiesOptions();

  // Chapter 2
  if (ch === 2 && sc === 1) return collectNashOptions();
  if (ch === 2 && sc === 2) return collectMinMaxOptions();

  // Chapter 3
  if (ch === 3 && sc === 1) return collectCspOptions();

  return {};
}