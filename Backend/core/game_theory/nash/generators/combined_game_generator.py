from __future__ import annotations

from typing import Any, Dict

from Backend.services.logging_service import Logger
from Backend.core.game_theory.nash.nash_pure_solver import NashPureSolver
from Backend.core.game_theory.nash.nash_mixed_solver import NashMixedSolver
from Backend.core.game_theory.nash.generators.base_generator import NashBaseGenerator
from Backend.core.game_theory.nash.generators.mixed_game_generator import NashMixedGameGenerator

log = Logger("NashCombinedGameGenerator")


class NashCombinedGameGenerator(NashBaseGenerator):
    @staticmethod
    def generate(size: int, payoff_min: int = -9, payoff_max: int = 9) -> Dict[str, Any]:
        if size < 2:
            log.error("Invalid size for combined game", {"size": size})
            raise ValueError("size must be >= 2")

        if size == 3:
            actions_p1 = ["A1", "A2", "A3"]
            actions_p2 = ["B1", "B2", "B3"]

            base = NashMixedGameGenerator._rps_3x3()["payoffs"]
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
        actions_p1, actions_p2 = NashCombinedGameGenerator._actions(m, n)
        payoffs = NashCombinedGameGenerator._random_payoffs(m, n, payoff_min, payoff_max)

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