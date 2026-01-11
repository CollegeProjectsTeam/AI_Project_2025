from __future__ import annotations

import random
from typing import Any

from Backend.services import Logger
from .knights_tour_validator import KnightsTourValidator

log = Logger("KnightsTourInstanceGenerator")


class KnightsTourInstanceGenerator:
    @staticmethod
    def generate(board_size: int, start: tuple[int, int] | None = None) -> dict[str, Any]:
        if start is None:
            start = (random.randrange(0, board_size), random.randrange(0, board_size))

        validator = KnightsTourValidator()
        if not validator.is_valid(board_size, start):
            raise RuntimeError("KnightsTourInstanceGenerator produced invalid instance")

        log.ok("Generated Knights Tour instance", ctx={"board_size": board_size, "start": list(start)})

        return {
            "problem_name": "Knights Tour",
            "board_size": board_size,
            "start": [start[0], start[1]],
        }