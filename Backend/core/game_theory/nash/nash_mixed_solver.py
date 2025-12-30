from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional

from Backend.services.logging_service import Logger

log = Logger("NashMixedSolver")


class NashMixedSolver:
    @staticmethod
    def _solve_square(A: List[List[float]], b: List[float], tol: float = 1e-12) -> Optional[List[float]]:
        n = len(A)
        if n == 0 or any(len(row) != n for row in A) or len(b) != n:
            return None

        M = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]

        for col in range(n):
            pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
            if abs(M[pivot][col]) < tol:
                return None
            if pivot != col:
                M[col], M[pivot] = M[pivot], M[col]

            div = M[col][col]
            for j in range(col, n + 1):
                M[col][j] /= div

            for r in range(n):
                if r == col:
                    continue
                factor = M[r][col]
                if abs(factor) < tol:
                    continue
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]

        return [M[i][n] for i in range(n)]

    @staticmethod
    def _expected_u1(payoffs: List[List[List[Any]]], q: List[float]) -> List[float]:
        m = len(payoffs)
        n = len(payoffs[0]) if m else 0
        out: List[float] = []
        for i in range(m):
            s = 0.0
            for j in range(n):
                s += q[j] * float(payoffs[i][j][0])
            out.append(s)
        return out

    @staticmethod
    def _expected_u2(payoffs: List[List[List[Any]]], p: List[float]) -> List[float]:
        m = len(payoffs)
        n = len(payoffs[0]) if m else 0
        out: List[float] = []
        for j in range(n):
            s = 0.0
            for i in range(m):
                s += p[i] * float(payoffs[i][j][1])
            out.append(s)
        return out

    @staticmethod
    def solve(payoffs: List[List[List[Any]]], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
        m = len(payoffs)
        n = len(payoffs[0]) if m else 0
        if m == 0 or n == 0:
            return None

        strategies1 = list(range(m))
        strategies2 = list(range(n))
        kmax = min(m, n)

        for k in range(1, kmax + 1):
            for S1 in itertools.combinations(strategies1, k):
                for S2 in itertools.combinations(strategies2, k):
                    i0 = S1[0]
                    j0 = S2[0]

                    A_q = [[1.0] * k]
                    b_q = [1.0]
                    for ii in S1[1:]:
                        A_q.append([float(payoffs[ii][jj][0]) - float(payoffs[i0][jj][0]) for jj in S2])
                        b_q.append(0.0)

                    q_s = NashMixedSolver._solve_square(A_q, b_q)
                    if q_s is None:
                        continue
                    if any(x < -tol for x in q_s):
                        continue
                    q_s = [0.0 if x < 0.0 else float(x) for x in q_s]
                    sq = sum(q_s)
                    if sq <= tol:
                        continue
                    q_s = [x / sq for x in q_s]

                    A_p = [[1.0] * k]
                    b_p = [1.0]
                    for jj in S2[1:]:
                        A_p.append([float(payoffs[ii][jj][1]) - float(payoffs[ii][j0][1]) for ii in S1])
                        b_p.append(0.0)

                    p_s = NashMixedSolver._solve_square(A_p, b_p)
                    if p_s is None:
                        continue
                    if any(x < -tol for x in p_s):
                        continue
                    p_s = [0.0 if x < 0.0 else float(x) for x in p_s]
                    sp = sum(p_s)
                    if sp <= tol:
                        continue
                    p_s = [x / sp for x in p_s]

                    p = [0.0] * m
                    q = [0.0] * n
                    for idx, ii in enumerate(S1):
                        p[ii] = p_s[idx]
                    for idx, jj in enumerate(S2):
                        q[jj] = q_s[idx]

                    eu1 = NashMixedSolver._expected_u1(payoffs, q)
                    eu2 = NashMixedSolver._expected_u2(payoffs, p)

                    v1 = max(eu1[ii] for ii in S1)
                    v2 = max(eu2[jj] for jj in S2)

                    ok = True

                    for ii in S1:
                        if abs(eu1[ii] - v1) > 1e-5:
                            ok = False
                            break

                    if ok:
                        for ii in range(m):
                            if ii in S1:
                                continue
                            if eu1[ii] > v1 + 1e-6:
                                ok = False
                                break

                    if ok:
                        for jj in S2:
                            if abs(eu2[jj] - v2) > 1e-5:
                                ok = False
                                break

                    if ok:
                        for jj in range(n):
                            if jj in S2:
                                continue
                            if eu2[jj] > v2 + 1e-6:
                                ok = False
                                break

                    if not ok:
                        continue

                    return {
                        "type": f"{m}x{n}",
                        "p": p,
                        "q": q,
                        "support_p1": list(S1),
                        "support_p2": list(S2),
                    }

        return None

    @staticmethod
    def has_mixed(payoffs: List[List[List[Any]]]) -> bool:
        return NashMixedSolver.solve(payoffs) is not None
