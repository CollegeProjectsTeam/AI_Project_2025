from __future__ import annotations

import heapq
import math
import random
from collections import deque
from typing import Dict, Hashable, Iterable, List, Optional, Tuple

from Backend.core.search_strategies.search_problem import SearchBudget, SearchProblem, State


def bfs(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    q = deque([problem.initial_state()])
    seen = {problem.key(q[0])}

    while q:
        if budget.exceeded():
            return None
        budget.tick()

        s = q.popleft()
        if problem.is_goal(s):
            return s

        for ns, _cost in problem.neighbors(s):
            k = problem.key(ns)
            if k in seen:
                continue
            seen.add(k)
            q.append(ns)

    return None


def dfs(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    stack = [problem.initial_state()]
    seen = set()

    while stack:
        if budget.exceeded():
            return None
        budget.tick()

        s = stack.pop()
        k = problem.key(s)
        if k in seen:
            continue
        seen.add(k)

        if problem.is_goal(s):
            return s

        # LIFO: push neighbors
        for ns, _ in problem.neighbors(s):
            stack.append(ns)

    return None


def ucs(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    start = problem.initial_state()
    pq: List[Tuple[int, State]] = [(0, start)]
    best: Dict[Hashable, int] = {problem.key(start): 0}

    while pq:
        if budget.exceeded():
            return None
        budget.tick()

        g, s = heapq.heappop(pq)
        k = problem.key(s)
        if g != best.get(k, 10**18):
            continue

        if problem.is_goal(s):
            return s

        for ns, step in problem.neighbors(s):
            ng = g + int(step)
            nk = problem.key(ns)
            if ng < best.get(nk, 10**18):
                best[nk] = ng
                heapq.heappush(pq, (ng, ns))

    return None


def greedy_best_first(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    start = problem.initial_state()
    pq: List[Tuple[float, State]] = [(problem.heuristic(start), start)]
    seen = set()

    while pq:
        if budget.exceeded():
            return None
        budget.tick()

        h, s = heapq.heappop(pq)
        k = problem.key(s)
        if k in seen:
            continue
        seen.add(k)

        if problem.is_goal(s):
            return s

        for ns, _ in problem.neighbors(s):
            heapq.heappush(pq, (problem.heuristic(ns), ns))

    return None


def a_star(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    start = problem.initial_state()
    pq: List[Tuple[float, int, State]] = [(problem.heuristic(start), 0, start)]
    best: Dict[Hashable, int] = {problem.key(start): 0}

    while pq:
        if budget.exceeded():
            return None
        budget.tick()

        f, g, s = heapq.heappop(pq)
        k = problem.key(s)
        if g != best.get(k, 10**18):
            continue

        if problem.is_goal(s):
            return s

        for ns, step in problem.neighbors(s):
            ng = g + int(step)
            nk = problem.key(ns)
            if ng < best.get(nk, 10**18):
                best[nk] = ng
                heapq.heappush(pq, (ng + problem.heuristic(ns), ng, ns))

    return None


def iddfs(problem: SearchProblem, budget: SearchBudget, max_depth: int) -> Optional[State]:
    start = problem.initial_state()

    def dls(s: State, depth: int, path_seen: set[Hashable]) -> Optional[State]:
        if budget.exceeded():
            return None
        budget.tick()

        if problem.is_goal(s):
            return s
        if depth == 0:
            return None

        k = problem.key(s)
        path_seen.add(k)

        for ns, _ in problem.neighbors(s):
            nk = problem.key(ns)
            if nk in path_seen:
                continue
            res = dls(ns, depth - 1, path_seen)
            if res is not None:
                return res

        path_seen.remove(k)
        return None

    for d in range(max_depth + 1):
        if budget.exceeded():
            return None
        res = dls(start, d, set())
        if res is not None:
            return res

    return None


def backtracking(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    start = problem.initial_state()

    def rec(s: State, path_seen: set[Hashable]) -> Optional[State]:
        if budget.exceeded():
            return None
        budget.tick()

        if problem.is_goal(s):
            return s

        k = problem.key(s)
        path_seen.add(k)

        for ns, _ in problem.neighbors(s):
            nk = problem.key(ns)
            if nk in path_seen:
                continue
            res = rec(ns, path_seen)
            if res is not None:
                return res

        path_seen.remove(k)
        return None

    return rec(start, set())


def beam_search(problem: SearchProblem, budget: SearchBudget, beam_width: int = 20) -> Optional[State]:
    frontier = [problem.initial_state()]

    while frontier:
        if budget.exceeded():
            return None

        next_level: List[State] = []
        for s in frontier:
            if budget.exceeded():
                return None
            budget.tick()

            if problem.is_goal(s):
                return s

            for ns, _ in problem.neighbors(s):
                next_level.append(ns)

        if not next_level:
            return None

        next_level.sort(key=problem.heuristic)
        frontier = next_level[: max(1, int(beam_width))]

    return None


def hill_climbing(problem: SearchProblem, budget: SearchBudget) -> Optional[State]:
    cur = problem.initial_state()
    cur_h = problem.heuristic(cur)

    while True:
        if budget.exceeded():
            return None
        budget.tick()

        if problem.is_goal(cur):
            return cur

        neigh = [ns for ns, _ in problem.neighbors(cur)]
        if not neigh:
            return None

        best = min(neigh, key=problem.heuristic)
        best_h = problem.heuristic(best)

        if best_h >= cur_h:
            return None

        cur, cur_h = best, best_h


def simulated_annealing(problem: SearchProblem, budget: SearchBudget, initial_temp: float = 1000.0, cooling: float = 0.995) -> Optional[State]:
    cur = problem.initial_state()
    temp = float(initial_temp)

    while temp > 1e-9:
        if budget.exceeded():
            return None
        budget.tick()

        if problem.is_goal(cur):
            return cur

        neigh = [ns for ns, _ in problem.neighbors(cur)]
        if not neigh:
            return None

        nxt = random.choice(neigh)

        delta = problem.heuristic(nxt) - problem.heuristic(cur)
        if delta < 0 or random.random() < math.exp(-delta / temp):
            cur = nxt

        temp *= float(cooling)

    return None