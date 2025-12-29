export function lockJsonSection({ dom }) {
  dom.btnToggleJson.disabled = true;
  dom.jsonPanel.classList.add("hidden");
  dom.jsonPanel.open = false;
}

export function unlockJsonSection({ dom }) {
  dom.btnToggleJson.disabled = false;
  dom.jsonPanel.classList.remove("hidden");
}

export function initJsonSection({ dom, state }) {
  lockJsonSection({ dom });

  dom.btnToggleJson.addEventListener("click", () => {
    if (!state.hasChecked) return;
    dom.jsonPanel.open = !dom.jsonPanel.open;
  });
}
