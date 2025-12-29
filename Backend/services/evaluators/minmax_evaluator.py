from __future__ import annotations

import re
from typing import Any, Dict, Tuple

from Backend.services import Logger
from Backend.core.game_theory.minmax.minmax_solver import MinMaxAlphaBetaSolver

log = Logger("Eval.MinMax")


def _parse_two_ints(val: Any) -> Tuple[int | None, int | None, bool]:
    s = str(val or "").strip()
    if not s:
        return None, None, False

    nums = re.findall(r"-?\d+", s)
    if len(nums) < 2:
        return None, None, False

    try:
        return int(nums[0]), int(nums[1]), True
    except Exception:
        return None, None, False


def _expected_from_item(item: Any) -> Tuple[int | None, int | None]:
    meta = getattr(item, "meta", None) or {}

    sol = meta.get("solution")
    if isinstance(sol, dict):
        rv = sol.get("root_value")
        lv = sol.get("leaf_visits")
        if isinstance(rv, int) and isinstance(lv, int):
            return rv, lv

    rv, lv, ok = _parse_two_ints(getattr(item, "correct_answer", None))
    if ok:
        return rv, lv

    return None, None


def _try_solve_from_meta(item: Any) -> Tuple[int | None, int | None, str | None]:
    meta = getattr(item, "meta", None) or {}

    tree = meta.get("tree")
    if isinstance(tree, dict):
        solved = MinMaxAlphaBetaSolver.solve(tree)
        if solved.get("ok"):
            return int(solved["root_value"]), int(solved["leaf_visits"]), None
        return None, None, str(solved.get("error") or "minmax solver failed")

    inst = meta.get("instance")
    if isinstance(inst, dict):
        t2 = inst.get("tree")
        if isinstance(t2, dict):
            solved = MinMaxAlphaBetaSolver.solve(t2)
            if solved.get("ok"):
                return int(solved["root_value"]), int(solved["leaf_visits"]), None
            return None, None, str(solved.get("error") or "minmax solver failed")

        solved = MinMaxAlphaBetaSolver.solve(inst)
        if solved.get("ok"):
            return int(solved["root_value"]), int(solved["leaf_visits"]), None
        return None, None, str(solved.get("error") or "minmax solver failed")

    return None, None, "missing tree in meta"


def _build_explanation(
    exp_root: int,
    exp_leaves: int,
    user_root: int,
    user_leaves: int,
    meta: Dict[str, Any],
) -> str:
    root_player = meta.get("root_player")
    if not root_player and isinstance(meta.get("instance"), dict):
        root_player = meta["instance"].get("root_player")
    rp = str(root_player or "MAX").upper()

    lines = [
        "MinMax evaluates a game tree where MAX tries to maximize the score and MIN tries to minimize it.",
        "Alpha-Beta pruning speeds this up by skipping branches that cannot affect the final decision.",
        "Answer format: `root_value leaf_visits` (example: `-2 8`).",
        f"Expected: {exp_root} {exp_leaves}. Received: {user_root} {user_leaves}.",
        f"Root player: {rp}.",
    ]

    return "\n".join(lines)


def evaluate_minmax(item: Any, answer: Any, reveal: bool = False) -> Dict[str, Any]:
    qid = getattr(item, "id", None)

    user_root, user_leaves, ok_parse = _parse_two_ints(answer)
    if not ok_parse:
        log.info(
            "Invalid MinMax answer format",
            {"qid": qid, "answer": str(answer or "")},
        )
        return {
            "ok": False,
            "error": "Answer must contain two integers: root_value leaf_visits (example: -2 8)",
        }

    exp_root, exp_leaves = _expected_from_item(item)

    if exp_root is None or exp_leaves is None:
        sr, sl, err = _try_solve_from_meta(item)
        if err is None:
            exp_root, exp_leaves = sr, sl
        else:
            log.warn(
                "MinMax evaluator missing expected answer",
                {"qid": qid, "error": err},
            )
            return {"ok": False, "error": "minmax evaluator missing expected answer"}

    correct = (user_root == exp_root) and (user_leaves == exp_leaves)
    score = 100.0 if correct else 0.0

    resp: Dict[str, Any] = {"ok": True, "correct": correct, "score": score}

    if reveal or not correct:
        resp["correct_answer"] = f"{exp_root} {exp_leaves}"
        resp["received"] = {"root_value": user_root, "leaf_visits": user_leaves}
        meta = getattr(item, "meta", None) or {}
        resp["explanation"] = _build_explanation(
            exp_root=int(exp_root),
            exp_leaves=int(exp_leaves),
            user_root=int(user_root),
            user_leaves=int(user_leaves),
            meta=meta,
        )

    log.info(
        "MinMax evaluated",
        {
            "qid": qid,
            "correct": correct,
            "score": score,
            "received": [user_root, user_leaves],
            "expected": [exp_root, exp_leaves],
        },
    )

    return resp