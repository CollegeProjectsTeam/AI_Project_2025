# greedy_best_first_search.py
from __future__ import annotations

import heapq
import time
from typing import Callable, List, Optional, Tuple

from Backend.services import Logger

log = Logger("Algo:GreedyBestFirst")


def greedy_best_first_search(
    initial_state: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
    heuristic: Callable[[List[int]], int],
) -> Optional[List[int]]:
    queue: List[Tuple[int, List[int]]] = [(heuristic(initial_state), initial_state)]
    visited = set()
    pops = 0
    pushes = 1

    while queue:
        h, state = heapq.heappop(queue)
        pops += 1

        t = tuple(state)
        if t in visited:
            continue
        visited.add(t)

        if is_complete(state):
            log.ok(
                "Greedy solution found",
                ctx={"pops": pops, "pushes": pushes, "visited": len(visited), "h": h, "len": len(state)},
            )
            return state

        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                heapq.heappush(queue, (heuristic(new_state), new_state))
                pushes += 1

    log.warn(
        "Greedy finished without solution",
        ctx={"pops": pops, "pushes": pushes, "visited": len(visited)},
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


def solve_nqueens(board):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    log.info("solve_nqueens start", ctx={"n": n, "preset_queens": len(initial_state)})

    start = time.perf_counter()
    sol = greedy_best_first_search(
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
