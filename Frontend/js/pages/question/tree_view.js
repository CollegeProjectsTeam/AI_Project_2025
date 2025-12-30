function isLeaf(node) {
  if (!node || typeof node !== "object") return false;
  const hasValue = typeof node.value === "number";
  const kids = node.children;
  const noKids = !Array.isArray(kids) || kids.length === 0;
  return hasValue && noKids;
}

export function renderGameTree(rootEl, tree, rootPlayer) {
  if (!rootEl) return;

  if (!tree) {
    rootEl.innerHTML = "";
    rootEl.classList.add("hidden");
    return;
  }

  rootEl.classList.remove("hidden");
  rootEl.innerHTML = "";

  const rp = String(rootPlayer || "MAX").toUpperCase();
  const next = (p) => (p === "MAX" ? "MIN" : "MAX");

  function nodeBox(text, kind) {
    const el = document.createElement("div");
    el.className = `tvBox ${kind}`;
    el.textContent = text;
    return el;
  }

  function build(node, player, isChild) {
    const wrap = document.createElement("div");
    wrap.className = "tvSubtree" + (isChild ? " tvChild" : "");

    if (isLeaf(node)) {
      wrap.appendChild(nodeBox(String(node.value), "tvLeaf"));
      return wrap;
    }

    wrap.appendChild(nodeBox(player, player === "MAX" ? "tvMax" : "tvMin"));

    const kids = Array.isArray(node.children) ? node.children : [];
    if (!kids.length) return wrap;

    const down = document.createElement("div");
    down.className = "tvDown";
    wrap.appendChild(down);

    const childrenWrap = document.createElement("div");
    childrenWrap.className = "tvChildrenWrap";

    const h = document.createElement("div");
    h.className = "tvH";
    childrenWrap.appendChild(h);

    const row = document.createElement("div");
    row.className = "tvRow";

    const np = next(player);
    for (const ch of kids) row.appendChild(build(ch, np, true));

    childrenWrap.appendChild(row);
    wrap.appendChild(childrenWrap);

    return wrap;
  }

  const wrap = document.createElement("div");
  wrap.className = "treeWrap";

  const title = document.createElement("div");
  title.className = "treeTitle";
  title.textContent = `MinMax tree (root: ${rp})`;

  wrap.appendChild(title);
  wrap.appendChild(build(tree, rp, false));

  rootEl.appendChild(wrap);
}
