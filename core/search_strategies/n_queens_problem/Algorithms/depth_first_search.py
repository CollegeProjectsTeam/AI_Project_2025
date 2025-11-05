def dfs(stack, is_complete, generate_options, is_valid):
    while stack:
        state = stack.pop()
        if is_complete(state):
            #print("Solutie gasita:", state)
            return state
        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                stack.append(new_state)
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

    return dfs(
        [initial_state],
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens
    )