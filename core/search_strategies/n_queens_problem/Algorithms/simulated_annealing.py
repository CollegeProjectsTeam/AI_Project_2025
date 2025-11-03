import random
import math

def simulated_annealing(initial_state, is_complete, generate_options, is_valid, heuristic, initial_temp, cooling_rate):
    current = initial_state
    temp = initial_temp
    while temp > 0:
        if is_complete(current):
            print("Solutie gasita:", current)
            return current
        neighbors = []
        for option in generate_options(current):
            if is_valid(option, current):
                neighbors.append(current + [option])
        if not neighbors:
            return None
        neighbor = random.choice(neighbors)
        delta = heuristic(neighbor) - heuristic(current)
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current = neighbor
        temp *= cooling_rate
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
    row = len(solution) - 1
    for r, c in enumerate(solution[:-1]):
        if solution[-1] == c or abs(solution[-1] - c) == abs(row - r):
            conflicts += 1
    return conflicts


def solve_nqueens(board, initial_temp=1000, cooling_rate=0.95):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    return simulated_annealing(
        initial_state,
        lambda sol: is_complete_nqueens(sol, n),
        lambda sol: generate_options_nqueens(sol, n),
        is_valid_nqueens,
        heuristic_nqueens,
        initial_temp,
        cooling_rate
    )