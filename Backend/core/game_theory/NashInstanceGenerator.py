from __future__ import annotations

import random
from typing import Any, Dict, List

from Backend.services.logging_service import Logger
from Backend.core.game_theory.NashPureSolver import NashPureSolver
from Backend.core.game_theory.NashMixedSolver import NashMixedSolver

log = Logger("NashInstanceGenerator")


class NashInstanceGenerator:
    @staticmethod
    def _random_payoffs(m: int, n: int, payoff_min: int = -9, payoff_max: int = 9) -> List[List[List[int]]]:
        return [
            [
                [random.randint(payoff_min, payoff_max), random.randint(payoff_min, payoff_max)]
                for _ in range(n)
            ]
            for _ in range(m)
        ]

    @staticmethod
    def generate_pure_game(m: int, n: int, payoff_min: int = -9, payoff_max: int = 9) -> Dict[str, Any]:
        if m < 1 or n < 1:
            log.error("Invalid dimensions for pure game", {"m": m, "n": n})
            raise ValueError("m and n must be >= 1")

        actions_p1 = [f"A{i+1}" for i in range(m)]
        actions_p2 = [f"B{j+1}" for j in range(n)]
        payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

        log.ok("Generated pure game", {"m": m, "n": n, "payoff_min": payoff_min, "payoff_max": payoff_max})
        return {
            "problem_name": "Nash Equilibrium (Pure)",
            "actions_p1": actions_p1,
            "actions_p2": actions_p2,
            "payoffs": payoffs,
        }

    @staticmethod
    def _rps_3x3() -> Dict[str, Any]:
        a1 = ["A1", "A2", "A3"]
        b1 = ["B1", "B2", "B3"]
        p1 = [
            [0, -1, 1],
            [1, 0, -1],
            [-1, 1, 0],
        ]

        payoffs = []
        for i in range(3):
            row = []
            for j in range(3):
                row.append([p1[i][j], -p1[i][j]])
            payoffs.append(row)

        return {
            "problem_name": "Nash Equilibrium (Mixed)",
            "actions_p1": a1,
            "actions_p2": b1,
            "payoffs": payoffs,
            "mixed_equilibrium": {
                "p1": [1 / 3, 1 / 3, 1 / 3],
                "p2": [1 / 3, 1 / 3, 1 / 3],
            },
        }

    @staticmethod
    def generate_mixed_game(size: int, payoff_min: int = -9, payoff_max: int = 9) -> Dict[str, Any]:
        if size < 2:
            log.error("Invalid size for mixed game", {"size": size})
            raise ValueError("size must be >= 2")

        m = n = size
        attempts = 0
        rejected_pure = 0
        rejected_no_mixed = 0

        log.info("Generating mixed game", {"size": size, "payoff_min": payoff_min, "payoff_max": payoff_max})

        while True:
            attempts += 1

            actions_p1 = [f"A{i+1}" for i in range(m)]
            actions_p2 = [f"B{j+1}" for j in range(n)]
            payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            if pure_eq:
                rejected_pure += 1
                if attempts % 25 == 0:
                    log.warn("Still searching mixed-only game", {"attempts": attempts, "rejected_pure": rejected_pure, "rejected_no_mixed": rejected_no_mixed})
                continue

            mixed_eq = NashMixedSolver.solve(payoffs)
            if mixed_eq is None:
                rejected_no_mixed += 1
                if attempts % 25 == 0:
                    log.warn("Still searching mixed-only game", {"attempts": attempts, "rejected_pure": rejected_pure, "rejected_no_mixed": rejected_no_mixed})
                continue

            log.ok(
                "Mixed game generated",
                {
                    "size": size,
                    "attempts": attempts,
                    "rejected_pure": rejected_pure,
                    "rejected_no_mixed": rejected_no_mixed,
                    "support_p1": len(mixed_eq.get("support_p1", [])),
                    "support_p2": len(mixed_eq.get("support_p2", [])),
                },
            )

            return {
                "problem_name": "Nash Equilibrium (Mixed)",
                "actions_p1": actions_p1,
                "actions_p2": actions_p2,
                "payoffs": payoffs,
                "mixed_equilibrium": mixed_eq,
            }

    @staticmethod
    def generate_combined_game(size: int, payoff_min: int = -9, payoff_max: int = 9) -> Dict[str, Any]:
        if size < 2:
            log.error("Invalid size for combined game", {"size": size})
            raise ValueError("size must be >= 2")

        if size == 3:
            actions_p1 = ["A1", "A2", "A3"]
            actions_p2 = ["B1", "B2", "B3"]

            base = NashInstanceGenerator._rps_3x3()["payoffs"]
            payoffs = [
                [base[0][0], base[0][1], base[0][2]],
                [base[1][0], base[1][1], base[1][2]],
                [base[2][0], base[2][1], base[2][2]],
            ]

            payoffs[0][0] = [9, 9]
            payoffs[1][0] = [0, 2]
            payoffs[2][0] = [0, 2]
            payoffs[0][1] = [2, 0]
            payoffs[0][2] = [2, 0]

            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            mixed_eq = NashMixedSolver.solve(payoffs)

            log.ok(
                "Generated combined 3x3 game",
                {"size": size, "pure_eq_count": len(pure_eq), "has_mixed": mixed_eq is not None},
            )

            return {
                "problem_name": "Nash Equilibrium (Combined)",
                "actions_p1": actions_p1,
                "actions_p2": actions_p2,
                "payoffs": payoffs,
                "pure_equilibria": pure_eq,
                "mixed_equilibrium": mixed_eq,
            }

        m = n = size
        actions_p1 = [f"A{i+1}" for i in range(m)]
        actions_p2 = [f"B{j+1}" for j in range(n)]
        payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

        pure_eq = NashPureSolver.find_nash_pure(payoffs)
        mixed_eq = NashMixedSolver.solve(payoffs)

        log.ok(
            "Generated combined game",
            {"size": size, "pure_eq_count": len(pure_eq), "has_mixed": mixed_eq is not None},
        )

        return {
            "problem_name": "Nash Equilibrium (Combined)",
            "actions_p1": actions_p1,
            "actions_p2": actions_p2,
            "payoffs": payoffs,
            "pure_equilibria": pure_eq,
            "mixed_equilibrium": mixed_eq,
        }

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
