from __future__ import annotations

from typing import Any, Dict

from Backend.services.logging_service import Logger
from Backend.core.game_theory.nash.generators.base_generator import NashBaseGenerator

log = Logger("NashPureGameGenerator")


class NashPureGameGenerator(NashBaseGenerator):
    @staticmethod
    def generate(m: int, n: int, payoff_min: int = -9, payoff_max: int = 9) -> Dict[str, Any]:
        if m < 1 or n < 1:
            log.error("Invalid dimensions for pure game", {"m": m, "n": n})
            raise ValueError("m and n must be >= 1")

        actions_p1, actions_p2 = NashPureGameGenerator._actions(m, n)
        payoffs = NashPureGameGenerator._random_payoffs(m, n, payoff_min, payoff_max)

        log.ok("Generated pure game", {"m": m, "n": n, "payoff_min": payoff_min, "payoff_max": payoff_max})
        return {
            "problem_name": "Nash Equilibrium (Pure)",
            "actions_p1": actions_p1,
            "actions_p2": actions_p2,
            "payoffs": payoffs,
        }