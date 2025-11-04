import heapq

def beam_search(initial_state, is_complete, generate_options, is_valid, heuristic, beam_width):
    queue = [(heuristic(initial_state), initial_state)]
    while queue:
        next_queue = []
        for h, state in queue:
            if is_complete(state):
                #print("Solutie gasita:", state)
                return state
            for option in generate_options(state):
                if is_valid(option, state):
                    new_state = state + [option]
                    heapq.heappush(next_queue, (heuristic(new_state), new_state))
        queue = [heapq.heappop(next_queue) for _ in range(min(beam_width, len(next_queue)))]
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


def heuristic_nqueens(solution):
    conflicts = 0
    row = len(solution) - 1
    for r, c in enumerate(solution[:-1]):
        if solution[-1] == c or abs(solution[-1] - c) == abs(row - r):
            conflicts += 1
    return conflicts


def solve_nqueens(board):
    n = len(board)
    beam_width = max(1, n // 2)  

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    #print(f"Stare initiala: {initial_state}")

    return beam_search(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        heuristic_nqueens,
        beam_width
    )