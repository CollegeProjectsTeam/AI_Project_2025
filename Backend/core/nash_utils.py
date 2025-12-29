from __future__ import annotations

from typing import Any, List, Tuple

from Backend.services.logging_service import Logger

log = Logger("NashUtils")


def parse_nash_answer(answer_str: Any, m: int, n: int, payoffs=None) -> tuple[List[Tuple[int, int]], bool]:
    s = ("" if answer_str is None else str(answer_str)).strip().lower()
    if s in ("none", "no", "nu", "0"):
        log.info("User answered none", {"m": m, "n": n})
        return [], True

    cleaned = ("" if answer_str is None else str(answer_str)).replace("(", " ").replace(")", " ").replace(";", " ")
    tokens = cleaned.replace(",", " ").split()

    nums: List[int] = []
    for tok in tokens:
        try:
            nums.append(int(tok))
        except ValueError:
            continue

    pairs: List[Tuple[int, int]] = []
    for i in range(0, len(nums), 2):
        if i + 1 >= len(nums):
            break
        r, c = nums[i], nums[i + 1]
        if 1 <= r <= m and 1 <= c <= n:
            pairs.append((r - 1, c - 1))

    pairs = list(set(pairs))

    used_payoff_match = False
    if not pairs and payoffs is not None and len(nums) == 2:
        pay1, pay2 = nums
        payoff_matches: List[Tuple[int, int]] = []
        for i in range(m):
            for j in range(n):
                p1v, p2v = payoffs[i][j]
                if p1v == pay1 and p2v == pay2:
                    payoff_matches.append((i, j))
        if len(payoff_matches) == 1:
            pairs = payoff_matches
            used_payoff_match = True

    log.ok(
        "Parsed nash answer",
        {
            "raw": ("" if answer_str is None else str(answer_str))[:120],
            "tokens": len(tokens),
            "nums": len(nums),
            "pairs": len(pairs),
            "used_payoff_match": used_payoff_match,
        },
    )

    return pairs, False


def evaluate_nash_answer(
    correct_eqs: List[Tuple[int, int]],
    user_eqs: List[Tuple[int, int]],
    user_said_none: bool,
) -> tuple[float, List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
    if not correct_eqs:
        if user_said_none and not user_eqs:
            log.ok("nash evaluation: correct none", {"score": 100.0})
            return 100.0, [], [], []
        log.warn("nash evaluation: expected none but user gave eqs", {"score": 0.0, "user_eqs": len(user_eqs)})
        return 0.0, [], [], user_eqs

    correct_set = set(correct_eqs)
    user_set = set(user_eqs)

    hits = list(correct_set & user_set)
    missing = list(correct_set - user_set)
    wrong = list(user_set - correct_set)

    score = 100.0 * len(hits) / len(correct_set)
    score = round(score, 2)

    log.ok(
        "nash evaluated",
        {"score": score, "hits": len(hits), "missing": len(missing), "wrong": len(wrong)},
    )

    return score, hits, missing, wrong


def format_eq_list(eq_list: List[Tuple[int, int]]) -> str:
    if not eq_list:
        return "none"
    return ", ".join(f"({i+1},{j+1})" for i, j in eq_list)
