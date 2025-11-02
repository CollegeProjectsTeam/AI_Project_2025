class NQueensValidator:
    """Validates N-Queens board instances."""

    @staticmethod
    def is_valid(board: list[list[int]], num_queens: int) -> bool:
        """Check if the board has no queens attacking each other."""
        n = len(board)
        queens = [(r, c) for r in range(n) for c in range(n) if board[r][c] == 1]

        if len(queens) != num_queens:
            return False

        for i, (r1, c1) in enumerate(queens):
            for j in range(i + 1, len(queens)):
                r2, c2 = queens[j]
                # Check same row
                if r1 == r2:
                    return False
                # Check same column
                if c1 == c2:
                    return False
                # Check diagonals
                if abs(r1 - r2) == abs(c1 - c2):
                    return False
        return True
