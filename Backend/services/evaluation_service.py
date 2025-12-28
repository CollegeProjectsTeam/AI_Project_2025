from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.nash_utils import parse_nash_answer, evaluate_nash_answer, format_eq_list

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
        user = (str(answer or "")).strip().lower()
        correct = (item.correct_answer or "").strip().lower()
        score = 100.0 if user == correct else 0.0
        resp = {"ok": True, "correct": (score == 100.0), "score": score}
        if reveal:
            resp["correct_answer"] = item.correct_answer
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
            "wrong": format_eq_list(wrong)
        }
        if reveal:
            resp["correct_answer"] = item.correct_answer
        return resp

    return {"ok": False, "error": "unsupported question type"}
