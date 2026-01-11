from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Tuple

from Backend.core.search_strategies.search_problem import SearchProblem, State


Pos = Tuple[int, int]

@dataclass(frozen=True)
class KnightsTourProblem(SearchProblem):
    name: str
    n: int
    start: Pos

    def initial_state(self) -> State:
        return (self.start,)

    def is_goal(self, state: State) -> bool:
        path: Tuple[Pos, ...] = state
        return len(path) == self.n * self.n

    def key(self, state: State) -> Hashable:
        return state

    def heuristic(self, state: State) -> float:
        path: Tuple[Pos, ...] = state
        return float((self.n * self.n) - len(path))

    def neighbors(self, state: State) -> Iterable[Tuple[State, int]]:
        path: Tuple[Pos, ...] = state
        last = path[-1]
        visited = set(path)

        moves = []
        for dr, dc in _KNIGHT_DELTAS:
            nr, nc = last[0] + dr, last[1] + dc
            if 0 <= nr < self.n and 0 <= nc < self.n and (nr, nc) not in visited:
                moves.append((nr, nc))

        moves.sort(key=lambda p: _onward_degree(p, visited, self.n))

        return [ (path + (p,), 1) for p in moves ]


_KNIGHT_DELTAS = [
    (-2, -1), (-2,  1),
    (-1, -2), (-1,  2),
    ( 1, -2), ( 1,  2),
    ( 2, -1), ( 2,  1),
]


def _onward_degree(pos: Pos, visited: set[Pos], n: int) -> int:
    cnt = 0
    for dr, dc in _KNIGHT_DELTAS:
        nr, nc = pos[0] + dr, pos[1] + dc
        if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited:
            cnt += 1
    return cnt


def build_knights_tour_problem(instance: dict) -> KnightsTourProblem:
    n = int(instance.get("board_size") or instance.get("n") or 0)
    start = instance.get("start") or [0, 0]
    sr, sc = int(start[0]), int(start[1])
    return KnightsTourProblem(name="Knight's Tour", n=n, start=(sr, sc))