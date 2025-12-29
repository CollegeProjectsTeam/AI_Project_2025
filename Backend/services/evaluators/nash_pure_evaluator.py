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


def _best_responses_p1(payoffs: Any, m: int, n: int) -> Dict[int, List[int]]:
    br: Dict[int, List[int]] = {}
    for j in range(n):
        vals = [int(payoffs[i][j][0]) for i in range(m)]
        mx = max(vals)
        br[j] = [i for i, v in enumerate(vals) if v == mx]
    return br


def _best_responses_p2(payoffs: Any, m: int, n: int) -> Dict[int, List[int]]:
    br: Dict[int, List[int]] = {}
    for i in range(m):
        vals = [int(payoffs[i][j][1]) for j in range(n)]
        mx = max(vals)
        br[i] = [j for j, v in enumerate(vals) if v == mx]
    return br


def _format_action_set(prefix: str, idxs: List[int]) -> str:
    if not idxs:
        return "none"
    return ", ".join(f"{prefix}{k+1}" for k in idxs)


def _vec_int(vals: List[int]) -> str:
    return "[" + ", ".join(str(x) for x in vals) + "]"


def _explain_pure_nash(
    payoffs: Any,
    m: int,
    n: int,
    correct_eqs: List[Tuple[int, int]],
    hits: List[Tuple[int, int]],
    missing: List[Tuple[int, int]],
    wrong: List[Tuple[int, int]],
    reveal: bool,
) -> List[str]:
    br1 = _best_responses_p1(payoffs, m, n)
    br2 = _best_responses_p2(payoffs, m, n)

    lines: List[str] = []
    lines.append("A pure Nash equilibrium (Ai,Bj) occurs when:")
    lines.append("- Ai is a best response for P1 to Bj (maximizes P1 payoff in column Bj)")
    lines.append("- Bj is a best response for P2 to Ai (maximizes P2 payoff in row Ai)")
    lines.append("")

    lines.append("P1 best responses (for each column Bj):")
    for j in range(n):
        vals = [int(payoffs[i][j][0]) for i in range(m)]
        lines.append(f"- B{j+1}: {_format_action_set('A', br1[j])}  (P1 payoffs in column: {_vec_int(vals)})")
    lines.append("")

    lines.append("P2 best responses (for each row Ai):")
    for i in range(m):
        vals = [int(payoffs[i][j][1]) for j in range(n)]
        lines.append(f"- A{i+1}: {_format_action_set('B', br2[i])}  (P2 payoffs in row: {_vec_int(vals)})")
    lines.append("")

    if correct_eqs:
        lines.append(f"Correct equilibria: {format_eq_list(correct_eqs)}")
    else:
        lines.append("There is no pure Nash equilibrium (no cell is a best response for both players).")

    if hits:
        lines.append(f"Correct in your answer: {format_eq_list(hits)}")

    if missing:
        lines.append("")
        lines.append("Why these equilibria are missing from your answer:")
        for (i, j) in missing:
            p1 = int(payoffs[i][j][0])
            p2 = int(payoffs[i][j][1])
            lines.append(f"- (A{i+1},B{j+1}) = ({p1},{p2}) is Nash because:")
            lines.append(f"  * at B{j+1}, P1 best response(s): {_format_action_set('A', br1[j])}")
            lines.append(f"  * at A{i+1}, P2 best response(s): {_format_action_set('B', br2[i])}")

    if wrong:
        lines.append("")
        lines.append("Why your selected cells are not Nash (at least one player has a profitable deviation):")
        for (i, j) in wrong:
            p1 = int(payoffs[i][j][0])
            p2 = int(payoffs[i][j][1])
            lines.append(f"- (A{i+1},B{j+1}) = ({p1},{p2}) is NOT Nash.")

            if i not in br1[j]:
                vals = [int(payoffs[ii][j][0]) for ii in range(m)]
                mx = max(vals)
                best_rows = br1[j]
                lines.append(
                    f"  * P1 can deviate to {_format_action_set('A', best_rows)} "
                    f"(payoff {mx} > {p1})."
                )

            if j not in br2[i]:
                vals = [int(payoffs[i][jj][1]) for jj in range(n)]
                mx = max(vals)
                best_cols = br2[i]
                lines.append(
                    f"  * P2 can deviate to {_format_action_set('B', best_cols)} "
                    f"(payoff {mx} > {p2})."
                )

    if reveal:
        lines.append("")
        lines.append("Note: with reveal=true you can also include the full correct answer in the payload.")

    return lines


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

    explanation_lines = _explain_pure_nash(
        payoffs=payoffs,
        m=m,
        n=n,
        correct_eqs=correct_eqs,
        hits=hits,
        missing=missing,
        wrong=wrong,
        reveal=reveal,
    )

    resp: Dict[str, Any] = {
        "ok": True,
        "correct": (float(score) == 100.0),
        "score": score,
        "hits": format_eq_list(hits),
        "missing": format_eq_list(missing),
        "wrong": format_eq_list(wrong),
        "explanation_lines": explanation_lines,
    }

    if reveal:
        resp["correct_answer"] = item.correct_answer

    return resp