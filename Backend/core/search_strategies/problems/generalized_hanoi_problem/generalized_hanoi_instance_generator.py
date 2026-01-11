from __future__ import annotations

from typing import Any

from Backend.services import Logger
from .generalized_hanoi_validator import GeneralizedHanoiValidator

log = Logger("GenHanoiInstanceGenerator")


class GeneralizedHanoiInstanceGenerator:
    @staticmethod
    def generate(disks: int, pegs: int = 4) -> dict[str, Any]:
        validator = GeneralizedHanoiValidator()
        if not validator.is_valid(disks, pegs):
            raise RuntimeError("GeneralizedHanoiInstanceGenerator produced invalid instance")

        # canonical start state: all disks on peg 0, goal is peg pegs-1
        start_state = [list(range(disks, 0, -1))] + [[] for _ in range(pegs - 1)]

        log.ok("Generated Generalized Hanoi instance", ctx={"disks": disks, "pegs": pegs})

        return {
            "problem_name": "Generalized Hanoi",
            "disks": disks,
            "pegs": pegs,
            "start_peg": 0,
            "goal_peg": pegs - 1,
            "start_state": start_state,
        }