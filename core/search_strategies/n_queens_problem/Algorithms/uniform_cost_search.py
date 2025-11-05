import heapq

def uniform_cost_search(initial_state, is_complete, generate_options, is_valid, cost_function):
    queue = [(0, initial_state)]
    while queue:
        cost, state = heapq.heappop(queue)
        if is_complete(state):
            #print("Solutie gasita:", state, "cu cost:", cost)
            return state
        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                new_cost = cost + cost_function(option, state)
                heapq.heappush(queue, (new_cost, new_state))
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


def cost_function_nqueens(col, solution):
    return 1


def solve_nqueens(board):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    return uniform_cost_search(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        cost_function_nqueens
    )