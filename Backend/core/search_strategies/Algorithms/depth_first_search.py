# depth_first_search.py
from __future__ import annotations

import time
from typing import Callable, List, Optional

from Backend.services import Logger

log = Logger("Algo:DFS")


def dfs(
    stack: List[List[int]],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
) -> Optional[List[int]]:
    pops = 0
    pushes = len(stack)

    while stack:
        state = stack.pop()
        pops += 1

        if is_complete(state):
            log.ok(
                "DFS solution found",
                ctx={"pops": pops, "pushes": pushes, "len": len(state)},
            )
            return state

        for option in generate_options(state):
            if is_valid(option, state):
                new_state = state + [option]
                stack.append(new_state)
                pushes += 1

    log.warn("DFS finished without solution", ctx={"pops": pops, "pushes": pushes})
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


def solve_nqueens(board):
    n = len(board)

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    log.info("solve_nqueens start", ctx={"n": n, "preset_queens": len(initial_state)})

    start = time.perf_counter()
    sol = dfs(
        [initial_state],
        lambda s: is_complete_nqueens(s, n),
        lambda s: generate_options_nqueens(s, n),
        is_valid_nqueens,
    )
    dt_ms = (time.perf_counter() - start) * 1000

    if sol is not None:
        log.ok("solve_nqueens solved", ctx={"n": n, "time_ms": round(dt_ms, 3), "len": len(sol)})
    else:
        log.warn("solve_nqueens no solution", ctx={"n": n, "time_ms": round(dt_ms, 3)})

    return sol
