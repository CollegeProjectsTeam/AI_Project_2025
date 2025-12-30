export function setHidden(el, hidden) {
  el.classList.toggle("hidden", !!hidden);
}

export function setError(el, msg) {
  if (!msg) {
    el.textContent = "";
    setHidden(el, true);
    return;
  }
  el.textContent = msg;
  setHidden(el, false);
}

export function formatJson(data) {
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
}

export function debounce(fn, ms) {
  let t = null;
  return (...args) => {
    if (t) clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}
