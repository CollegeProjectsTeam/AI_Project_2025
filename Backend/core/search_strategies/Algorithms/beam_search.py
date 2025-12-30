# beam_search.py
from __future__ import annotations

import heapq
import random
import time
from typing import Callable, List, Optional, Tuple

from Backend.services import Logger

log = Logger("Algo:BeamSearch")


def beam_search_robust(
    initial_state: List[int],
    is_complete: Callable[[List[int]], bool],
    generate_options: Callable[[List[int]], List[int]],
    is_valid: Callable[[int, List[int]], bool],
    heuristic: Callable[[List[int]], int],
    beam_width: int,
    max_retries: int = 5,
) -> Optional[List[int]]:
    for attempt in range(1, max_retries + 1):
        queue: List[Tuple[int, List[int]]] = [(heuristic(initial_state), initial_state)]
        expansions = 0

        while queue:
            next_queue: List[Tuple[int, List[int]]] = []

            for h, state in queue:
                expansions += 1
                if is_complete(state):
                    log.ok(
                        "BeamSearch solution found",
                        ctx={
                            "attempt": attempt,
                            "expansions": expansions,
                            "beam_width": beam_width,
                            "h": h,
                            "len": len(state),
                        },
                    )
                    return state

                for option in generate_options(state):
                    if is_valid(option, state):
                        new_state = state + [option]
                        heapq.heappush(next_queue, (heuristic(new_state), new_state))

            if not next_queue:
                break

            k = min(beam_width, len(next_queue))
            queue = [heapq.heappop(next_queue) for _ in range(k)]

        random.shuffle(initial_state)

    log.warn(
        "BeamSearch finished without solution",
        ctx={"beam_width": beam_width, "max_retries": max_retries},
    )
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

    log.info(
        "solve_nqueens start",
        ctx={"n": n, "preset_queens": len(initial_state), "beam_width": beam_width},
    )

    start = time.perf_counter()
    sol = beam_search_robust(
        initial_state,
        lambda s: is_complete_nqueens(s, n),
        lambda s: generate_options_nqueens(s, n),
        is_valid_nqueens,
        heuristic_nqueens_full,
        beam_width,
        max_retries=10,
    )
    dt_ms = (time.perf_counter() - start) * 1000

    if sol is not None:
        log.ok("solve_nqueens solved", ctx={"n": n, "time_ms": round(dt_ms, 3), "len": len(sol)})
    else:
        log.warn("solve_nqueens no solution", ctx={"n": n, "time_ms": round(dt_ms, 3)})

    return sol
