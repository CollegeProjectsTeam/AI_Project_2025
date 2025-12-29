from Backend.services import Logger

log = Logger("NQueensValidator")

class NQueensValidator:

    @staticmethod
    def is_valid(board: list[list[int]], num_queens: int) -> bool:
        n = len(board)
        queens = [(r, c) for r in range(n) for c in range(n) if board[r][c] == 1]

        if len(queens) != num_queens:
            return False

        for i, (r1, c1) in enumerate(queens):
            for j in range(i + 1, len(queens)):
                r2, c2 = queens[j]
                if r1 == r2:
                    return False
                if c1 == c2:
                    return False
                if abs(r1 - r2) == abs(c1 - c2):
                    return False

        log.ok("Board is valid", ctx={"board_size": n, "num_queens": num_queens})
        return True
