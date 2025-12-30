function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatConstraint(c) {
  if (!c || typeof c !== "object") return String(c);

  const type = String(c.type || "").toLowerCase();
  const vars = Array.isArray(c.vars) ? c.vars : [];
  if (vars.length !== 2) return JSON.stringify(c);

  const a = String(vars[0]);
  const b = String(vars[1]);

  if (type === "gt") return `${a} > ${b}`;
  if (type === "lt") return `${a} < ${b}`;
  if (type === "neq") return `${a} \u2260 ${b}`;

  return JSON.stringify(c);
}

function formatDomains(domains) {
  if (!domains || typeof domains !== "object") return [];
  return Object.entries(domains).map(([v, arr]) => {
    const vals = Array.isArray(arr) ? arr.join(", ") : String(arr);
    return `${v}: {${vals}}`;
  });
}

export function renderCspQuestion(root, question) {
  const meta = question?.meta || {};
  const tv = meta?.template_vars || {};

  const inst = tv?.instance || meta?.instance || {};
  const options = tv?.options || meta?.settings || {};
  const askFor = tv?.ask_for || meta?.settings?.ask_for || "";
  const statement = tv?.statement || "";

  const answerFormat =
    tv?.answer_format ||
    meta?.template_vars?.answer_format ||
    "";

  const vars = Array.isArray(inst.variables) ? inst.variables : [];
  const order = Array.isArray(inst.order) ? inst.order : [];
  const domainsLines = formatDomains(inst.domains);
  const constraints = Array.isArray(inst.constraints) ? inst.constraints : [];
  const constraintsLines = constraints.map(formatConstraint);

  const optLine = [
    options.inference ? `Inference: ${options.inference}` : null,
    options.consistency ? `Consistency: ${options.consistency}` : null,
    options.var_heuristic ? `Var: ${options.var_heuristic}` : null,
    options.value_heuristic ? `Value: ${options.value_heuristic}` : null,
  ].filter(Boolean);

  root.innerHTML = `
    <div class="cspCard">
      <div class="cspTitle">CSP (Backtracking)</div>

      ${
        statement
          ? `
            <div class="cspSection">
              <div class="cspLabel">Cerinta</div>
              <div class="cspText">${escapeHtml(statement)}</div>
            </div>
          `
          : ""
      }

      <div class="cspSection">
        <div class="cspLabel">Optiuni</div>
        <div class="cspChips">
          ${optLine.map(t => `<span class="chip">${escapeHtml(t)}</span>`).join("")}
        </div>
      </div>

      <div class="cspSection">
        <div class="cspLabel">Task</div>
        <div class="cspText">${escapeHtml(askFor || "")}</div>
      </div>

      ${
        answerFormat
          ? `
            <div class="cspSection">
              <div class="cspLabel">Format raspuns</div>
              <div class="cspText cspFormatText">${escapeHtml(answerFormat)}</div>
            </div>
          `
          : ""
      }

      <div class="cspGrid">
        <div class="cspSection">
          <div class="cspLabel">Variabile</div>
          <div class="mono">${escapeHtml(vars.join(", ") || "—")}</div>
        </div>

        <div class="cspSection">
          <div class="cspLabel">Ordine</div>
          <div class="mono">${escapeHtml(order.join(" → ") || "—")}</div>
        </div>
      </div>

      <div class="cspSection">
        <div class="cspLabel">Domenii</div>
        <ul class="cspList">
          ${
            domainsLines.length
              ? domainsLines.map(x => `<li class="mono">${escapeHtml(x)}</li>`).join("")
              : `<li class="muted">—</li>`
          }
        </ul>
      </div>

      <div class="cspSection">
        <div class="cspLabel">Constrangeri</div>
        <ul class="cspList">
          ${
            constraintsLines.length
              ? constraintsLines.map(x => `<li class="mono">${escapeHtml(x)}</li>`).join("")
              : `<li class="muted">—</li>`
          }
        </ul>
      </div>
    </div>
  `;
}