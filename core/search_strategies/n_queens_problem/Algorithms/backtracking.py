def backtrack(solution, is_complete, generate_options, is_valid):
    if is_complete(solution):
        #print("Solutie gasita:", solution)
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

    #print(f"Stare initiala: {initial_state}")

    return backtrack(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens
    )

    #print(f"Stare initiala: {solution}")