def backtrack(solution, is_complete, generate_options, is_valid):
    if is_complete(solution):
        return solution
    for option in generate_options(solution):
        if is_valid(option, solution):
            solution.append(option)
            if backtrack(solution, is_complete, generate_options, is_valid):
                return solution
            solution.pop()
    return None


def is_complete_nqueens(solution, n):
    return len(solution) == n


def generate_options_nqueens(solution, n):
    return list(range(n))


def is_valid_nqueens(col, solution):
    row = len(solution)
    for r, c in enumerate(solution):
        if c == col or abs(c - col) == abs(r - row):
            return False
    return True


def solve_nqueens(board):
    n = len(board)
    initial_state = []

    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    sol = backtrack(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens
    )
    return sol

def print_board(solution):
    if not solution:
        print("No solution found.")
        return
    n = len(solution)
    for r in range(n):
        line = ""
        for c in range(n):
            line += "1 " if solution[r] == c else "0 "
        print(line)
    print()