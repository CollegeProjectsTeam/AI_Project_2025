from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Tuple

from Backend.core.search_strategies.search_problem import SearchProblem, State

Pegs = Tuple[Tuple[int, ...], ...]

@dataclass(frozen=True)
class GeneralizedHanoiProblem(SearchProblem):
    name: str
    disks: int
    pegs: int

    def initial_state(self) -> State:
        start_peg = tuple(range(self.disks, 0, -1))
        rest = tuple(() for _ in range(self.pegs - 1))
        return (start_peg,) + rest

    def is_goal(self, state: State) -> bool:
        s: Pegs = state
        return len(s[-1]) == self.disks

    def key(self, state: State) -> Hashable:
        return state

    def heuristic(self, state: State) -> float:
        s: Pegs = state
        return float(self.disks - len(s[-1]))

    def neighbors(self, state: State) -> Iterable[Tuple[State, int]]:
        s: Pegs = state
        out: list[Tuple[State, int]] = []

        tops = []
        for i, peg in enumerate(s):
            tops.append(peg[-1] if peg else None)

        for i in range(self.pegs):
            if tops[i] is None:
                continue
            disk = tops[i]
            for j in range(self.pegs):
                if i == j:
                    continue
                top_j = tops[j]
                if top_j is None or top_j > disk:
                    out.append((_move(s, i, j), 1))

        return out


def _move(state: Pegs, src: int, dst: int) -> Pegs:
    pegs = [list(p) for p in state]
    disk = pegs[src].pop()
    pegs[dst].append(disk)
    return tuple(tuple(p) for p in pegs)


def build_generalized_hanoi_problem(instance: dict) -> GeneralizedHanoiProblem:
    disks = int(instance.get("disks") or instance.get("n_disks") or 0)
    pegs = int(instance.get("pegs") or instance.get("k") or 3)
    return GeneralizedHanoiProblem(name="Generalized Hanoi", disks=disks, pegs=pegs)