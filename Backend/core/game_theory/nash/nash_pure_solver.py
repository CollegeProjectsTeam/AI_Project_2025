from __future__ import annotations

from typing import List, Tuple, Any

from Backend.services.logging_service import Logger

log = Logger("NashPureSolver")


class NashPureSolver:
    @staticmethod
    def find_nash_pure(payoffs: List[List[List[Any]]]) -> List[Tuple[int, int]]:
        m = len(payoffs)
        n = len(payoffs[0]) if m else 0
        if m == 0 or n == 0:
            return []

        solutions: List[Tuple[int, int]] = []

        for i in range(m):
            for j in range(n):
                p1_ij, p2_ij = payoffs[i][j]

                best_for_p1 = True
                for ii in range(m):
                    if payoffs[ii][j][0] > p1_ij:
                        best_for_p1 = False
                        break
                if not best_for_p1:
                    continue

                best_for_p2 = True
                for jj in range(n):
                    if payoffs[i][jj][1] > p2_ij:
                        best_for_p2 = False
                        break
                if not best_for_p2:
                    continue

                solutions.append((i, j))

        return solutions
