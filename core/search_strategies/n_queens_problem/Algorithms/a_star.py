import heapq

def a_star(initial_state, is_complete, generate_options, is_valid, g_cost, h_cost):
    queue = [(h_cost(initial_state), 0, initial_state)]
    visited = set()
    while queue:
        f, g, state = heapq.heappop(queue)
        t = tuple(state)
        if t in visited:
            continue
        visited.add(t)
        if is_complete(state):
            #print("Solutie gasita:", state, "cu cost:", g)
            return state
        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                new_g = g + g_cost(option, state)
                heapq.heappush(queue, (new_g + h_cost(new_state), new_g, new_state))
    return None


def is_complete_nqueens(solution, n):
    return len(solution) == n


def generate_options_nqueens(solution, n):
    return list(range(n))


def is_valid_nqueens(col, solution):
    row = len(solution)
    for r, c in enumerate(solution):
        if c == col or abs(c - col) == abs(row - r):
            return False
    return True


def g_cost_nqueens(col, solution):
    return 1


def h_cost_nqueens(solution):
    conflicts = 0
    for r1 in range(len(solution)):
        for r2 in range(r1 + 1, len(solution)):
            if solution[r1] == solution[r2] or abs(solution[r1] - solution[r2]) == abs(r1 - r2):
                conflicts += 1
    return conflicts

def solve_nqueens(board):
    n = len(board)
    initial_state = []

    # extract the initial state from the board (queens' positions)
    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:  
                initial_state.append(col)

    # apelam A*s
    return a_star(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        g_cost_nqueens,
        h_cost_nqueens
    )

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:  # presupunem ca 1 = regina
                initial_state.append(col)

    print(f"Stare initiala: {initial_state}")

    # apelam A*
    return a_star(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        g_cost_nqueens,
        h_cost_nqueens
    )
