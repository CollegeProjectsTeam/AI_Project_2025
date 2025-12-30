from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from Backend.services import Logger
from Backend.core.game_theory.minmax.minmax_solver import MinMaxAlphaBetaSolver

log = Logger("Eval.MinMax")


def _parse_ints(val: Any) -> List[int]:
    s = str(val or "").strip()
    if not s:
        return []
    return [int(x) for x in re.findall(r"-?\d+", s)]


def _parse_one_int(val: Any) -> Tuple[int | None, bool]:
    nums = _parse_ints(val)
    if len(nums) < 1:
        return None, False
    return nums[0], True


def _parse_two_ints(val: Any) -> Tuple[int | None, int | None, bool]:
    nums = _parse_ints(val)
    if len(nums) < 2:
        return None, None, False
    return nums[0], nums[1], True


def _solve_from_meta(item: Any) -> Tuple[int | None, int | None, str | None]:
    meta = getattr(item, "meta", None) or {}

    tree = meta.get("tree")
    if not isinstance(tree, dict):
        return None, None, "missing tree in meta"

    root_player = str(meta.get("root_player") or "MAX").strip().upper()
    if root_player not in ("MAX", "MIN"):
        root_player = "MAX"

    solved = MinMaxAlphaBetaSolver.solve({"root_player": root_player, "tree": tree})
    if not solved.get("ok"):
        return None, None, str(solved.get("error") or "minmax solver failed")

    return int(solved["root_value"]), int(solved["leaf_visits"]), None


def _expected_from_item(item: Any) -> Tuple[int | None, int | None, str | None]:
    meta = getattr(item, "meta", None) or {}

    # Prefer solution stored in meta (fast + safe)
    sol = meta.get("solution")
    if isinstance(sol, dict):
        rv = sol.get("root_value")
        lv = sol.get("leaf_visits")
        if isinstance(rv, int) and isinstance(lv, int):
            return rv, lv, None

    # Otherwise solve from meta.tree
    return _solve_from_meta(item)


def _fmt_for(meta: Dict[str, Any]) -> str:
    fmt = str(meta.get("answer_format") or "").strip().lower()
    if fmt in ("root_value", "root_value leaf_visits"):
        return fmt
    # default for older items
    return "root_value leaf_visits"


def evaluate_minmax(*, item: Any, answer: Any, reveal: bool = False) -> Dict[str, Any]:
    qid = getattr(item, "id", None)
    meta = getattr(item, "meta", None) or {}
    fmt = _fmt_for(meta)

    exp_root, exp_leaves, err = _expected_from_item(item)
    if err is not None or exp_root is None or exp_leaves is None:
        log.warn("MinMax missing expected answer", {"qid": qid, "error": err})
        return {"ok": False, "error": "minmax evaluator missing expected answer"}

    # ---------------- easy: only root_value ----------------
    if fmt == "root_value":
        user_root, ok_parse = _parse_one_int(answer)
        if not ok_parse or user_root is None:
            msg = "Answer must contain one integer: root_value (example: -2)"
            log.info("Invalid MinMax answer format (root only)", {"qid": qid, "answer": str(answer or "")})
            return {
                "ok": True,
                "correct": False,
                "score": 0.0,
                "message": msg,
                "explanation_lines": [msg],
            }

        correct = (int(user_root) == int(exp_root))
        score = 100.0 if correct else 0.0

        resp: Dict[str, Any] = {
            "ok": True,
            "correct": correct,
            "score": score,
            "received": {"root_value": int(user_root)},
        }

        lines = [
            "MinMax (Alpha-Beta): compute the value at the root.",
            "Format: root_value (one integer).",
            f"Expected root_value: {int(exp_root)}",
            f"Your root_value: {int(user_root)}",
        ]
        resp["explanation_lines"] = lines

        # if reveal or incorrect, show full correct solution (also leaf visits)
        if reveal or not correct:
            resp["correct_answer_text"] = str(int(exp_root))
            resp["correct_answer"] = {"root_value": int(exp_root), "leaf_visits": int(exp_leaves)}

        log.info(
            "MinMax evaluated (root only)",
            {"qid": qid, "correct": correct, "score": score, "received_root": int(user_root), "expected_root": int(exp_root)},
        )
        return resp

    # ---------------- medium/hard: root_value + leaf_visits ----------------
    user_root, user_leaves, ok_parse = _parse_two_ints(answer)
    if not ok_parse or user_root is None or user_leaves is None:
        msg = "Answer must contain two integers: root_value leaf_visits (example: -2 8)"
        log.info("Invalid MinMax answer format (two ints)", {"qid": qid, "answer": str(answer or "")})
        return {
            "ok": True,
            "correct": False,
            "score": 0.0,
            "message": msg,
            "explanation_lines": [msg],
        }

    correct = (int(user_root) == int(exp_root)) and (int(user_leaves) == int(exp_leaves))
    score = 100.0 if correct else 0.0

    resp = {
        "ok": True,
        "correct": correct,
        "score": score,
        "received": {"root_value": int(user_root), "leaf_visits": int(user_leaves)},
        "explanation_lines": [
            "MinMax (Alpha-Beta): compute the value at the root and how many leaves were visited.",
            "Format: root_value leaf_visits (two integers).",
            f"Expected: {int(exp_root)} {int(exp_leaves)}",
            f"Your answer: {int(user_root)} {int(user_leaves)}",
        ],
    }

    if reveal or not correct:
        resp["correct_answer_text"] = f"{int(exp_root)} {int(exp_leaves)}"
        resp["correct_answer"] = {"root_value": int(exp_root), "leaf_visits": int(exp_leaves)}

    log.info(
        "MinMax evaluated",
        {
            "qid": qid,
            "correct": correct,
            "score": score,
            "received": [int(user_root), int(user_leaves)],
            "expected": [int(exp_root), int(exp_leaves)],
        },
    )

    return resp
