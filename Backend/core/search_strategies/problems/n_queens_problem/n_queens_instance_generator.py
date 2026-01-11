from __future__ import annotations

import random
from typing import Any

from Backend.services import Logger
from .n_queens_validator import NQueensValidator

from Backend.core.search_strategies.algorithms_generic import backtracking as bt
from Backend.core.search_strategies.problems.nqueens import build_nqueens_problem
from Backend.core.search_strategies.search_problem import SearchBudget

log = Logger("NQueensInstanceGenerator")

class NQueensInstanceGenerator:
    @staticmethod
    def generate(board_size: int) -> dict[str, Any]:
        num_queens = random.randint(0, board_size)

        log.info(
            "Generating N-Queens instance",
            ctx={"board_size": board_size, "num_queens": num_queens},
        )

        board = [[0] * board_size for _ in range(board_size)]
        validator = NQueensValidator()

        attempts = 0
        while True:
            attempts += 1

            for r in range(board_size):
                for c in range(board_size):
                    board[r][c] = 0

            positions = random.sample(range(board_size), num_queens)
            for r, c in enumerate(positions):
                board[r][c] = 1

            is_valid = validator.is_valid(board, num_queens)
            if not is_valid:
                if attempts % 10 == 0:
                    log.info(
                        "Still searching for a valid solvable instance",
                        ctx={
                            "attempts": attempts,
                            "board_size": board_size,
                            "num_queens": num_queens,
                            "status": "invalid_board",
                        },
                    )
                if attempts > 100:
                    log.error(
                        "Failed to generate a valid N-Queens instance after max attempts",
                        ctx={"attempts": attempts, "board_size": board_size, "num_queens": num_queens},
                    )
                    raise RuntimeError("Failed to generate a valid N-Queens instance after 100 tries.")
                continue

            try:
                problem = build_nqueens_problem(board)
                budget = SearchBudget(max_time_s=0.7, max_expansions=200_000)
                solvable = bt(problem, budget) is not None
            except Exception as e:
                log.error(
                    "Backtracking crashed while validating solvability",
                    ctx={"attempts": attempts, "board_size": board_size, "num_queens": num_queens},
                    exc=e,
                )
                solvable = False

            if solvable:
                log.ok(
                    "Generated solvable N-Queens instance",
                    ctx={"attempts": attempts, "board_size": board_size, "num_queens": num_queens},
                )
                break

            if attempts % 10 == 0:
                log.info(
                    "Still searching for a valid solvable instance",
                    ctx={
                        "attempts": attempts,
                        "board_size": board_size,
                        "num_queens": num_queens,
                        "status": "not_solvable_yet",
                    },
                )

            if attempts > 100:
                log.error(
                    "Failed to generate a solvable N-Queens instance after max attempts",
                    ctx={"attempts": attempts, "board_size": board_size, "num_queens": num_queens},
                )
                raise RuntimeError("Failed to generate a solvable N-Queens instance after 100 tries.")

        return {
            "problem_name": "N-Queens",
            "board_size": board_size,
            "queen_number_on_board": num_queens,
            "board": board,
        }