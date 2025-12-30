from __future__ import annotations

import random
from typing import Any, Dict, List

from Backend.services.logging_service import Logger
from Backend.core.game_theory.minmax.minmax_utils import build_instance_string

log = Logger("MinMax.Generator")

TreeNode = Dict[str, Any]


class MinMaxInstanceGenerator:
    @staticmethod
    def _leaf(value: int) -> TreeNode:
        return {"value": int(value)}

    @staticmethod
    def _node(children: List[TreeNode]) -> TreeNode:
        return {"children": children}

    @staticmethod
    def _build_full_tree(depth: int, branching: int, vmin: int, vmax: int) -> TreeNode:
        if depth <= 0:
            return MinMaxInstanceGenerator._leaf(random.randint(vmin, vmax))
        children = [
            MinMaxInstanceGenerator._build_full_tree(depth - 1, branching, vmin, vmax)
            for _ in range(branching)
        ]
        return MinMaxInstanceGenerator._node(children)

    @staticmethod
    def generate(
        depth: int = 3,
        branching: int = 2,
        value_min: int = -9,
        value_max: int = 9,
        root_player: str = "MAX",
    ) -> Dict[str, Any]:
        depth = max(1, int(depth))
        branching = max(2, int(branching))

        root_player = (root_player or "MAX").strip().upper()
        if root_player not in ("MAX", "MIN"):
            root_player = "MAX"

        tree = MinMaxInstanceGenerator._build_full_tree(depth, branching, value_min, value_max)

        instance_params: Dict[str, Any] = {
            "problem_name": "MinMax (Alpha-Beta)",
            "root_player": root_player,
            "depth": depth,
            "branching": branching,
            "tree": tree,
        }

        instance_params["instance"] = build_instance_string(instance_params)

        log.ok(
            "Generated MinMax instance",
            {"depth": depth, "branching": branching, "root_player": root_player},
        )
        return instance_params