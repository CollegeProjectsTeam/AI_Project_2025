# backtracking.py
from __future__ import annotations

import time
from typing import Callable, List, Optional

from Backend.services import Logger

log = Logger("Algo:Backtracking")


def backtrack(
    solution: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
) -> Optional[List[int]]:
    if is_complete(solution):
        return solution

    for option in generate_options(solution):
        if is_valid(option, solution):
            solution.append(option)
            result = backtrack(solution, is_complete, generate_options, is_valid)
            if result:
                return solution
            solution.pop()

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

    log.info(
        "solve_nqueens start",
        ctx={"n": n, "preset_queens": len(initial_state)},
    )

    start = time.perf_counter()
    sol = backtrack(
        initial_state,
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


def print_board(solution):
    if not solution:
        log.warn("print_board called with empty solution")
        print("No solution found.")
        return

    n = len(solution)
    for r in range(n):
        line = ""
        for c in range(n):
            line += "1 " if solution[r] == c else "0 "
        print(line)
    print()
