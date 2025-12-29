# a_star.py
from __future__ import annotations

import heapq
import time
from typing import Any, Callable, List, Optional

from Backend.services import Logger

log = Logger("Algo:AStar")


def a_star(
    initial_state: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
    g_cost: Callable[[int, List[int]], int],
    h_cost: Callable[[List[int]], int],
) -> Optional[List[int]]:
    queue = [(h_cost(initial_state), 0, initial_state)]
    visited = set()
    pops = 0
    pushes = 1

    while queue:
        f, g, state = heapq.heappop(queue)
        pops += 1

        t = tuple(state)
        if t in visited:
            continue
        visited.add(t)

        if is_complete(state):
            log.ok(
                "A* solution found",
                ctx={
                    "pops": pops,
                    "pushes": pushes,
                    "visited": len(visited),
                    "g": g,
                    "f": f,
                    "len": len(state),
                },
            )
            return state

        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                new_g = g + g_cost(option, state)
                heapq.heappush(queue, (new_g + h_cost(new_state), new_g, new_state))
                pushes += 1

    log.warn(
        "A* finished without solution",
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
        if c == col or abs(c - col) == abs(row - r):
            return False
    return True


def g_cost_nqueens(col, solution):
    return 1


def h_cost_nqueens(solution):
    conflicts = 0
    for r1 in range(len(solution)):
        for r2 in range(r1 + 1, len(solution)):
            if solution[r1] == solution[r2] or abs(solution[r1] - solution[r2]) == abs(
                r1 - r2
            ):
                conflicts += 1
    return conflicts


def solve_nqueens(board):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    log.info(
        "solve_nqueens start",
        ctx={"n": n, "preset_queens": len(initial_state)},
    )

    start = time.perf_counter()
    sol = a_star(
        initial_state,
        lambda s: is_complete_nqueens(s, n),
        lambda s: generate_options_nqueens(s, n),
        is_valid_nqueens,
        g_cost_nqueens,
        h_cost_nqueens,
    )
    dt_ms = (time.perf_counter() - start) * 1000

    if sol is not None:
        log.ok("solve_nqueens solved", ctx={"n": n, "time_ms": round(dt_ms, 3), "len": len(sol)})
    else:
        log.warn("solve_nqueens no solution", ctx={"n": n, "time_ms": round(dt_ms, 3)})

    return sol