from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Tuple

from Backend.core.search_strategies.search_problem import SearchProblem, State


@dataclass(frozen=True)
class GraphColoringProblem(SearchProblem):
    name: str
    num_nodes: int
    num_colors: int
    edges: Tuple[Tuple[int, int], ...]

    def initial_state(self) -> State:
        return ()

    def is_goal(self, state: State) -> bool:
        s: Tuple[int, ...] = state
        return len(s) == self.num_nodes

    def key(self, state: State) -> Hashable:
        return state

    def heuristic(self, state: State) -> float:
        s: Tuple[int, ...] = state
        return float(self.num_nodes - len(s))

    def neighbors(self, state: State) -> Iterable[Tuple[State, int]]:
        s: Tuple[int, ...] = state
        i = len(s)
        if i >= self.num_nodes:
            return []

        out: list[Tuple[State, int]] = []
        for color in range(self.num_colors):
            if _valid_color(i, color, s, self.edges):
                out.append((s + (color,), 1))
        return out


def _valid_color(node: int, color: int, partial: Tuple[int, ...], edges: Tuple[Tuple[int, int], ...]) -> bool:
    for a, b in edges:
        if a == node and b < len(partial):
            if partial[b] == color:
                return False
        elif b == node and a < len(partial):
            if partial[a] == color:
                return False
    return True


def build_graph_coloring_problem(instance: dict) -> GraphColoringProblem:
    n = int(instance.get("num_nodes") or instance.get("nodes") or 0)
    k = int(instance.get("num_colors") or instance.get("colors") or 0)

    edges_raw = instance.get("edges") or instance.get("edge_list")
    if edges_raw is None:
        adj = instance.get("adj_list")
        if isinstance(adj, list):
            edges_tmp: list[tuple[int, int]] = []
            for u, neigh in enumerate(adj):
                if not isinstance(neigh, list):
                    continue
                for v in neigh:
                    try:
                        v = int(v)
                    except Exception:
                        continue
                    if 0 <= u < n and 0 <= v < n and u != v:
                        a, b = (u, v) if u < v else (v, u)
                        edges_tmp.append((a, b))
            edges_raw = edges_tmp
        else:
            edges_raw = []

    edges: list[tuple[int, int]] = []
    for e in edges_raw:
        if isinstance(e, (list, tuple)) and len(e) == 2:
            edges.append((int(e[0]), int(e[1])))

    edges = sorted(set(edges))

    return GraphColoringProblem(
        name="Graph Coloring",
        num_nodes=n,
        num_colors=k,
        edges=tuple(edges),
    )