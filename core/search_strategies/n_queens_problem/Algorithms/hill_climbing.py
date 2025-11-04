def hill_climbing(initial_state, is_complete, generate_options, is_valid, heuristic):
    current = initial_state
    while True:
        if is_complete(current):
            #print("Solutie gasita:", current)
            return current
        neighbors = []
        for option in generate_options(current):
            if is_valid(option, current):
                neighbors.append(current + [option])
        if not neighbors:
            return None
        neighbor = min(neighbors, key=heuristic)
        if heuristic(neighbor) >= heuristic(current):
            return None
        current = neighbor


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


def heuristic_nqueens(solution):
    conflicts = 0
    row = len(solution) - 1
    for r, c in enumerate(solution[:-1]):
        if solution[-1] == c or abs(solution[-1] - c) == abs(row - r):
            conflicts += 1
    return conflicts


def solve_nqueens(board):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    return hill_climbing(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        heuristic_nqueens
    )