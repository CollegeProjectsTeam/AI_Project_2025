import { formatJson } from "../../ui.js";

function extractJsonBlock(text) {
  if (!text) return null;

  const start = text.indexOf("{");
  if (start < 0) return null;

  let depth = 0;
  let inString = false;
  let escape = false;

  for (let i = start; i < text.length; i++) {
    const ch = text[i];

    if (inString) {
      if (escape) {
        escape = false;
      } else if (ch === "\\") {
        escape = true;
      } else if (ch === '"') {
        inString = false;
      }
      continue;
    } else if (ch === '"') {
      inString = true;
      continue;
    }

    if (ch === "{") depth++;
    if (ch === "}") {
      depth--;
      if (depth === 0) {
        return text.slice(start, i + 1);
      }
    }
  }

  return null;
}

function stripInstanceFromQuestionText(questionText, jsonBlock) {
  const cleaned = (questionText || "")
    .replace(jsonBlock || "", "")
    .replace(/\s+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return cleaned
    .replace("cu instanta", "pe instanta de mai jos")
    .replace("cu instanta", "pe instanta de mai jos");
}

function el(tag, cls, text) {
  const x = document.createElement(tag);
  if (cls) x.className = cls;
  if (text != null) x.textContent = text;
  return x;
}

function renderHeader(container, title, subtitle, metaText) {
  const head = el("div", "ssHead");
  const left = el("div", "ssHeadLeft");
  left.appendChild(el("div", "ssTitle", title));
  if (subtitle) left.appendChild(el("div", "ssSubtitle", subtitle));

  head.appendChild(left);

  if (metaText) {
    head.appendChild(el("div", "ssMeta", metaText));
  }

  container.appendChild(head);
}

function renderNQueensBody(container, inst) {
  const n = inst.board_size || (inst.board?.length ?? 0);
  const qn = inst.queen_number_on_board ?? "?";

  const wrap = el("div", "ssBody");
  const board = el("div", "ssBoard");
  board.style.setProperty("--n", n);

  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const dark = (r + c) % 2 === 1;
      const cell = el("div", `ssCell ${dark ? "dark" : "light"}`);
      const v = inst.board?.[r]?.[c] ?? 0;
      if (v === 1) {
        const q = el("span", "ssQueen", "♛");
        cell.appendChild(q);
      }
      board.appendChild(cell);
    }
  }

  wrap.appendChild(board);
  container.appendChild(wrap);

  return `size=${n} • queens_on_board=${qn}`;
}

function renderKnightsTourBody(container, inst) {
  const n = inst.board_size || 8;
  const start = inst.start || [0, 0];
  const [sr, sc] = start;

  const wrap = el("div", "ssBody");
  const board = el("div", "ssBoard");
  board.style.setProperty("--n", n);

  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const dark = (r + c) % 2 === 1;
      const isStart = r === sr && c === sc;
      const cell = el("div", `ssCell ${dark ? "dark" : "light"} ${isStart ? "start" : ""}`);
      if (isStart) cell.appendChild(el("span", "ssKnight", "♞"));
      board.appendChild(cell);
    }
  }

  wrap.appendChild(board);
  container.appendChild(wrap);

  return `size=${n} • start=[${sr}, ${sc}]`;
}

function renderGraphColoringBody(container, inst) {
  const n = inst.num_nodes ?? (inst.adj_list?.length ?? 0);
  const k = inst.num_colors ?? "?";
  const adj = inst.adj_list || [];

  const edges = [];
  for (let i = 0; i < adj.length; i++) {
    for (const j of adj[i] || []) {
      if (typeof j === "number" && j > i) edges.push([i, j]);
    }
  }

  const wrap = el("div", "ssBody");

  const info = el("div", "ssInfoRow");
  info.appendChild(el("div", "ssPill", `nodes=${n}`));
  info.appendChild(el("div", "ssPill", `colors=${k}`));
  info.appendChild(el("div", "ssPill", `edges=${edges.length}`));
  wrap.appendChild(info);

  const grid = el("div", "gcGrid");
  for (let i = 0; i < n; i++) {
    const row = el("div", "gcRow");
    row.appendChild(el("div", "gcNode", `N${i}`));
    const neigh = (adj[i] || []).map(x => `N${x}`).join(", ");
    row.appendChild(el("div", "gcAdj", neigh || "—"));
    grid.appendChild(row);
  }
  wrap.appendChild(grid);

  if (edges.length) {
    const edgesBox = el("div", "gcEdges");
    edgesBox.appendChild(el("div", "gcEdgesTitle", "Edges"));
    edgesBox.appendChild(el("div", "gcEdgesText", edges.map(([a, b]) => `(N${a}, N${b})`).join(", ")));
    wrap.appendChild(edgesBox);
  }

  container.appendChild(wrap);

  return `nodes=${n} • colors=${k} • edges=${edges.length}`;
}

function renderHanoiBody(container, inst) {
  const disks = inst.disks ?? "?";
  const pegs = inst.pegs ?? (inst.start_state?.length ?? "?");
  const startPeg = inst.start_peg ?? "?";
  const goalPeg = inst.goal_peg ?? "?";
  const state = inst.start_state || [];

  const wrap = el("div", "ssBody");

  const info = el("div", "ssInfoRow");
  info.appendChild(el("div", "ssPill", `disks=${disks}`));
  info.appendChild(el("div", "ssPill", `pegs=${pegs}`));
  info.appendChild(el("div", "ssPill", `start_peg=${startPeg}`));
  info.appendChild(el("div", "ssPill", `goal_peg=${goalPeg}`));
  wrap.appendChild(info);

  const pegsWrap = el("div", "hanoiPegs");

  const maxDisk = Math.max(
    1,
    ...state.flat().map(x => (typeof x === "number" ? x : 1))
  );

  for (let p = 0; p < state.length; p++) {
    const peg = el("div", `hanoiPeg ${p === goalPeg ? "goal" : ""}`);
    peg.appendChild(el("div", "hanoiPegTitle", `Peg ${p}`));

    const stack = el("div", "hanoiStack");
    const discs = (state[p] || []).slice();
    for (const d of discs) {
      const disc = el("div", "hanoiDisc", String(d));
      const w = 20 + Math.round((Number(d) / maxDisk) * 90);
      disc.style.width = `${w}px`;
      stack.appendChild(disc);
    }

    peg.appendChild(stack);
    pegsWrap.appendChild(peg);
  }

  wrap.appendChild(pegsWrap);
  container.appendChild(wrap);

  return `disks=${disks} • pegs=${pegs} • goal_peg=${goalPeg}`;
}

export function tryRenderSearchStrategies(dom, question) {
  const q = question || {};
  const meta = q.meta || {};
  if (meta.group !== "search_strategies") return false;

  const rawText = q.question_text || "";
  const jsonBlock = extractJsonBlock(rawText);
  if (!jsonBlock) return false;

  let inst;
  try {
    inst = JSON.parse(jsonBlock);
  } catch {
    return false;
  }

  const prompt = stripInstanceFromQuestionText(rawText, jsonBlock);

  dom.questionRender.classList.remove("hidden");
  dom.questionText.classList.add("hidden");

  const card = el("div", "ssCard");

  const title = inst.problem_name || meta.problem || meta.type || "Search problem";
  const subtitle = prompt || "Alege strategia potrivita predata la curs.";

  let metaLine = "";
  if (meta.problem === "nqueens") metaLine = renderNQueensBody(card, inst);
  else if (meta.problem === "knights_tour") metaLine = renderKnightsTourBody(card, inst);
  else if (meta.problem === "graph_coloring") metaLine = renderGraphColoringBody(card, inst);
  else if (meta.problem === "generalized_hanoi") metaLine = renderHanoiBody(card, inst);
  else {
    const wrap = el("div", "ssBody");
    const pre = el("pre", "ssRawPre");
    pre.textContent = formatJson(inst);
    wrap.appendChild(pre);
    card.appendChild(wrap);
    metaLine = meta.problem || meta.type || "";
  }

  card.insertBefore(el("div"), card.firstChild);
  card.removeChild(card.firstChild);
  renderHeader(card, title, subtitle, metaLine);

  dom.questionRender.innerHTML = "";
  dom.questionRender.appendChild(card);

  return true;
}