def dls(state, depth, is_complete, generate_options, is_valid):
    if is_complete(state):
        print("Solutie gasita:", state)
        return state
    if depth == 0:
        return None
    for option in generate_options(state):
        if is_valid(option, state):
            new_state = state + [option]
            result = dls(new_state, depth - 1, is_complete, generate_options, is_valid)
            if result is not None:
                return result
    return None


def iddfs(initial_state, is_complete, generate_options, is_valid, max_depth):
    for depth in range(max_depth + 1):
        result = dls(initial_state, depth, is_complete, generate_options, is_valid)
        if result is not None:
            return result
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
    max_depth = n

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)
                
    return iddfs(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        max_depth
    )