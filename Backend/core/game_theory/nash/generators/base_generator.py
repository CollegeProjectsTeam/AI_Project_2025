from __future__ import annotations

import random
from typing import Any, Dict, List

from Backend.services.logging_service import Logger

log = Logger("NashBaseGenerator")


class NashBaseGenerator:
    @staticmethod
    def _random_payoffs(
        m: int,
        n: int,
        payoff_min: int = -9,
        payoff_max: int = 9,
    ) -> List[List[List[int]]]:
        return [
            [
                [random.randint(payoff_min, payoff_max), random.randint(payoff_min, payoff_max)]
                for _ in range(n)
            ]
            for _ in range(m)
        ]

    @staticmethod
    def _actions(m: int, n: int) -> tuple[list[str], list[str]]:
        return [f"A{i+1}" for i in range(m)], [f"B{j+1}" for j in range(n)]

    @staticmethod
    def instance_to_text(instance: Dict[str, Any]) -> str:
        p1_actions = instance["actions_p1"]
        p2_actions = instance["actions_p2"]
        payoffs = instance["payoffs"]

        col_width = 9
        header = " " * 6 + " | " + " | ".join(f"{b:^{col_width}}" for b in p2_actions) + "\n"
        separator = "-" * (8 + (col_width + 3) * len(p2_actions)) + "\n"

        rows = ""
        for i, a in enumerate(p1_actions):
            row_cells = []
            for j in range(len(p2_actions)):
                p1v, p2v = payoffs[i][j]
                cell = f"({p1v},{p2v})"
                row_cells.append(f"{cell:^{col_width}}")
            rows += f"{a:<6} | " + " | ".join(row_cells) + "\n"

        return header + separator + rows