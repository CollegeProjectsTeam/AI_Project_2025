export async function getCatalog() {
  const r = await fetch("/api/catalog");
  return await r.json();
}

export async function postQuestion(payload) {
  const r = await fetch("/api/question", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await r.json();
  return { ok: r.ok, status: r.status, data };
}

export async function postCheck(payload) {
  const r = await fetch("/api/question/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await r.json();
  return { ok: r.ok, status: r.status, data };
}
