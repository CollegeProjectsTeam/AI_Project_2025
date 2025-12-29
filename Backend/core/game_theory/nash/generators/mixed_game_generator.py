from __future__ import annotations

from typing import Any, Dict, List

from Backend.services.logging_service import Logger
from Backend.core.game_theory.nash.nash_pure_solver import NashPureSolver
from Backend.core.game_theory.nash.nash_mixed_solver import NashMixedSolver
from Backend.core.game_theory.nash.generators.base_generator import NashBaseGenerator

log = Logger("NashMixedGameGenerator")


class NashMixedGameGenerator(NashBaseGenerator):
    @staticmethod
    def _rps_3x3() -> Dict[str, Any]:
        a1 = ["A1", "A2", "A3"]
        b1 = ["B1", "B2", "B3"]
        p1 = [
            [0, -1, 1],
            [1, 0, -1],
            [-1, 1, 0],
        ]

        payoffs: List[List[List[int]]] = []
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
    def generate(size: int, payoff_min: int = -9, payoff_max: int = 9) -> Dict[str, Any]:
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

            actions_p1, actions_p2 = NashMixedGameGenerator._actions(m, n)
            payoffs = NashMixedGameGenerator._random_payoffs(m, n, payoff_min, payoff_max)

            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            if pure_eq:
                rejected_pure += 1
                if attempts % 25 == 0:
                    log.warn(
                        "Still searching mixed-only game",
                        {
                            "attempts": attempts,
                            "rejected_pure": rejected_pure,
                            "rejected_no_mixed": rejected_no_mixed,
                        },
                    )
                continue

            mixed_eq = NashMixedSolver.solve(payoffs)
            if mixed_eq is None:
                rejected_no_mixed += 1
                if attempts % 25 == 0:
                    log.warn(
                        "Still searching mixed-only game",
                        {
                            "attempts": attempts,
                            "rejected_pure": rejected_pure,
                            "rejected_no_mixed": rejected_no_mixed,
                        },
                    )
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