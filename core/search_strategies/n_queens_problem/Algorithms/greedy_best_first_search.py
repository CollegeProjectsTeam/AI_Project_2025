import heapq

def greedy_best_first_search(initial_state, is_complete, generate_options, is_valid, heuristic):
    queue = [(heuristic(initial_state), initial_state)]
    visited = set()
    while queue:
        h, state = heapq.heappop(queue)
        t = tuple(state)
        if t in visited:
            continue
        visited.add(t)
        if is_complete(state):
            #print("Solutie gasita:", state)
            return state
        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                heapq.heappush(queue, (heuristic(new_state), new_state))
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


def heuristic_nqueens(solution):
    conflicts = 0
    n = len(solution)
    for i in range(n):
        for j in range(i+1, n):
            if solution[i] == solution[j] or abs(i - j) == abs(solution[i] - solution[j]):
                conflicts += 1
    return conflicts


def solve_nqueens(board):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)
                
    return greedy_best_first_search(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        heuristic_nqueens
    )