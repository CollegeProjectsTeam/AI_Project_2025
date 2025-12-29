from __future__ import annotations

from typing import Any, Dict, List, Tuple

from Backend.services import Logger
from Backend.core.nash_utils import parse_nash_answer, evaluate_nash_answer, format_eq_list

log = Logger("Eval.NashPure")


def _parse_correct_eqs(correct_answer: str) -> List[Tuple[int, int]]:
    correct_eqs: List[Tuple[int, int]] = []
    corr = (correct_answer or "").strip().lower()

    if corr in ("none", ""):
        return correct_eqs

    parts = corr.replace(" ", "").split("),")
    for p in parts:
        p = p.replace("(", "").replace(")", "").strip()
        if not p:
            continue
        a, b = p.split(",")
        correct_eqs.append((int(a) - 1, int(b) - 1))

    return correct_eqs


def evaluate_nash_pure(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    meta = item.meta or {}
    m = int(meta.get("m") or 0)
    n = int(meta.get("n") or 0)
    payoffs = meta.get("payoffs")

    log.info(f"NashPure evaluate m={m} n={n} reveal={reveal}")

    if not m or not n or payoffs is None:
        log.info("NashPure missing meta (m/n/payoffs)")
        return {"ok": False, "error": "missing nash meta"}

    correct_eqs = _parse_correct_eqs(item.correct_answer or "")
    ans_str = "" if answer is None else str(answer)

    user_pairs, user_said_none = parse_nash_answer(ans_str, m, n, payoffs)
    score, hits, missing, wrong = evaluate_nash_answer(correct_eqs, user_pairs, user_said_none)

    log.info(
        f"NashPure result score={score} hits={len(hits)} missing={len(missing)} wrong={len(wrong)} user_none={user_said_none}"
    )

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