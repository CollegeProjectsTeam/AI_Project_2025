import os
import importlib.util
import random
from .n_queens_validator import NQueensValidator

class NQueensInstanceGenerator:
    """Generates a random N-Queens instance given board size and number of queens, ensuring it is solvable"""

    @staticmethod
    def load_backtracking_solver():
        """Dynamically loads the backtracking solver module."""
        algorithm_folder = "core/search_strategies/n_queens_problem/Algorithms"
        algorithm_file = "backtracking.py"
        algorithms_path = os.path.join(os.getcwd(), algorithm_folder, algorithm_file)

        spec = importlib.util.spec_from_file_location("backtracking", algorithms_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.solve_nqueens
    

    @staticmethod
    def generate(board_size: int) -> dict:
        
        num_queens = random.randint(0, board_size)

        # Load the backtracking solver
        solve_bkt = NQueensInstanceGenerator.load_backtracking_solver()

        board = [[0] * board_size for _ in range(board_size)]
        validator = NQueensValidator()

        attempts = 0
        while True:
            attempts += 1
            # Reset board
            for r in range(board_size):
                for c in range(board_size):
                    board[r][c] = 0

            # Place queens randomly
            positions = random.sample(range(board_size), num_queens)
            for r, c in enumerate(positions):
                board[r][c] = 1

            # Validate board and ensure it is solvable
            if validator.is_valid(board, num_queens) and solve_bkt(board) is not None:
                break

            if attempts > 100:
                raise RuntimeError("Failed to generate a valid N-Queens instance after 100 tries")

        return {
            "problem_name": "N-Queens",
            "board_size": board_size,
            "queen_number_on_board": num_queens,
            "board": board
        }
