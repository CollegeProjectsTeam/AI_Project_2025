from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Protocol, Tuple


State = Any


class SearchProblem(Protocol):
    name: str

    def initial_state(self) -> State: ...
    def is_goal(self, state: State) -> bool: ...
    def neighbors(self, state: State) -> Iterable[Tuple[State, int]]: ...
    def key(self, state: State) -> Hashable: ...
    def heuristic(self, state: State) -> float: ...


@dataclass
class SearchBudget:
    max_time_s: float = 2.5
    max_expansions: int = 300_000
    started: float = field(default_factory=time.perf_counter)
    expansions: int = 0

    def tick(self, n: int = 1) -> None:
        self.expansions += n

    def time_s(self) -> float:
        return time.perf_counter() - self.started

    def exceeded(self) -> bool:
        if self.expansions >= self.max_expansions:
            return True
        if self.time_s() >= self.max_time_s:
            return True
        return False
