from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.nash_utils import parse_nash_answer, evaluate_nash_answer, format_eq_list
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import AlgorithmComparator, string_name


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _nq_user_to_key(ans: Any) -> str | None:
    raw = "" if ans is None else str(ans).strip()
    if not raw:
        return None

    keys = getattr(AlgorithmComparator, "ALGORITHM_ORDER", [])

    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(keys):
            return keys[idx]
        return None

    user = _norm(raw)
    if user in keys:
        return user

    label_map = {string_name(k).strip().lower(): k for k in keys}
    return label_map.get(user)


def evaluate_answer(payload: Dict[str, Any]) -> Dict[str, Any]:
    qid = (payload.get("question_id") or "").strip()
    answer = payload.get("answer")
    reveal = bool(payload.get("reveal") or False)

    if not qid:
        return {"ok": False, "error": "question_id is required"}

    item = store.get(qid)
    if item is None:
        return {"ok": False, "error": "unknown question_id"}

    meta = item.meta or {}
    qtype = meta.get("type")

    if qtype == "nqueens":
        correct_key = _norm(str(item.correct_answer or ""))
        user_key = _nq_user_to_key(answer)
        score = 100.0 if (user_key is not None and user_key == correct_key) else 0.0
        resp = {"ok": True, "correct": (score == 100.0), "score": score}
        if reveal:
            resp["correct_answer"] = string_name(correct_key)
        return resp

    if qtype == "nash_pure":
        m = int(meta.get("m") or 0)
        n = int(meta.get("n") or 0)
        payoffs = meta.get("payoffs")

        if not m or not n or payoffs is None:
            return {"ok": False, "error": "missing nash meta"}

        correct_eqs = []
        corr = (item.correct_answer or "").strip().lower()
        if corr != "none" and corr != "":
            parts = corr.replace(" ", "").split("),")
            for p in parts:
                p = p.replace("(", "").replace(")", "").strip()
                if not p:
                    continue
                a, b = p.split(",")
                correct_eqs.append((int(a) - 1, int(b) - 1))

        ans_str = "" if answer is None else str(answer)
        user_pairs, user_said_none = parse_nash_answer(ans_str, m, n, payoffs)
        score, hits, missing, wrong = evaluate_nash_answer(correct_eqs, user_pairs, user_said_none)

        resp = {
            "ok": True,
            "correct": (float(score) == 100.0),
            "score": score,
            "hits": format_eq_list(hits),
            "missing": format_eq_list(missing),
            "wrong": format_eq_list(wrong),
        }
        if reveal:
            resp["correct_answer"] = item.correct_answer
        return resp

    return {"ok": False, "error": "unsupported question type"}
