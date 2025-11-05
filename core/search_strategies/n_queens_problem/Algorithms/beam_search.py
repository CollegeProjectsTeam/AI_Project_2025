import heapq
import random

def beam_search_robust(initial_state, is_complete, generate_options, is_valid, heuristic, beam_width, max_retries=5):
    n = len(initial_state) + (0 if initial_state else 1)
    
    for attempt in range(max_retries):
        queue = [(heuristic(initial_state), initial_state)]
        while queue:
            next_queue = []
            for h, state in queue:
                if is_complete(state):
                    return state
                for option in generate_options(state):
                    if is_valid(option, state):
                        new_state = state + [option]
                        heapq.heappush(next_queue, (heuristic(new_state), new_state))
            if not next_queue:
                break
            queue = [heapq.heappop(next_queue) for _ in range(min(beam_width, len(next_queue)))]
        random.shuffle(initial_state)
    return None


def is_complete_nqueens(solution, n):
    return len(solution) == n


def generate_options_nqueens(solution, n):
    return list(range(n))


def is_valid_nqueens(col, solution):
    row = len(solution)
    for r, c in enumerate(solution):
        if c == col or abs(row - r) == abs(col - c):
            return False
    return True


def heuristic_nqueens_full(solution):
    conflicts = 0
    n = len(solution)
    for i in range(n):
        for j in range(i + 1, n):
            if solution[i] == solution[j] or abs(i - j) == abs(solution[i] - solution[j]):
                conflicts += 1
    return conflicts


def solve_nqueens(board):
    n = len(board)
    beam_width = max(4, n // 2)
    initial_state = []

    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    return beam_search_robust(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        heuristic_nqueens_full,
        beam_width,
        max_retries=10
    )