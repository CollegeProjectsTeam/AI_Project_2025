# iterative_deepening_depth_first_search.py
from __future__ import annotations

import time
from typing import Callable, List, Optional

from Backend.services import Logger

log = Logger("Algo:IDDFS")


def dls(
    state: List[int],
    depth: int,
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
) -> Optional[List[int]]:
    if is_complete(state):
        return state
    if depth == 0:
        return None

    for option in generate_options(state):
        if is_valid(option, state):
            new_state = state + [option]
            result = dls(new_state, depth - 1, is_complete, generate_options, is_valid)
            if result is not None:
                return result

    return None


def iddfs(
    initial_state: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
    max_depth: int,
) -> Optional[List[int]]:
    for depth in range(max_depth + 1):
        result = dls(initial_state, depth, is_complete, generate_options, is_valid)
        if result is not None:
            log.ok("IDDFS solution found", ctx={"depth": depth, "len": len(result)})
            return result

    log.warn("IDDFS finished without solution", ctx={"max_depth": max_depth})
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
    max_depth = n

    initial_state = []
    for row in range(n):
        for col in range(n):
            if board[row][col] == 1:
                initial_state.append(col)

    log.info(
        "solve_nqueens start",
        ctx={"n": n, "preset_queens": len(initial_state), "max_depth": max_depth},
    )

    start = time.perf_counter()
    sol = iddfs(
        initial_state,
        lambda s: is_complete_nqueens(s, n),
        lambda s: generate_options_nqueens(s, n),
        is_valid_nqueens,
        max_depth,
    )
    dt_ms = (time.perf_counter() - start) * 1000

    if sol is not None:
        log.ok("solve_nqueens solved", ctx={"n": n, "time_ms": round(dt_ms, 3), "len": len(sol)})
    else:
        log.warn("solve_nqueens no solution", ctx={"n": n, "time_ms": round(dt_ms, 3)})

    return sol
