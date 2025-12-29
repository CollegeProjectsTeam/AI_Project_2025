from __future__ import annotations

from typing import Any, Dict

from Backend.services import Logger
from Backend.services.evaluators.nash_utils_eval import parse_floats, norm_prob_vec, vec_close

log = Logger("Eval.NashMixed")


def evaluate_nash_mixed(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    meta = item.meta or {}
    payoffs = meta.get("payoffs")
    mixed = meta.get("mixed_equilibrium") or {}
    p_corr = mixed.get("p")
    q_corr = mixed.get("q")

    if payoffs is None or not isinstance(p_corr, list) or not isinstance(q_corr, list):
        log.info("NashMixed missing meta (payoffs/mixed_equilibrium)")
        return {"ok": False, "error": "missing nash_mixed meta"}

    m = len(p_corr)
    n = len(q_corr)

    ans_str = "" if answer is None else str(answer)
    s = ans_str.strip().lower()

    log.info(f"NashMixed evaluate m={m} n={n} reveal={reveal} answer={ans_str!r}")

    if "mixed" in s or "exists" in s:
        log.info("NashMixed user answered presence of mixed only -> correct")
        return {"ok": True, "correct": True, "score": 100.0}

    nums = parse_floats(ans_str)
    p_user = None
    q_user = None

    if m == 2 and n == 2 and len(nums) == 2:
        p = nums[0]
        q = nums[1]
        p_user = norm_prob_vec([p, 1.0 - p])
        q_user = norm_prob_vec([q, 1.0 - q])

    elif len(nums) >= (m + n):
        p_user = norm_prob_vec(nums[:m])
        q_user = norm_prob_vec(nums[m : m + n])

    if p_user is None or q_user is None:
        log.info(f"NashMixed parse failed nums={nums}")
        return {
            "ok": True,
            "correct": False,
            "score": 0.0,
            "error": (
                f"Could not parse mixed strategy. Provide {m+n} numbers (p then q) "
                f"or (for 2x2) 2 numbers."
            ),
        }

    tol = 0.05
    ok = vec_close(p_user, p_corr, tol) and vec_close(q_user, q_corr, tol)

    log.info(f"NashMixed parsed p_user={p_user} q_user={q_user} -> ok={ok} tol={tol}")

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