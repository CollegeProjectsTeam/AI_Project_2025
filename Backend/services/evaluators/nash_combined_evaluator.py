from __future__ import annotations

from typing import Any, Dict

from Backend.services import Logger
from Backend.core.nash_utils import parse_nash_answer, evaluate_nash_answer, format_eq_list

log = Logger("Eval.NashCombined")


def evaluate_nash_combined(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    meta = item.meta or {}
    payoffs = meta.get("payoffs")
    pure_corr = meta.get("pure_equilibria") or []
    mixed = meta.get("mixed_equilibrium")

    if payoffs is None:
        log.info("NashCombined missing meta (payoffs)")
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

    log.info(
        f"NashCombined score_pure={score_pure} mixed_ok={mixed_ok} "
        f"expected_mixed={correct_has_mixed} -> score={score} correct={correct}"
    )

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