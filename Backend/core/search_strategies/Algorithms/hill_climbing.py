# hill_climbing.py
from __future__ import annotations

import time
from typing import Callable, List, Optional

from Backend.services import Logger

log = Logger("Algo:HillClimbing")


def hill_climbing(
    initial_state: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
    heuristic: Callable[[List[int]], int],
) -> Optional[List[int]]:
    current = initial_state
    steps = 0

    while True:
        steps += 1

        if is_complete(current):
            log.ok(
                "HillClimbing solution found",
                ctx={"steps": steps, "h": heuristic(current), "len": len(current)},
            )
            return current

        neighbors = []
        for option in generate_options(current):
            if is_valid(option, current):
                neighbors.append(current + [option])

        if not neighbors:
            log.warn("HillClimbing stuck (no neighbors)", ctx={"steps": steps, "len": len(current)})
            return None

        neighbor = min(neighbors, key=heuristic)

        if heuristic(neighbor) >= heuristic(current):
            log.warn(
                "HillClimbing stuck (no improvement)",
                ctx={"steps": steps, "h_current": heuristic(current), "h_best": heuristic(neighbor), "len": len(current)},
            )
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
    n = len(solution)
    for i in range(n):
        for j in range(i + 1, n):
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

    log.info("solve_nqueens start", ctx={"n": n, "preset_queens": len(initial_state)})

    start = time.perf_counter()
    sol = hill_climbing(
        initial_state,
        lambda s: is_complete_nqueens(s, n),
        lambda s: generate_options_nqueens(s, n),
        is_valid_nqueens,
        heuristic_nqueens,
    )
    dt_ms = (time.perf_counter() - start) * 1000

    if sol is not None:
        log.ok("solve_nqueens solved", ctx={"n": n, "time_ms": round(dt_ms, 3), "len": len(sol)})
    else:
        log.warn("solve_nqueens no solution", ctx={"n": n, "time_ms": round(dt_ms, 3)})

    return sol
