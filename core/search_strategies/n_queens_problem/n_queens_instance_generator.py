import os
import importlib.util
import random
from .n_queens_validator import NQueensValidator


class NQueensInstanceGenerator:
    """Generates a random N-Queens instance given board size and number of queens, ensuring it is solvable."""

    @staticmethod
    def load_backtracking_solver():
        """
        Loads the generic backtracking solver from:
            core/search_strategies/Algorithms/backtracking.py
        """

        # directorul acestui fișier = core/search_strategies/n_queens_problem
        current_dir = os.path.dirname(__file__)

        # urcăm UN nivel → core/search_strategies
        root_search_dir = os.path.dirname(current_dir)

        # folderul unde sunt toate algoritmurile generice
        algorithms_dir = os.path.join(root_search_dir, "Algorithms")

        solver_path = os.path.join(algorithms_dir, "backtracking.py")

        if not os.path.exists(solver_path):
            raise FileNotFoundError(f"[NQueens] backtracking.py not found at: {solver_path}")

        # dynamic import
        spec = importlib.util.spec_from_file_location("backtracking", solver_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # function expected: solve_nqueens(board)
        return module.solve_nqueens

    @staticmethod
    def generate(board_size: int) -> dict:
        """Generate a random, solvable N-Queens instance."""

        num_queens = random.randint(0, board_size)

        # Load backtracking solver
        solve_bkt = NQueensInstanceGenerator.load_backtracking_solver()

        board = [[0] * board_size for _ in range(board_size)]
        validator = NQueensValidator()

        attempts = 0

        while True:
            attempts += 1

            # Clear board
            for r in range(board_size):
                for c in range(board_size):
                    board[r][c] = 0

            # Random placement of queens (same number as row index position)
            positions = random.sample(range(board_size), num_queens)
            for r, c in enumerate(positions):
                board[r][c] = 1

            # Validate board and ensure solver can solve it
            if validator.is_valid(board, num_queens) and solve_bkt(board) is not None:
                break

            if attempts > 100:
                raise RuntimeError("Failed to generate a valid N-Queens instance after 100 tries.")

        return {
            "problem_name": "N-Queens",
            "board_size": board_size,
            "queen_number_on_board": num_queens,
            "board": board
        }
