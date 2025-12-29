from __future__ import annotations

from typing import Any, Dict, Tuple

from Backend.services.logging_service import Logger
from Backend.core.game_theory.minmax.minmax_utils import validate_tree, is_leaf

log = Logger("MinMax.Solver")

TreeNode = Dict[str, Any]


class MinMaxAlphaBetaSolver:
    @staticmethod
    def solve(instance_params: Dict[str, Any]) -> Dict[str, Any]:
        root_player = (instance_params.get("root_player") or "MAX").strip().upper()
        tree = instance_params.get("tree")

        ok, err = validate_tree(tree)
        if not ok:
            log.warn("solve called with invalid tree", {"err": err})
            return {"ok": False, "error": err}

        is_max = root_player != "MIN"
        value, leaf_visits = MinMaxAlphaBetaSolver._alpha_beta(
            node=tree,
            is_max=is_max,
            alpha=-10**18,
            beta=10**18,
        )

        resp = {
            "ok": True,
            "root_value": value,
            "leaf_visits": leaf_visits,
            "root_player": root_player,
        }
        log.ok("Solved MinMax Alpha-Beta", resp)
        return resp

    @staticmethod
    def _alpha_beta(node: TreeNode, is_max: bool, alpha: int, beta: int) -> Tuple[int, int]:
        if is_leaf(node):
            return int(node["value"]), 1

        children = node.get("children") or []
        leaf_visits_total = 0

        if is_max:
            best = -10**18
            for ch in children:
                v, lv = MinMaxAlphaBetaSolver._alpha_beta(ch, False, alpha, beta)
                leaf_visits_total += lv
                if v > best:
                    best = v
                if best > alpha:
                    alpha = best
                if alpha >= beta:
                    break
            return best, leaf_visits_total

        best = 10**18
        for ch in children:
            v, lv = MinMaxAlphaBetaSolver._alpha_beta(ch, True, alpha, beta)
            leaf_visits_total += lv
            if v < best:
                best = v
            if best < beta:
                beta = best
            if alpha >= beta:
                break
        return best, leaf_visits_total
