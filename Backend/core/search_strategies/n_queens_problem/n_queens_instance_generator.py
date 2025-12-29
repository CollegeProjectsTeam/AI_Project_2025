import os
import importlib.util
import random
from .n_queens_validator import NQueensValidator

from Backend.services import Logger

log = Logger("NQueensInstanceGenerator")


class NQueensInstanceGenerator:

    @staticmethod
    def load_backtracking_solver():
        current_dir = os.path.dirname(__file__)
        root_search_dir = os.path.dirname(current_dir)
        algorithms_dir = os.path.join(root_search_dir, "Algorithms")
        solver_path = os.path.join(algorithms_dir, "backtracking.py")

        log.info(
            "Loading backtracking solver",
            ctx={
                "current_dir": current_dir,
                "root_search_dir": root_search_dir,
                "algorithms_dir": algorithms_dir,
                "solver_path": solver_path,
            },
        )

        if not os.path.exists(solver_path):
            log.error("backtracking.py not found", ctx={"solver_path": solver_path})
            raise FileNotFoundError(f"[NQueens] backtracking.py not found at: {solver_path}")

        try:
            spec = importlib.util.spec_from_file_location("backtracking", solver_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            log.error("Failed importing backtracking module", ctx={"solver_path": solver_path}, exc=e)
            raise

        solve_fn = getattr(module, "solve_nqueens", None)
        if not solve_fn:
            log.error(
                "backtracking.py missing solve_nqueens",
                ctx={"solver_path": solver_path},
            )
            raise AttributeError("backtracking.py missing solve_nqueens(board)")

        log.ok("Backtracking solver loaded", ctx={"solver_path": solver_path})
        return solve_fn

    @staticmethod
    def generate(board_size: int) -> dict:
        num_queens = random.randint(0, board_size)

        log.info(
            "Generating N-Queens instance",
            ctx={"board_size": board_size, "num_queens": num_queens},
        )

        solve_bkt = NQueensInstanceGenerator.load_backtracking_solver()

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
                solvable = solve_bkt(board) is not None
            except Exception as e:
                log.error(
                    "Backtracking solver crashed while validating solvability",
                    ctx={"attempts": attempts, "board_size": board_size, "num_queens": num_queens},
                    exc=e,
                )
                solvable = False

            if is_valid and solvable:
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
                    "Failed to generate a valid N-Queens instance after max attempts",
                    ctx={"attempts": attempts, "board_size": board_size, "num_queens": num_queens},
                )
                raise RuntimeError("Failed to generate a valid N-Queens instance after 100 tries.")

        return {
            "problem_name": "N-Queens",
            "board_size": board_size,
            "queen_number_on_board": num_queens,
            "board": board,
        }