# simulated_annealing.py
from __future__ import annotations

import random
import math
import time
from typing import Callable, List, Optional

from Backend.services import Logger

log = Logger("Algo:SimulatedAnnealing")


def simulated_annealing(
    initial_state: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
    heuristic: Callable[[List[int]], int],
    initial_temp: float,
    cooling_rate: float,
) -> Optional[List[int]]:
    current = initial_state
    temp = float(initial_temp)
    steps = 0

    while temp > 0:
        steps += 1

        if is_complete(current):
            log.ok(
                "SimulatedAnnealing solution found",
                ctx={"steps": steps, "temp": round(temp, 6), "h": heuristic(current), "len": len(current)},
            )
            return current

        neighbors = []
        for option in generate_options(current):
            if is_valid(option, current):
                neighbors.append(current + [option])

        if not neighbors:
            log.warn("SimulatedAnnealing stuck (no neighbors)", ctx={"steps": steps, "temp": round(temp, 6)})
            return None

        neighbor = random.choice(neighbors)
        delta = heuristic(neighbor) - heuristic(current)

        if delta < 0 or random.random() < math.exp(-delta / temp):
            current = neighbor

        temp *= cooling_rate

    log.warn(
        "SimulatedAnnealing finished (temperature cooled) without solution",
        ctx={"steps": steps, "initial_temp": initial_temp, "cooling_rate": cooling_rate},
    )
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
        for j in range(i + 1, n):
            if solution[i] == solution[j] or abs(i - j) == abs(solution[i] - solution[j]):
                conflicts += 1
    return conflicts


def solve_nqueens(board, initial_temp=1000, cooling_rate=0.95):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    log.info(
        "solve_nqueens start",
        ctx={
            "n": n,
            "preset_queens": len(initial_state),
            "initial_temp": initial_temp,
            "cooling_rate": cooling_rate,
        },
    )

    start = time.perf_counter()
    sol = simulated_annealing(
        initial_state,
        lambda s: is_complete_nqueens(s, n),
        lambda s: generate_options_nqueens(s, n),
        is_valid_nqueens,
        heuristic_nqueens,
        initial_temp,
        cooling_rate,
    )
    dt_ms = (time.perf_counter() - start) * 1000

    if sol is not None:
        log.ok("solve_nqueens solved", ctx={"n": n, "time_ms": round(dt_ms, 3), "len": len(sol)})
    else:
        log.warn("solve_nqueens no solution", ctx={"n": n, "time_ms": round(dt_ms, 3)})

    return sol
