from __future__ import annotations

import re
from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.nash_utils import parse_nash_answer, evaluate_nash_answer, format_eq_list
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import (
    AlgorithmComparator,
    string_name,
)


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


def _parse_floats(s: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", s or "")]


def _norm_prob_vec(v: list[float]) -> list[float] | None:
    if not v:
        return None
    s = sum(v)
    if s <= 0:
        return None
    return [x / s for x in v]


def _vec_close(a: list[float] | None, b: list[float] | None, tol: float) -> bool:
    if a is None or b is None or len(a) != len(b):
        return False
    return all(abs(a[i] - b[i]) <= tol for i in range(len(a)))


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
        if corr not in ("none", ""):
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

    if qtype == "nash_mixed":
        payoffs = meta.get("payoffs")
        mixed = meta.get("mixed_equilibrium") or {}
        p_corr = mixed.get("p")
        q_corr = mixed.get("q")

        if payoffs is None or not isinstance(p_corr, list) or not isinstance(q_corr, list):
            return {"ok": False, "error": "missing nash_mixed meta"}

        m = len(p_corr)
        n = len(q_corr)

        ans_str = "" if answer is None else str(answer)
        s = ans_str.strip().lower()

        if "mixed" in s or "exists" in s:
            return {"ok": True, "correct": True, "score": 100.0}

        nums = _parse_floats(ans_str)

        p_user = None
        q_user = None

        if m == 2 and n == 2 and len(nums) == 2:
            p = nums[0]
            q = nums[1]
            p_user = _norm_prob_vec([p, 1.0 - p])
            q_user = _norm_prob_vec([q, 1.0 - q])

        elif len(nums) >= (m + n):
            p_user = _norm_prob_vec(nums[:m])
            q_user = _norm_prob_vec(nums[m : m + n])

        if p_user is None or q_user is None:
            return {
                "ok": True,
                "correct": False,
                "score": 0.0,
                "error": f"Could not parse mixed strategy. Provide {m+n} numbers (p then q) or (for 2x2) 2 numbers.",
            }

        tol = 0.05
        ok = _vec_close(p_user, p_corr, tol) and _vec_close(q_user, q_corr, tol)

        resp = {
            "ok": True,
            "correct": ok,
            "score": 100.0 if ok else 0.0,
            "p_user": p_user,
            "q_user": q_user,
        }
        if reveal:
            resp["p_correct"] = p_corr
            resp["q_correct"] = q_corr
        return resp

    if qtype == "nash_combined":
        payoffs = meta.get("payoffs")
        pure_corr = meta.get("pure_equilibria") or []
        mixed = meta.get("mixed_equilibrium")  # poate fi None

        if payoffs is None:
            return {"ok": False, "error": "missing nash_combined meta"}

        m = len(payoffs)
        n = len(payoffs[0]) if m else 0

        ans_str = "" if answer is None else str(answer)
        user_pairs, user_said_none = parse_nash_answer(ans_str, m, n, payoffs)

        score_pure, hits, missing, wrong = evaluate_nash_answer(
            pure_corr, user_pairs, user_said_none
        )

        s = ans_str.strip().lower()
        user_says_mixed = ("mixed" in s) or ("exists" in s)
        correct_has_mixed = mixed is not None
        mixed_ok = (user_says_mixed == correct_has_mixed)

        score = round(0.5 * float(score_pure) + (50.0 if mixed_ok else 0.0), 2)
        correct = (score >= 99.99)

        resp = {
            "ok": True,
            "correct": correct,
            "score": score,
            "hits": format_eq_list(hits),
            "missing": format_eq_list(missing),
            "wrong": format_eq_list(wrong),
            "mixed_ok": mixed_ok,
            "mixed_expected": correct_has_mixed,
        }
        if reveal:
            resp["correct_answer"] = item.correct_answer
        return resp

    return {"ok": False, "error": "unsupported question type"}
