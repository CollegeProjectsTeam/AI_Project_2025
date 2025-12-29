from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from Backend.services import Logger

log = Logger("Algo:BidirectionalSearch")


@dataclass(frozen=True)
class _StateInfo:
    state: List[int]
    cols: int
    d1: int
    d2: int


def _diag1_index(row: int, col: int, n: int) -> int:
    return (row - col) + (n - 1)


def _diag2_index(row: int, col: int) -> int:
    return row + col


def _expand_prefix(start_state: List[int], target_len: int, n: int, max_states: int) -> List[_StateInfo]:
    cols = 0
    d1 = 0
    d2 = 0

    for r, c in enumerate(start_state):
        if c < 0 or c >= n:
            return []
        cb = 1 << c
        d1b = 1 << _diag1_index(r, c, n)
        d2b = 1 << _diag2_index(r, c)
        if (cols & cb) or (d1 & d1b) or (d2 & d2b):
            return []
        cols |= cb
        d1 |= d1b
        d2 |= d2b

    out: List[_StateInfo] = []
    stack: List[tuple[List[int], int, int, int]] = [(list(start_state), cols, d1, d2)]

    while stack:
        state, cols_m, d1_m, d2_m = stack.pop()
        if len(out) >= max_states:
            break

        r = len(state)
        if r == target_len:
            out.append(_StateInfo(state, cols_m, d1_m, d2_m))
            continue

        for c in range(n):
            cb = 1 << c
            d1b = 1 << _diag1_index(r, c, n)
            d2b = 1 << _diag2_index(r, c)
            if (cols_m & cb) or (d1_m & d1b) or (d2_m & d2b):
                continue
            stack.append((state + [c], cols_m | cb, d1_m | d1b, d2_m | d2b))

    return out


def _expand_suffix(target_len: int, n: int, split_row: int, max_states: int) -> List[_StateInfo]:
    out: List[_StateInfo] = []
    stack: List[tuple[List[int], int, int, int]] = [([], 0, 0, 0)]

    while stack:
        state, cols_m, d1_m, d2_m = stack.pop()
        if len(out) >= max_states:
            break

        if len(state) == target_len:
            out.append(_StateInfo(state, cols_m, d1_m, d2_m))
            continue

        row = (n - 1) - len(state)
        if row < split_row:
            continue

        for c in range(n):
            cb = 1 << c
            d1b = 1 << _diag1_index(row, c, n)
            d2b = 1 << _diag2_index(row, c)
            if (cols_m & cb) or (d1_m & d1b) or (d2_m & d2b):
                continue
            stack.append((state + [c], cols_m | cb, d1_m | d1b, d2_m | d2b))

    return out


def solve_nqueens(board, max_states_per_side: int = 200_000) -> Optional[List[int]]:
    n = len(board)

    initial_state: List[int] = []
    for row in range(n):
        found = None
        for col in range(n):
            if board[row][col] == 1:
                found = col
                break
        if found is None:
            break
        initial_state.append(found)

    log.info(
        "solve_nqueens start",
        ctx={
            "n": n,
            "preset_queens": len(initial_state),
            "max_states_per_side": max_states_per_side,
        },
    )

    start = time.perf_counter()

    split = max(len(initial_state), n // 2)
    suffix_len = n - split

    prefix_states = _expand_prefix(initial_state, split, n, max_states_per_side)
    if not prefix_states:
        dt_ms = (time.perf_counter() - start) * 1000
        log.warn("solve_nqueens no solution (invalid preset or no prefix states)", ctx={"n": n, "time_ms": round(dt_ms, 3)})
        return None

    if len(prefix_states) >= max_states_per_side:
        log.warn("Prefix expansion hit max_states_per_side", ctx={"n": n, "prefix_states": len(prefix_states), "limit": max_states_per_side})

    suffix_states = _expand_suffix(suffix_len, n, split, max_states_per_side)

    if not suffix_states:
        dt_ms = (time.perf_counter() - start) * 1000
        log.warn("solve_nqueens no solution (no suffix states)", ctx={"n": n, "time_ms": round(dt_ms, 3)})
        return None

    if len(suffix_states) >= max_states_per_side:
        log.warn("Suffix expansion hit max_states_per_side", ctx={"n": n, "suffix_states": len(suffix_states), "limit": max_states_per_side})

    checks = 0
    for p in prefix_states:
        for s in suffix_states:
            checks += 1
            if (p.cols & s.cols) or (p.d1 & s.d1) or (p.d2 & s.d2):
                continue
            sol = p.state + list(reversed(s.state))
            dt_ms = (time.perf_counter() - start) * 1000
            log.ok(
                "solve_nqueens solved",
                ctx={
                    "n": n,
                    "time_ms": round(dt_ms, 3),
                    "len": len(sol),
                    "split": split,
                    "prefix_states": len(prefix_states),
                    "suffix_states": len(suffix_states),
                    "pair_checks": checks,
                },
            )
            return sol

    dt_ms = (time.perf_counter() - start) * 1000
    log.warn(
        "solve_nqueens no solution",
        ctx={
            "n": n,
            "time_ms": round(dt_ms, 3),
            "split": split,
            "prefix_states": len(prefix_states),
            "suffix_states": len(suffix_states),
            "pair_checks": checks,
        },
    )
    return None