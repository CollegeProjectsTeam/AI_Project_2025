from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Tuple

from Backend.core.search_strategies.search_problem import SearchProblem, State


@dataclass(frozen=True)
class NQueensProblem(SearchProblem):
    name: str
    n: int
    preset: Tuple[int, ...]

    def initial_state(self) -> State:
        return self.preset

    def is_goal(self, state: State) -> bool:
        s: Tuple[int, ...] = state
        return len(s) == self.n

    def key(self, state: State) -> Hashable:
        return state

    def heuristic(self, state: State) -> float:
        s: Tuple[int, ...] = state
        return float(self.n - len(s))

    def neighbors(self, state: State) -> Iterable[Tuple[State, int]]:
        s: Tuple[int, ...] = state
        row = len(s)
        if row >= self.n:
            return []

        out: list[Tuple[State, int]] = []
        for col in range(self.n):
            if _is_valid(col, s):
                out.append((s + (col,), 1))
        return out


def _is_valid(col: int, partial: Tuple[int, ...]) -> bool:
    row = len(partial)
    for r, c in enumerate(partial):
        if c == col:
            return False
        if abs(c - col) == abs(r - row):
            return False
    return True


def build_nqueens_problem(board: list[list[int]]) -> NQueensProblem:
    n = len(board)
    preset: list[int] = []
    for row in range(n):
        found = None
        for col in range(n):
            if board[row][col] == 1:
                found = col
                break
        if found is None:
            break
        preset.append(found)

    return NQueensProblem(
        name="N-Queens",
        n=n,
        preset=tuple(preset),
    )