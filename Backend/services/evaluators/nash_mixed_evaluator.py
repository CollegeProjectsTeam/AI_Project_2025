from __future__ import annotations

from typing import Any, Dict, List

from Backend.services import Logger
from Backend.services.evaluators.nash_utils_eval import parse_floats, norm_prob_vec, vec_close

log = Logger("Eval.NashMixed")


def _vec_str(v: List[float] | None) -> str:
    if not v:
        return "none"
    return "[" + ", ".join(f"{x:.3f}" for x in v) + "]"


def _build_lines(*, correct: bool, score: float, p_user, q_user, tol: float, reveal: bool, p_corr, q_corr) -> List[str]:
    lines = [
        f"Correct: {'Yes' if correct else 'No'}",
        f"Score: {score}",
        f"Parsed p: {_vec_str(p_user)}",
        f"Parsed q: {_vec_str(q_user)}",
        f"Tolerance: ±{tol}",
    ]
    if reveal:
        lines.append(f"Expected p: {_vec_str(p_corr)}")
        lines.append(f"Expected q: {_vec_str(q_corr)}")
    else:
        lines.append("Tip: enable reveal to see the expected probabilities.")
    return lines


def evaluate_nash_mixed(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    meta = item.meta or {}
    payoffs = meta.get("payoffs")

    mixed = meta.get("mixed_equilibrium") or {}

    p_corr = mixed.get("p") or mixed.get("p1")
    q_corr = mixed.get("q") or mixed.get("p2")

    if payoffs is None or not isinstance(p_corr, list) or not isinstance(q_corr, list):
        log.info("NashMixed missing meta (payoffs/mixed_equilibrium)")
        return {"ok": False, "error": "missing nash_mixed meta"}

    m = len(p_corr)
    n = len(q_corr)

    ans_str = "" if answer is None else str(answer)
    s = ans_str.strip().lower()

    log.info(f"NashMixed evaluate m={m} n={n} reveal={reveal} answer={ans_str!r}")

    if "mixed" in s or "exists" in s:
        return {
            "ok": True,
            "correct": True,
            "score": 100.0,
            "explanation_lines": ["Correct: Yes", "Score: 100", "User indicated mixed equilibrium exists."],
        }

    nums = parse_floats(ans_str)
    p_user = None
    q_user = None

    if m == 2 and n == 2 and len(nums) == 2:
        p = nums[0]
        q = nums[1]

        # validate typical 2x2 input in [0,1]
        if 0.0 <= p <= 1.0 and 0.0 <= q <= 1.0:
            p_user = norm_prob_vec([p, 1.0 - p])
            q_user = norm_prob_vec([q, 1.0 - q])

    elif len(nums) >= (m + n):
        p_user = norm_prob_vec(nums[:m])
        q_user = norm_prob_vec(nums[m : m + n])

    if p_user is None or q_user is None:
        log.info(f"NashMixed parse failed nums={nums}")

        msg_lines = [
            "Invalid format for mixed strategy.",
            f"Expected {m+n} numbers: first p (length {m}), then q (length {n}).",
        ]
        if m == 2 and n == 2:
            msg_lines.append("For 2x2 you can also give 2 numbers: p and q (in [0,1]).")
            msg_lines.append("Example: 0.6 0.25")
        else:
            msg_lines.append(f"Example: {' '.join(['0.2'] * m)} {' '.join(['0.2'] * n)}")

        return {
            "ok": True,
            "correct": False,
            "score": 0.0,
            "hits": "none",
            "missing": "invalid_format",
            "wrong": "none",
            "message": "\n".join(msg_lines),
            "explanation_lines": msg_lines,
            "nums_parsed": nums,
        }

    tol = 0.05
    ok = vec_close(p_user, p_corr, tol) and vec_close(q_user, q_corr, tol)

    score = 100.0 if ok else 0.0
    lines = _build_lines(
        correct=ok,
        score=score,
        p_user=p_user,
        q_user=q_user,
        tol=tol,
        reveal=reveal,
        p_corr=p_corr,
        q_corr=q_corr,
    )

    resp: Dict[str, Any] = {
        "ok": True,
        "correct": ok,
        "score": score,
        "p_user": p_user,
        "q_user": q_user,
        "message": "\n".join(lines),
        "explanation_lines": lines,
        "hits": "parsed",
        "missing": "none" if ok else "outside_tolerance",
        "wrong": "none" if ok else "p_or_q",
    }

    if reveal:
        resp["p_correct"] = p_corr
        resp["q_correct"] = q_corr

    return resp
